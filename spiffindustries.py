#!/bin/python3

import sys
from sitebuilder import SiteBuilder

class SpiffIndustries(SiteBuilder):
    pass

def main(development):
    print("### Initiating \"Spiff Industries\" site installation ###")
    if development:
        url = ""
        username = "robbie9485"
        pmu = "apt"
    else:
        url = "spiffindustries.com"
        username = "ec2-user"
        pmu = "yum"
    spiffindustries = SpiffIndustries("spiffindustries", url, "Spiff-Industries-Website", \
        "rbrutherford3", "robbie.rutherford@gmail.com", username, pmu,
        True, "", 0)
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