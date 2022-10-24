#!/bin/python3

import os
import sys

from sitebuilder import SiteBuilder
from passwords import Passwords
from recaptchav3 import reCAPTCHAv3

class BaltAA(SiteBuilder):
    pass

def main(development: bool):
    print("### Initiating \"Baltimore AA\" site installation ###")
    project_name = "baltaa"
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
    baltaa = BaltAA(project_name, url, "Baltimore-AA", \
        "rbrutherford3", "robbie.rutherford@gmail.com", username, pmu,
        False, project_root, False)
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
        baltaa.nginx_conf()
    print("### Finalizing ###")
    baltaa.finalize()
    print("### Finished! ###")

if __name__ == '__main__':
    if len(sys.argv) > 1:
        if (sys.argv[1] == '--development' or sys.argv[1] == '-d'):
            main(True)
        else:
            print("Invalid option: enter '-d' or '--development' for development servers")
    else:
        main(False)