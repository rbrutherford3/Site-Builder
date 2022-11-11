#!/bin/python3

import os, sys
from sitebuilder import SiteBuilder
from config import Config

class SpiffIndustries(SiteBuilder):
    pass

def main(development):
    print("### Initiating \"Spiff Industries\" site installation ###")
    project_name = "spiffindustries"
    if development:
        url = None
        username = Config.local_username
        pmu = Config.local_pmu
        project_root = os.path.join(Config.local_development_root, project_name)
    else:
        url = Config.url
        username = Config.server_username
        pmu = Config.server_pmu
        project_root = None
    spiffindustries = SpiffIndustries(project_name, url, "Spiff-Industries-Website", \
        Config.github_username, Config.email, username, pmu,
        True, project_root)
    spiffindustries.install(not development)
    spiffindustries.get_paths()
    spiffindustries.clone()
    print("### Configuring NGINX ###")
    spiffindustries.nginx_conf(False)
    print("### Finalizing ###")
    spiffindustries.finalize()
    print("### Finished! ###")

if __name__ == '__main__':
    if len(sys.argv) > 1:
        if (sys.argv[1] == '--development' or sys.argv[1] == '-d'):
            main(True)
        else:
            print("Invalid option: enter '-d' or '--development' for development servers")
    else:
        main(False)
