#!/bin/python3

import os, sys
from sitebuilder import SiteBuilder
from config import Config

class PizzaPricer(SiteBuilder):
    pass

def main(development: bool):
    print("### Initiating \"Pizza Pricer\" site installation ###")
    project_name = "pizzapricer"
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
    pizzaPricer = PizzaPricer(project_name, url, "Pizza-Pricer", \
        Config.github_username, Config.email, username, pmu,
        False, project_root, None)
    pizzaPricer.get_paths()
    print("### Cloning repository ###")
    pizzaPricer.clone()
    print("### Configuring NGINX ###")
    pizzaPricer.nginx_conf()
    print("### Finalizing ###")
    pizzaPricer.finalize()
    print("### Finished! ###")

if __name__ == '__main__':
    if len(sys.argv) > 1:
        if (sys.argv[1] == '--development' or sys.argv[1] == '-d'):
            main(True)
        else:
            print("Invalid option: enter '-d' or '--development' for development servers")
    else:
        main(False)
