#!/bin/python3

import os, sys
from sitebuilder import SiteBuilder
from config import Config

class PDFPublisher(SiteBuilder):
    def install(self, aws: bool) -> None:
        if aws:
            os.system("amazon-linux-extras install libreoffice -y")
        else:
            os.system(self.pmu + " install libreoffice -y")
        os.system("pip3 install PyPDF2")
        os.system("pip3 install FPDF")
        os.system("pip3 install pdf.tocgen")

def main(development: bool):
    print("### Initiating \"PDF Publisher\" site installation ###")
    project_name = "pdfpublisher"
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
    pdfPublisher = PDFPublisher(project_name, url, "PDF-Publisher", \
        Config.github_username, Config.email, username, pmu,
        False, project_root, 5001)
    pdfPublisher.install(not development)
    pdfPublisher.get_paths()
    print("### Cloning repository ###")
    pdfPublisher.clone()
    print("### Creating systemd service ###")
    pdfPublisher.gunicorn("Gunicorn service for PDF Publisher")
    pdfPublisher.nginx_conf()
    print("### Finalizing ###")
    pdfPublisher.finalize()
    print("### Finished! ###")

if __name__ == '__main__':
    if len(sys.argv) > 1:
        if (sys.argv[1] == '--development' or sys.argv[1] == '-d'):
            main(True)
        else:
            print("Invalid option: enter '-d' or '--development' for development servers")
    else:
        main(False)
