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
        if aws:
            os.system(self.pmu + " install curl cabextract xorg-x11-font-utils fontconfig -y")
            os.system("rpm -i https://downloads.sourceforge.net/project/mscorefonts2/rpms/msttcore-fonts-installer-2.6-1.noarch.rpm")
        else:
            os.system(self.pmu + " install ttf-mscorefonts-installer -y")

def start():
    os.system("systemctl start pdfpublisher.service")

def main(development: bool, test:bool = False):
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
        pdfPublisher.gunicorn(Config.local_username, "Gunicorn service for PDF Publisher", False, 5, 3)
    else:
        pdfPublisher.gunicorn("nginx", "Gunicorn service for PDF Publisher", False, 5, 3)
    pdfPublisher.nginx_conf(True, test, project_name, False, 5001)
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
    print("### Modifying nginx.conf ###")
    nginx_conf_file_path = "/etc/nginx/nginx.conf"
    search_string = "client_max_body_size"
    line_num = PDFPublisher.find_text_in_file(search_string, nginx_conf_file_path, False)
    if line_num > 0:
        with open(nginx_conf_file_path, 'r+') as fp:
            lines = fp.readlines()
            fp.seek(0)
            fp.truncate()
            newlines = [''] * (len(lines) -1)
            newlines[0:line_num-1] = lines[0:line_num]
            newlines[line_num:] = lines[line_num+1:]
            fp.writelines(newlines)
    search_string = "http {\n"
    line_num = PDFPublisher.find_text_in_file(search_string, nginx_conf_file_path, True)
    if line_num > 0:
        with open(nginx_conf_file_path, 'r+') as fp:
            lines = fp.readlines()
            fp.seek(0)
            fp.truncate()
            newlines = [''] * (len(lines)+5)
            newlines[0:line_num] = lines[0:line_num+1]
            newlines[line_num+1] = "    client_max_body_size 1024M;\n"
            newlines[line_num+2] = "    proxy_connect_timeout 600;\n"
            newlines[line_num+3] = "    proxy_send_timeout 600;\n"
            newlines[line_num+4] = "    proxy_read_timeout 600;\n"
            newlines[line_num+5] = "    send_timeout 600;\n"
            newlines[line_num+6:] = lines[line_num+1:]
            fp.writelines(newlines)       
    print("### Finalizing ###")
    pdfPublisher.finalize()
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
