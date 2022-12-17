#!/bin/python3

import os, sys
from sitebuilder import SiteBuilder
from config import Config
from recaptchav3 import reCAPTCHAv3

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
    PDFPublisher.new_file(recaptcha, os.path.join(pdfPublisher.project_path, "recaptchav3.py"))
    print("### Creating systemd service ###")
    if development:
        pdfPublisher.gunicorn(Config.local_username, "Gunicorn service for PDF Publisher", False)
    else:
        pdfPublisher.gunicorn("nginx", "Gunicorn service for PDF Publisher", False)
    pdfPublisher.nginx_conf(True, project_name, False, 5001)
    print("### Setting up nightly maintenance ###")
    cron_cmd = "0 3 * * * systemctl stop pdfpublisher \n" + \
        "5 3 * * * systemctl start pdfpublisher \n"
    cron_file = "/var/spool/cron/root"
    if os.path.exists(cron_file):
        with open(cron_file, "a") as myfile:
            myfile.write(cron_cmd)
    else:
        PDFPublisher.new_file(cron_cmd, cron_file)
        os.system("chmod 600 " + cron_file)
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
