#!/bin/python3

import os
import sys

from sitebuilder import SiteBuilder
from config import Config

class TaskMaster(SiteBuilder):
    pass

def main(development: bool):
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
    taskmaster.nginx_conf(True, "spiffindustries", True, 8000)
    print("### Finalizing ###")
    taskmaster.finalize()
    reset_tasks="""#!/bin/bash
rm -r {0}
mysql -e "DELETE FROM SpiffIndustries.django_migrations WHERE app = '{1}'"
python3 {2} makemigrations {1}
python3 {2} migrate
python3 {2} collectstatic
""".format(os.path.join(taskmaster.project_path, "migrations"), project_name, os.path.join(taskmaster.nginx_html_path, "manage.py"))
    reset_tasks_path = os.path.join(taskmaster.project_path, "reset_tasks")
    TaskMaster.new_file(reset_tasks, reset_tasks_path)
    os.system("chmod +x " + reset_tasks_path)
    os.system("bash " + reset_tasks_path)
    os.system("systemctl restart spiffindustries")
    print("### Finished! ###")

if __name__ == '__main__':
    if len(sys.argv) > 1:
        if (sys.argv[1] == '--development' or sys.argv[1] == '-d'):
            main(True)
        else:
            print("Invalid option: enter '-d' or '--development' for development servers")
    else:
        main(False)
