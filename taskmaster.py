#!/bin/python3

import os
import sys

from sitebuilder import SiteBuilder
from config import Config

class TaskMaster(SiteBuilder):
    pass

def main(development: bool, test: bool = False):
    print("### Initiating \"Taskmaster\" site installation ###")
    project_name = "taskmaster"
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
    taskmaster = TaskMaster(project_name, url, domain, "Task-Master", \
        Config.github_username, Config.email, username, pmu,
        False, project_root)
    print("### Cloning repository ###")
    taskmaster.get_paths()
    taskmaster.clone()
    print("### Configuring NGINX ###")
    taskmaster.nginx_conf(True, test, "spiffindustries", True, 8000)
    print("### Finalizing ###")
    taskmaster.finalize()
    manage_py_path = os.path.join(taskmaster.nginx_html_path, "manage.py")
    os.system(f"python3 {manage_py_path} makemigrations {project_name}")
    os.system(f"python3 {manage_py_path} migrate")
    os.system(f"python3 {manage_py_path} collectstatic")
    os.system("systemctl restart spiffindustries")
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
