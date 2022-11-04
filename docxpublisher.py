#!/bin/python3

import os, sys
from sitebuilder import SiteBuilder
from config import Config

class DocXPublisher(SiteBuilder):
    def install(self, aws: bool) -> None:
        if aws:
            os.system("amazon-linux-extras install libreoffice -y")
        else:
            os.system(self.pmu + " install libreoffice -y")
        os.system("pip3 install PyPDF2")
        os.system("pip3 install FPDF")

def main(development: bool):
    print("### Initiating \"docX Publisher\" site installation ###")
    project_name = "docxpublisher"
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
    docxPublisher = DocXPublisher(project_name, url, "docx-Publisher", \
        Config.github_username, Config.email, username, pmu,
        False, project_root, 5001)
    docxPublisher.install(not development)
    docxPublisher.get_paths()
    print("### Cloning repository ###")
    docxPublisher.clone()
    print("### Creating systemd service ###")
    docxPublisher.gunicorn("Gunicorn service for docX Publisher")
    docxPublisher.nginx_conf()
    print("### Finalizing ###")
    docxPublisher.finalize()
    print("### Finished! ###")

if __name__ == '__main__':
    if len(sys.argv) > 1:
        if (sys.argv[1] == '--development' or sys.argv[1] == '-d'):
            main(True)
        else:
            print("Invalid option: enter '-d' or '--development' for development servers")
    else:
        main(False)
