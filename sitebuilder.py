#!/bin/python3

import os, shutil
from subprocess import run
import subprocess

# Generic class for setting up a site from a Github repository
class SiteBuilder():
    # Assign constants
    github_url = "https://github.com/"
    nginx_conf_path = "/etc/nginx/conf.d"
    dir_path = os.path.dirname(os.path.realpath(__file__))

    # Constructor
    def __init__(self, project_name: str, url: str, github_name: str, \
        github_username: str, email: str, username: str, pmu: str, \
            is_web_root: bool, project_path: str, has_gunicorn_service: bool, *args) -> None:
        
        # Run only as 'sudo' or 'root'
        if os.geteuid() > 0:
            print("Please re-run as root")
            exit()

        # Save variables
        self.project_name = project_name
        self.url = url
        self.www_url = "www." + url
        self.github_name = github_name
        self.github_username = github_username
        self.git_url = self.github_url + github_username + "/" + github_name
        self.email = email
        self.username = username
        self.home_dir = "/home/" + self.username
        self.pmu = pmu
        self.is_web_root = is_web_root
        self.project_path = project_path
        self.has_gunicorn_service = has_gunicorn_service
        if len(args) == 0:
            self.has_reCAPTCHAv3 = False
        elif len(args) == 2:
            self.has_reCAPTCHAv3 = True
            self.reCAPTCHAv3_site_key = args[0]
            self.reCAPTCHAv3_secret_key = args[1]
        else:
            print("Invalid number of arguments")
            exit()

        if len(self.url) == 0:
            self.debug = True
        else:
            self.debug = False
            self.nginx_domain_path = os.path.join(self.nginx_conf_path, self.url + ".conf")
            self.nginx_domain_path_www = os.path.join(self.nginx_conf_path, self.www_url + ".conf")

    def get_paths(self) -> None:
        # Find NGINX HTML path
        nginx_html_path_1 = "/usr/share/nginx/www"
        nginx_html_path_2 = "/usr/share/nginx/html"
        nginx_html_path_3 = "/var/www/html"
        if os.path.exists(nginx_html_path_1):
            self.nginx_html_path = nginx_html_path_1
        elif os.path.exists(nginx_html_path_2):
            self.nginx_html_path = nginx_html_path_2
        elif os.path.exists(nginx_html_path_3):
            self.nginx_html_path = nginx_html_path_3
        else:
            print("Cannot find NGINX HTML path")
            exit()
        if self.is_web_root:
            self.html_path = self.nginx_html_path
        else:
            self.html_path = os.path.join(self.nginx_html_path, self.project_name)

        # If a project path is provided, a symlink is needed:
        if len(self.project_path) == 0:
            self.has_symlink = False
            self.project_path = self.html_path
        else:
            self.has_symlink = True

    # Clone project from GitHub
    def clone(self) -> None:
        if os.path.exists(self.project_path):
            if os.path.isdir(self.project_path):
                SiteBuilder.delete_dir(self.project_path)
            else:
                os.remove(self.project_path)
        os.system("git clone " + self.git_url + " " + self.project_path)
        # Symlink from HTML directory to project path
        if self.has_symlink:   # maybe change
            if os.path.exists(self.html_path):
                if os.path.isdir(self.html_path):
                    SiteBuilder.delete_dir(self.html_path)
                else:
                    os.remove(self.html_path)
            os.system("ln -s " + self.project_path + " " + self.html_path)

    # Create a PHP file for storing database credentials
    def credentials_php(db_name: str, username: str, password: str) -> str:
        php = """<?php

function credentials() {{
	$host = 'localhost';
	$database = '{0}';
	$username = '{1}';
	$password = '{2}';
	return array('HOST' => $host, 'DATABASE' => $database, 'USERNAME' => $username, 'PASSWORD' => $password);
}}

?>
""".format(db_name, username, password)
        return php

    # Create a SQL statement for creating a new MySQL user
    def new_user_sql(db_name: str, username: str, password: str, admin: bool) -> str:
        if admin:
            privileges = "ALL PRIVILEGES"
        else:
            privileges = "SELECT"
        sql="""CREATE USER {1}@localhost IDENTIFIED BY '{2}';
GRANT {3} ON `{0}`.* TO {1}@localhost;
FLUSH PRIVILEGES;
""".format(db_name, username, password, privileges)

        return sql

    # Create a PHP file for storing the Google reCAPTCHAv3 credentials
    def recaptcha_php(recaptchav3_site_key: str, recaptchav3_secret_key: str) -> str: 
        return """<?php
    const RECAPTCHA_SITE_KEY_V3="{0}";
    const RECAPTCHA_SECRET_KEY_V3="{1}";
?>
""".format(recaptchav3_site_key, recaptchav3_secret_key)

    # Create NGINX configuration files for domain, subdomains and http-to-https forwarding
    # Include SSL certificate locations as needed, using the get_ssl function
    def nginx_conf(self) -> None:
        # Create conf file for http-to-https forwarding on initial site creation
        if self.is_web_root:
            secure_conf="""server {
    listen 80 default_server;
    listen [::]:80 default_server;
    server_name _;
    return 301 https://$host$request_uri;
}"""
            SiteBuilder.new_file(secure_conf, os.path.join(self.nginx_conf_path, "secure.conf"))
        
        # Only create a conf file on the development server for socket connections
        if self.debug:
            if self.has_gunicorn_service:
                conf="""server {{
    listen 80;
    server_name {0};
    access_log /var/log/nginx/access.log;
    error_log /var/log/nginx/error.log;
    root {1};
        
    location / {{
        proxy_pass http://unix:/usr/share/nginx/sockets/{2}.sock;
        proxy_set_header Host $http_host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }}
}}
""".format(self.project_name, self.html_path, self.project_name)
                SiteBuilder.new_file(conf, os.path.join(self.nginx_conf_path, self.project_name + ".conf"))
        else:
            # Get SSL certificate
            certificate_path, key_path = SiteBuilder.get_ssl(self.email, self.url)
            # Connect to socket if using a systemd service like GUNICORN
            if self.has_gunicorn_service:
                conf="""server {{
    listen 443 ssl http2;
    server_name {0};
    ssl_certificate {1};
    ssl_certificate_key {2};
    access_log /var/log/nginx/access.log;
    error_log /var/log/nginx/error.log;
    root {3};
        
    location / {{
        proxy_pass http://unix:/usr/share/nginx/sockets/{4}.sock;
        proxy_set_header Host $http_host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }}
}}
""".format(self.url, certificate_path, key_path, self.html_path, self.project_name)
            # Normal setup (No socket, SSL certificates, 2 conf files [reg. and www]):
            else:
                conf="""server {{
    listen 443 ssl http2;
    server_name {0};
    ssl_certificate {1};
    ssl_certificate_key {2};
    access_log /var/log/nginx/access.log;
    error_log /var/log/nginx/error.log;
    root {3};
    
    location / {{
        index		    index.html index.htm index.php;
    }}
    
    location ~* \.php$ {{
        fastcgi_pass	unix:/var/run/php-fpm/www.sock;
        fastcgi_index   index.php;
        include		    fastcgi_params;
        fastcgi_param   SCRIPT_FILENAME	$document_root$fastcgi_script_name;
        fastcgi_param   SCRIPT_NAME	$fastcgi_script_name;
    }}
}}
""".format(self.url, certificate_path, key_path, self.html_path)
            SiteBuilder.new_file(conf, self.nginx_domain_path)
            
            certificate_path_www, key_path_www = SiteBuilder.get_ssl(self.email, self.www_url)
            conf_www="""server {{
    listen 443 ssl http2;
    server_name {0};
    ssl_certificate {1};
    ssl_certificate_key {2};
    return 301 https://{3}$request_uri;
}}
""".format(self.www_url, certificate_path_www, key_path_www, self.url)
            SiteBuilder.new_file(conf_www, self.nginx_domain_path_www)
        
        # Create a socket path if it doesn't exist
        if self.has_gunicorn_service:
            if not os.path.exists("/usr/share/nginx/sockets"):
                os.mkdir("/usr/share/nginx/sockets")

    # Create a new file and place a string in it
    def new_file(contents: str, filepath: str) -> None:
        file = open(filepath, "x")
        file.write(contents)
        file.close()

    # Run SQL statement(s) from a file
    def run_sql(filepath: str) -> None:
        os.system("mysql < " + filepath)

    # Get an SSL certificate for a domain or subdomain (tricky string operation!)
    def get_ssl(email: str, url: str) -> str:
        # Get the certificate location output from the system
        ssl = os.popen("certbot certonly -n --agree-tos -m " + email + " --nginx -d " + url).read()

        # Find the first .pem file location by the string that precedes it.
        certificate_search_begin = "Your certificate and chain have been saved at:\n   "
        search_end = ".pem"
        certificate_path_start = ssl.find(certificate_search_begin) + len(certificate_search_begin)
        certificate_path_end = ssl[certificate_path_start:].find(search_end) + certificate_path_start + len(search_end)
        certificate_path = ssl[certificate_path_start:certificate_path_end]

        # Find the second .pem file location by the string that precedes it.
        key_search_begin = "Your key file has been saved at:\n   "
        key_path_start = ssl.find(key_search_begin) + len(key_search_begin)
        key_path_end = ssl[key_path_start:].find(search_end) + key_path_start + len(search_end)
        key_path = ssl[key_path_start:key_path_end]

        return certificate_path, key_path

    # Createa a gunicorn systemd file and install it
    def gunicorn(self, description: str) -> None:

        data = subprocess.run("runuser -l " + self.username + " -c 'which gunicorn'", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        gunicorn_path = data.stdout.decode().replace("\n","")
        service_name = self.project_name + ".service"
        service="""[Unit]
Description={0}
After=network.target

[Service]
User=root
Group=root
WorkingDirectory={1}
Environment="PATH=cd"
ExecStart={2} --workers=5 --threads=2 --bind=unix:/usr/share/nginx/sockets/{3}.sock app:app

[Install]
WantedBy=multi-user.target
"""
        service = service.format(description, self.project_path, gunicorn_path, self.project_name)
        SiteBuilder.new_file(service, os.path.join("/etc/systemd/system/", service_name))
        os.system("systemctl daemon-reload")
        os.system("systemctl enable " + service_name)

    # Install all software for the server, including NGINX, PHP, MySQL, Python, etc
    def install(self, aws: bool) -> None:
        # Make system updates and upgrades
        os.system(self.pmu + " update -y")
        if self.pmu == "apt":
            os.system(self.pmu + " upgrade -y")
        # Install NGINX
        if aws:
            os.system("amazon-linux-extras install nginx1 -y")
            os.system("amazon-linux-extras install php8.0 -y")
            os.system("amazon-linux-extras install mariadb10.5 -y")
        else:
            os.system(self.pmu + " install nginx -y")
            os.system(self.pmu + " install php -y")
            os.system(self.pmu + " install mariadb-server -y")
        os.system("systemctl restart nginx")
        os.system("systemctl restart mariadb")
        os.system(self.pmu + " install php-fpm -y")
        os.system("systemctl restart php-fpm")
        os.system(self.pmu + " install php-curl -y")
        os.system(self.pmu + " install git -y") # Install Git
        # Install Python3 and PIP package manager
        if aws:
            os.system("amazon-linux-extras install python3.8 -y")
        else:
            os.system(self.pmu + " install python3 -y")
        os.system(self.pmu + " install python3-pip -y")
        # Install certbot (aka letsencrypt) for SSL certificates
        if aws:
            os.system("amazon-linux-extras install epel -y")
        os.system(self.pmu + " install certbot-nginx -y")

    # Install a PIP component on both user and root for systemd service purposes
    def pip_install(self, component):
        os.system("runuser -l " + self.username + " -c 'pip3 install " + component + "'")
        os.system("pip3 install " + component)

    # Copy files from one directory to another directory that already exists
    def copytree_existing(src, dst):
        items = os.listdir(src)
        for item in items:
            item_src = os.path.join(src, item)
            item_dst = os.path.join(dst, item)
            if os.path.isdir(item_src):
                shutil.copytree(item_src, item_dst)
            else:
                shutil.copy2(item_src, item_dst)

    def delete_dir(top: str):
        for root, dirs, files in os.walk(top, topdown=False):
            for name in files:
                os.remove(os.path.join(root, name))
            for name in dirs:
                os.rmdir(os.path.join(root, name))

    # Kick out the jams
    def finalize(self) -> None:
        if self.has_symlink:
            os.system("chown -R " + self.username + ":" + self.username + " " + self.project_path)
        if not self.debug:
            os.system("chown -R nginx:nginx " + self.html_path)
        if self.has_gunicorn_service:
            os.system("systemctl restart " + self.project_name)
        os.system("systemctl restart nginx")