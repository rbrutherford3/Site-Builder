#!/bin/python3

import os
import sys

from sitebuilder import SiteBuilder
from config import Config

class Chess(SiteBuilder):

    # Install Python3 web services
    def install(self, aws: bool) -> None:
        self.pip_install("flask")
        self.pip_install("gunicorn")
        self.pip_install("jsonpickle")

def main(development: bool):
    print("### Initiating \"ASCII Chess\" site installation ###")
    project_name = "chess"
    if development:
        url = None
        username = Config.local_username
        pmu = Config.local_pmu
        project_root = os.path.join(Config.local_development_root, project_name)
    else:
        url = project_name + "." + Config.url
        username = Config.server_username
        pmu = Config.server_pmu
        project_root = None
    chess = Chess(project_name, url, "ASCII-Chess", \
        Config.github_username, Config.email, username, pmu,
        False, project_root, 5000)
    chess.install(not development)
    chess.get_paths()
    print("### Cloning repository ###")
    chess.clone()
    print("### Creating systemd service ###")
    chess.gunicorn("Gunicorn service for ASCII chess game")
    #if not debug:  # TBD
    #    print("### Configuring chess.spiffindustries.com on NGINX ###")
    #    chess.nginx_conf()
    chess.nginx_conf()
    print("### Finalizing ###")
    chess.finalize()
    print("### Finished! ###")

if __name__ == '__main__':
    if len(sys.argv) > 1:
        if (sys.argv[1] == '--development' or sys.argv[1] == '-d'):
            main(True)
        else:
            print("Invalid option: enter '-d' or '--development' for development servers")
    else:
        main(False)
