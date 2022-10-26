#!/bin/python3

import os, sys
import shutil
import subprocess
from pathlib import Path
from passwords import Passwords
from recaptchav3 import reCAPTCHAv3
from sitebuilder import SiteBuilder

class Lesley(SiteBuilder):
    # Install PHP-Imagick
    def install(self, aws: bool) -> None:
        os.system(self.pmu + " install php-imagick -y")
        os.system("systemctl restart php-fpm")

def main(development: bool):
    print("### Initiating \"Lesley Paige Art\" site installation ###")
    project_name = "lesley"
    if development:
        url = ""
        username = "robbie9485"
        pmu = "apt"
        project_root = os.path.join("/home", username, "Development", project_name)
    else:
        url = project_name + ".spiffindustries.com"
        username = "ec2-user"
        pmu = "yum"
        project_root = ""
    lesley = Lesley(project_name, url, "Lesley-Paige-Art", \
        "rbrutherford3", "robbie.rutherford@gmail.com", username, pmu,
        False, project_root, 0)
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
        lesley.nginx_conf()
    print("### Finalizing ###")
    lesley.finalize()
    # Change folder permissions to allow writing new images as admin
    os.system('chmod -R og+w ' + os.path.join(lesley.html_path, 'admin', 'upload'))
    os.system('chmod -R og+w ' + os.path.join(lesley.html_path, 'img'))
    print("### Downloading and setting up demo art ###")
    this_dir = Path(__file__).resolve().parent
    shutil.copy(os.path.join(this_dir, "lesley_demo.php"), os.path.join(lesley.project_path, "admin", "demo.php"))
    subprocess.run("cd " + os.path.join(lesley.project_path, "admin") + "; php -f demo.php", capture_output=False, shell=True)      
    print("### Finished! ###")

if __name__ == '__main__':
    if len(sys.argv) > 1:
        if (sys.argv[1] == '--development' or sys.argv[1] == '-d'):
            main(True)
        else:
            print("Invalid option: enter '-d' or '--development' for development servers")
    else:
        main(False)
