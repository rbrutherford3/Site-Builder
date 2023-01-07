#!/bin/python3

import os, sys
from sitebuilder import SiteBuilder
from config import Config

class PizzaPricer(SiteBuilder):
    pass

def main(development: bool, test: bool = False):
    print("### Initiating \"Pizza Pricer\" site installation ###")
    project_name = "pizzapricer"
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
    pizzaPricer = PizzaPricer(project_name, url, domain, "Pizza-Pricer", \
        Config.github_username, Config.email, username, pmu,
        False, project_root)
    pizzaPricer.get_paths()
    print("### Cloning repository ###")
    pizzaPricer.clone()
    if not development:
        print("### Configuring pizzapricer.spiffindustries.com on NGINX ###")
        pizzaPricer.nginx_conf(False, test)
    print("### Finalizing ###")
    pizzaPricer.finalize()
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
