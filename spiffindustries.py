#!/bin/python3

import os, sys, shutil
from sitebuilder import SiteBuilder
from config import Config
from passwords import Passwords
from recaptchav3 import reCAPTCHAv3

class SpiffIndustries(SiteBuilder):
    pass

def start():
    os.system("systemctl start spiffindustries.service")

def main(development: bool, test: bool = False):
    print("### Initiating \"Spiff Industries\" site installation ###")
    project_name = "spiffindustries"
    if development:
        url = None
        domain = None
        username = Config.local_username
        pmu = Config.local_pmu
        project_root = os.path.join(Config.local_development_root, project_name)
    else:
        url = Config.url
        domain = Config.url
        username = Config.server_username
        pmu = Config.server_pmu
        project_root = None
    spiffindustries = SpiffIndustries(project_name, url, domain, "Spiff-Industries-Website", \
        Config.github_username, Config.email, username, pmu,
        True, project_root)
    spiffindustries.install(not development)
    spiffindustries.get_paths()
    print("### Cloning repository ###")
    spiffindustries.clone()
    print("### Creating Google Recaptcha v3 ###")
    recaptcha="""#!/bin/python3

# Class for storing the Google reCAPTCHAv3 keys
class reCAPTCHAv3:
    site_key = "{0}"
    secret_key = "{1}"
"""
    if development:
        recaptcha = recaptcha.format(reCAPTCHAv3.local_site_key, reCAPTCHAv3.local_secret_key)
    else:
        recaptcha = recaptcha.format(reCAPTCHAv3.aws_site_key, reCAPTCHAv3.aws_secret_key)
    SpiffIndustries.new_file(recaptcha, os.path.join(spiffindustries.project_path, "recaptchav3.py"))
    print("### Copying AWS SAS credentials ###")
    shutil.copy("aws_sas.py", spiffindustries.project_path)
    print("### Copying configuration file ###")
    shutil.copy("spiffindustries_config.py", spiffindustries.project_path)
    print("### Setting up database ###")
    SpiffIndustries.run_sql(os.path.join(spiffindustries.project_path, "setup.sql"))
    print("### Creating database user ###")
    db_user_sql = SpiffIndustries.new_user_sql("SpiffIndustries", "spiff", Passwords.spiff_password, True)
    db_user_sql_path = os.path.join(spiffindustries.html_path, "new_user.sql")
    SpiffIndustries.new_file(db_user_sql, db_user_sql_path)
    SpiffIndustries.run_sql(db_user_sql_path)
    os.remove(db_user_sql_path)
    print("### Creating systemd service ###")
    if development:
        spiffindustries.gunicorn(Config.local_username, "Gunicorn service for spiffindustries Django server", True, 3, 1)
    else:
        spiffindustries.gunicorn("nginx", "Gunicorn service for spiffindustries Django server", True, 3, 1)
    print("### Configuring NGINX ###")
    spiffindustries.nginx_conf(False, test)
    print("### Setting up nightly maintenance ###")
    cron_cmd = "0 3 * * * systemctl stop spiffindustries \n" + \
        "5 3 * * * systemctl start spiffindustries \n" + \
            "0 3 * * * mv " + os.path.join(spiffindustries.project_path, "index.html") + " " + \
                os.path.join(spiffindustries.project_path, "index_saved.html") + " && " + \
                    "mv " + os.path.join(spiffindustries.project_path, "maintenance.html") + " " + \
                        os.path.join(spiffindustries.project_path, "index.html") + "\n" + \
                            "5 3 * * * mv " + os.path.join(spiffindustries.project_path, "index.html") + " " + \
                                os.path.join(spiffindustries.project_path, "maintenance.html") + " && " + \
                                    "mv " + os.path.join(spiffindustries.project_path, "index_saved.html") + " " + \
                                        os.path.join(spiffindustries.project_path, "index.html") + "\n"
    cron_file = "/var/spool/cron/root"
    if os.path.exists(cron_file):
        with open(cron_file, "a") as myfile:
            myfile.write(cron_cmd)
    else:
        SpiffIndustries.new_file(cron_cmd, cron_file)
        os.system("chmod 600 " + cron_file)
    print("### Modifying nginx.conf ###")
    nginx_conf_file_path = "/etc/nginx/nginx.conf"
    search_string = "    server {\n"
    start_num = SpiffIndustries.find_text_in_file(search_string, nginx_conf_file_path, True)
    search_string = "    }\n"
    end_num = SpiffIndustries.find_text_in_file(search_string, nginx_conf_file_path, True)
    with open(nginx_conf_file_path, 'r+') as fp:
        lines = fp.readlines()
        fp.seek(0)
        fp.truncate()
        newlines = [''] * (len(lines) - (end_num - start_num + 1))
        newlines[0:start_num-1] = lines[0:start_num-1]
        newlines[start_num:] = lines[end_num+1:]
        fp.writelines(newlines) 
    print("### Finalizing ###")
    spiffindustries.finalize()
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
