#!/bin/python3

import os, sys
import shutil
import subprocess
from pathlib import Path
from passwords import Passwords
from recaptchav3 import reCAPTCHAv3
from sitebuilder import SiteBuilder
from config import Config
import urllib.request

class Lesley(SiteBuilder):
    # Install PHP-Imagick
    def install(self, aws: bool) -> None:
        os.system(self.pmu + " install php-imagick -y")
        if not aws:
            os.system(self.pmu + " install libmagickcore-6* -y")
        os.system("systemctl restart php-fpm")

def main(development: bool, test: bool = False):
    print("### Initiating \"Lesley Paige Art\" site installation ###")
    project_name = "lesley"
    if development:
        url = None
        domain = None
        username = Config.local_username
        pmu = Config.local_pmu
        project_root = os.path.join(Config.local_development_root, project_name)
    else:
        url = project_name + "." + Config.url
        domain = Config.url
        username = Config.server_username
        pmu = Config.server_pmu
        project_root = None
    lesley = Lesley(project_name, url, domain, "Lesley-Paige-Art", \
        Config.github_username, Config.email, username, pmu,
        False, project_root)
    lesley.install(not development)
    lesley.get_paths()
    print("### Cloning repository ###")
    lesley.clone()
    print("### Setting up database ###")
    Lesley.run_sql(os.path.join(lesley.project_path, "setup.sql"))
    Lesley.run_sql("lesley_demo_data.sql")
    print("### Creating database users ###")
    db_name = "lesley"    
    db_admin_username = db_name + "_admin"
    db_viewer_username = db_name + "_viewer"
    db_password = Passwords.lesley_password
    db_admin_sql = Lesley.new_user_sql(db_name, db_admin_username, db_password, True)
    db_viewer_sql = Lesley.new_user_sql(db_name, db_viewer_username, db_password, False)
    db_admin_sql_path = os.path.join(lesley.html_path, "new_admin.sql")
    db_viewer_sql_path = os.path.join(lesley.html_path, "new_viewer.sql")
    Lesley.new_file(db_admin_sql, db_admin_sql_path)
    Lesley.new_file(db_viewer_sql, db_viewer_sql_path)
    Lesley.run_sql(db_admin_sql_path)
    Lesley.run_sql(db_viewer_sql_path)
    os.remove(db_admin_sql_path)
    os.remove(db_viewer_sql_path)
    print("### Creating PHP database access ###")
    db_admin_php = Lesley.credentials_php(db_name, db_admin_username, db_password)
    db_viewer_php = Lesley.credentials_php(db_name, db_viewer_username, db_password)
    db_admin_php_path = os.path.join(lesley.project_path, "admin", "credentials.php")
    db_viewer_php_path = os.path.join(lesley.project_path, "credentials.php")
    Lesley.new_file(db_admin_php, db_admin_php_path)
    Lesley.new_file(db_viewer_php, db_viewer_php_path) 
    print("### Creating Google Recaptcha v3 ###")
    if development:
        recaptcha_php = Lesley.recaptcha_php(reCAPTCHAv3.local_site_key, reCAPTCHAv3.local_secret_key)
    else:
        recaptcha_php = Lesley.recaptcha_php(reCAPTCHAv3.aws_site_key, reCAPTCHAv3.aws_secret_key)
    Lesley.new_file(recaptcha_php, os.path.join(lesley.project_path, "admin", "credentialsrecaptchav3.php"))
    if not development:
        print("### Configuring lesley.spiffindustries.com on NGINX ###")
        lesley.nginx_conf(False, test)
    print("### Setting up PHPMailer ###")
    this_dir = os.path.dirname(os.path.realpath(__file__))
    admin_path = os.path.join(lesley.project_path, "admin")
    urllib.request.urlretrieve("https://github.com/PHPMailer/PHPMailer/archive/master.zip", os.path.join(this_dir, "phpmailer.zip"))
    shutil.unpack_archive(os.path.join(this_dir, "phpmailer.zip"), admin_path)
    shutil.copy(os.path.join(this_dir, "aws_sas.php"), os.path.join(admin_path, "aws_sas.php"))
    print("### Modifying php.ini ###")
    cmd = 'php --ini | grep "Loaded Configuration File"'
    ps = subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
    output = ps.communicate()[0]
    output = output.decode()
    start = output.find('/')
    end = output.find('\n')
    phpfilepath = output[start:end]
    postmaxsize_linenum = SiteBuilder.find_text_in_file('post_max_size', phpfilepath, False)
    uploadmaxfilesize_linenum = SiteBuilder.find_text_in_file('upload_max_filesize', phpfilepath, False)
    with open(phpfilepath, 'r+') as fp:
        lines = fp.readlines()
        fp.seek(0)
        fp.truncate()
        newlines = lines
        newlines[postmaxsize_linenum] = "post_max_size = 128M\n"
        newlines[uploadmaxfilesize_linenum] = "upload_max_filesize = 128M\n"
        fp.writelines(newlines)
    os.system("systemctl restart php*fpm")
    print("### Finalizing ###")
    lesley.finalize()
    # Change folder permissions to allow writing new images as admin
    os.system('chmod -R og+w ' + os.path.join(lesley.html_path, 'admin', 'upload'))
    os.system('chmod -R og+w ' + os.path.join(lesley.html_path, 'img'))
    print("### Downloading and setting up demo art ###")
    shutil.copy(os.path.join(this_dir, "lesley_demo.php"), os.path.join(admin_path, "demo.php"))
    subprocess.run("cd " + admin_path + "; php -f demo.php", capture_output=False, shell=True)
    if not development:
        print("### Creating nightly data reset ###")
        reset_sql = "lesley_demo_data_reset.sql"
        data_sql = "lesley_demo_data.sql"
        reset = "lesley_demo_data_reset"
        shutil.copy(os.path.join(this_dir, reset_sql), lesley.project_path)
        shutil.copy(os.path.join(this_dir, data_sql), lesley.project_path)
        nightly = """#!/bin/bash

mysql < {0}
mysql < {1}
rm {2}
rm {3}
rm {4}
cd {5} && php -f demo.php
""".format(os.path.join(lesley.project_path, reset_sql), os.path.join(lesley.project_path, data_sql), \
    os.path.join(lesley.project_path, "img", "originals", "*"), os.path.join(lesley.project_path, "img", "thumbnails", "*"), \
        os.path.join(lesley.project_path, "img", "watermarked", "*"), admin_path)
        reset_file = os.path.join(lesley.project_path, reset)
        Lesley.new_file(nightly, reset_file)
        os.system("chmod +x " + reset_file)
        cron_cmd = "0 3 * * * " + reset_file + "\n"
        cron_file = "/var/spool/cron/root"
        if os.path.exists(cron_file):
            with open(cron_file, "a") as myfile:
                myfile.write(cron_cmd)
        else:
            Lesley.new_file(cron_cmd, cron_file)
            os.system("chmod 600 " + cron_file)
        os.system("systemctl restart crond")
    print("### Finished! ###")

if __name__ == '__main__':
    error_msg = "Invalid options: enter '-d' or '--development' for development servers and '-t' or '--test' for test certifications (production only)"
    if len(sys.argv) == 2:
        if (sys.argv[1] == '--development' or sys.argv[1] == '-d'):
            main(True)
        elif (sys.argv[1] == '--test' or sys.argv[1] == '-t'):
            main(False, True)
        else:
            print(error_msg)
    elif len(sys.argv) > 2:
        print(error_msg)
    else:
        main(False)
