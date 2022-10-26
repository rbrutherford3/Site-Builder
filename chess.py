#!/bin/python3

import os
import sys

from sitebuilder import SiteBuilder

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
        url = ""
        username = "robbie9485"
        pmu = "apt"
        project_root = os.path.join("/home", username, "Development", project_name)
    else:
        url = project_name + ".spiffindustries.com"
        username = "ec2-user"
        pmu = "yum"
        project_root = ""
    chess = Chess(project_name, url, "ASCII-Chess", \
        "rbrutherford3", "robbie.rutherford@gmail.com", username, pmu,
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