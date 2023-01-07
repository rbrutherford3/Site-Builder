#!/bin/python3

import os
import sys

from sitebuilder import SiteBuilder
from config import Config
from recaptchav3 import reCAPTCHAv3

class Chess(SiteBuilder):

    # Install Python3 web services
    def install(self, aws: bool) -> None:
        self.pip_install("flask")
        self.pip_install("jsonpickle")

def main(development: bool, test: bool = False):
    print("### Initiating \"ASCII Chess\" site installation ###")
    project_name = "chess"
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
    chess = Chess(project_name, url, domain, "ASCII-Chess", \
        Config.github_username, Config.email, username, pmu,
        False, project_root)
    chess.install(not development)
    chess.get_paths()
    print("### Cloning repository ###")
    chess.clone()
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
    Chess.new_file(recaptcha, os.path.join(chess.project_path, "recaptchav3.py"))
    print("### Creating systemd service ###")
    if development:
        chess.gunicorn(Config.local_username, "Gunicorn service for ASCII chess game", False)
    else:
        chess.gunicorn("nginx", "Gunicorn service for ASCII chess game", False)
    chess.nginx_conf(True, test, project_name, False, 5000)
    print("### Setting up nightly maintenance ###")
    cron_cmd = "0 3 * * * systemctl stop chess \n" + \
        "5 3 * * * systemctl start chess \n"
    cron_file = "/var/spool/cron/root"
    if os.path.exists(cron_file):
        with open(cron_file, "a") as myfile:
            myfile.write(cron_cmd)
    else:
        Chess.new_file(cron_cmd, cron_file)
        os.system("chmod 600 " + cron_file)
    print("### Finalizing ###")
    chess.finalize()
    os.system("systemctl restart " + project_name)
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
