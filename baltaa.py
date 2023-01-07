#!/bin/python3

import os
import sys
import shutil

from sitebuilder import SiteBuilder
from passwords import Passwords
from recaptchav3 import reCAPTCHAv3
from config import Config

class BaltAA(SiteBuilder):
    pass

def main(development: bool, test: bool = False):
    print("### Initiating \"Baltimore AA\" site installation ###")
    project_name = "baltaa"
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
    baltaa = BaltAA(project_name, url, domain, "Baltimore-AA", \
        Config.github_username, Config.email, username, pmu,
        False, project_root)
    print("### Cloning repository ###")
    baltaa.get_paths()
    baltaa.clone()
    print("### Setting up database ###")
    BaltAA.run_sql(os.path.join(baltaa.project_path, "setup.sql"))
    BaltAA.run_sql("baltaa_demo_data.sql")
    db_name = "baltaa"
    print("### Creating database users ###")
    db_admin_username = db_name + "_admin"
    db_viewer_username = db_name + "_viewer"
    db_password = Passwords.baltaa_password
    db_admin_sql = BaltAA.new_user_sql(db_name, db_admin_username, db_password, True)
    db_viewer_sql = BaltAA.new_user_sql(db_name, db_viewer_username, db_password, False)
    db_admin_sql_path = os.path.join(baltaa.html_path, "new_admin.sql")
    db_viewer_sql_path = os.path.join(baltaa.html_path, "new_viewer.sql")
    BaltAA.new_file(db_admin_sql, db_admin_sql_path)
    BaltAA.new_file(db_viewer_sql, db_viewer_sql_path)
    BaltAA.run_sql(db_admin_sql_path)
    BaltAA.run_sql(db_viewer_sql_path)
    os.remove(db_admin_sql_path)
    os.remove(db_viewer_sql_path)
    print("### Creating PHP database access ###")
    db_admin_php = BaltAA.credentials_php(db_name, db_admin_username, db_password)
    db_viewer_php = BaltAA.credentials_php(db_name, db_viewer_username, db_password)
    db_admin_php_path = os.path.join(baltaa.project_path, "lib", "credentials.php")
    db_viewer_php_path = os.path.join(baltaa.project_path, "lib", "credentialsview.php")
    BaltAA.new_file(db_admin_php, db_admin_php_path)
    BaltAA.new_file(db_viewer_php, db_viewer_php_path)
    print("### Creating Google Recaptcha v3 ###")
    if development:
        recaptcha_php = BaltAA.recaptcha_php(reCAPTCHAv3.local_site_key, reCAPTCHAv3.local_secret_key)
    else:
        recaptcha_php = BaltAA.recaptcha_php(reCAPTCHAv3.aws_site_key, reCAPTCHAv3.aws_secret_key)
    BaltAA.new_file(recaptcha_php, os.path.join(baltaa.project_path, "lib", "credentialsrecaptchav3.php"))
    if not development:
        print("### Configuring baltaa.spiffindustries.com on NGINX ###")
        baltaa.nginx_conf(False, test)
    if not development:
        this_dir = os.path.dirname(os.path.realpath(__file__))
        print("### Creating nightly data reset ###")
        reset_sql = "baltaa_demo_data_reset.sql"
        data_sql = "baltaa_demo_data.sql"
        reset = "baltaa_demo_data_reset"
        shutil.copy(os.path.join(this_dir, reset_sql), baltaa.project_path)
        shutil.copy(os.path.join(this_dir, data_sql), baltaa.project_path)
        nightly = """#!/bin/bash

mysql < {0}
mysql < {1}
""".format(os.path.join(baltaa.project_path, reset_sql), os.path.join(baltaa.project_path, data_sql))
        reset_file = os.path.join(baltaa.project_path, reset)
        BaltAA.new_file(nightly, reset_file)
        os.system("chmod +x " + reset_file)
        cron_cmd = "0 3 * * * " + reset_file + "\n"
        cron_file = "/var/spool/cron/root"
        if os.path.exists(cron_file):
            with open(cron_file, "a") as myfile:
                myfile.write(cron_cmd)
        else:
            BaltAA.new_file(cron_cmd, cron_file)
            os.system("chmod 600 " + cron_file)
        os.system("systemctl restart crond")
    print("### Finalizing ###")
    baltaa.finalize()
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
