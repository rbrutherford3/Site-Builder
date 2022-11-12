#!/bin/python3

import os, sys, shutil
from sitebuilder import SiteBuilder
from config import Config
from passwords import Passwords

class SpiffIndustries(SiteBuilder):
    pass

def main(development):
    print("### Initiating \"Spiff Industries\" site installation ###")
    project_name = "spiffindustries"
    if development:
        url = None
        username = Config.local_username
        pmu = Config.local_pmu
        project_root = os.path.join(Config.local_development_root, project_name)
    else:
        url = Config.url
        username = Config.server_username
        pmu = Config.server_pmu
        project_root = None
    spiffindustries = SpiffIndustries(project_name, url, "Spiff-Industries-Website", \
        Config.github_username, Config.email, username, pmu,
        True, project_root)
    spiffindustries.install(not development)
    spiffindustries.get_paths()
    print("### Cloning repository ###")
    spiffindustries.clone()
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
        spiffindustries.gunicorn(Config.local_username, "Gunicorn service for spiffindustries Django server", True)
    else:
        spiffindustries.gunicorn("nginx", "Gunicorn service for spiffindustries Django server", True)
    print("### Configuring NGINX ###")
    spiffindustries.nginx_conf(False)
    print("### Finalizing ###")
    spiffindustries.finalize()
    os.system("systemctl restart " + project_name)
    print("### Finished! ###")

if __name__ == '__main__':
    if len(sys.argv) > 1:
        if (sys.argv[1] == '--development' or sys.argv[1] == '-d'):
            main(True)
        else:
            print("Invalid option: enter '-d' or '--development' for development servers")
    else:
        main(False)
