#!/bin/python3

import sys
from sitebuilder import SiteBuilder
from config import Config

class SpiffIndustries(SiteBuilder):
    pass

def main(development):
    print("### Initiating \"Spiff Industries\" site installation ###")
    if development:
        url = None
        username = Config.local_username
        pmu = Config.local_pmu
    else:
        url = Config.url
        username = Config.server_username
        pmu = Config.server_pmu
    spiffindustries = SpiffIndustries("spiffindustries", url, "Spiff-Industries-Website", \
        Config.github_username, Config.email, username, pmu,
        True, None, None)
    spiffindustries.install(not development)
    spiffindustries.get_paths()
    spiffindustries.clone()
    print("### Configuring NGINX ###")
    spiffindustries.nginx_conf()
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
