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
    pdfPublisher = PDFPublisher(project_name, url, domain, "PDF-Publisher", \
        Config.github_username, Config.email, username, pmu,
        False, project_root)
    pdfPublisher.install(not development)
    pdfPublisher.get_paths()
    print("### Cloning repository ###")
    pdfPublisher.clone()
    print("### Creating systemd service ###")
    if development:
        pdfPublisher.gunicorn(Config.local_username, "Gunicorn service for PDF Publisher", False)
    else:
        pdfPublisher.gunicorn("nginx", "Gunicorn service for PDF Publisher", False)
    pdfPublisher.nginx_conf(True, project_name, False, 5001)
    print("### Finalizing ###")
    pdfPublisher.finalize()
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
