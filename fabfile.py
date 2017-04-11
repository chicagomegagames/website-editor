from fabric.api import task, env, sudo, run
from fabric.operations import prompt
from fabric.context_managers import cd, hide
from functools import cmp_to_key
from datetime import datetime
import re
import subprocess

env.hosts = [
    "chicagomegagames.com"
]
env.forward_agent = True

git_checkout_path = "/tmp/git_repos/website-editor"
git_repo = "git@gitlab.com:megagames/website-editor.git"
deploy_location = "/home/manager/megagame_manager"

def recent_git_tags():
    git_cmd = subprocess.Popen(["git", "tag"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = git_cmd.communicate()

    if len(err) != 0:
        print("There were errors!")
        print(err.decode("utf8", "strict"))
        raise Exception("Errors in local command `{}`\n{}".format(command, err.decode("utf8", "strict")))

    tags = out.decode("utf8", "strict").strip().split("\n")

    regex = re.compile(r"^v(\d+).(\d+)(|.)(\d*)$", re.M)
    def int_convert(string):
        try:
            return int(string)
        except ValueError:
            return 0

    def tag_sort(tag1, tag2):
        r1 = regex.match(tag1)
        r2 = regex.match(tag2)

        if r1 and not r2:
            return 1
        if r2 and not r2:
            return -1

        v1 = list(map(int_convert, [r1.group(1), r1.group(2), r1.group(4)]))
        v2 = list(map(int_convert, [r2.group(1), r2.group(2), r2.group(4)]))

        if v1[0] != v2[0]:
            return v1[0] - v2[0]
        if v1[1] != v2[1]:
            return v1[1] - v2[1]
        if v1[2] != v2[2]:
            return v1[2] - v2[2]

        return tag1 - tag2

    sorted_tags = sorted(tags, key=cmp_to_key(tag_sort))
    sorted_tags.reverse()
    recent_tags = sorted_tags[0:5]
    recent_tags.reverse()
    return recent_tags

def get_revision():
    print("Recent git tags:")
    for tag in recent_git_tags():
        print("    {}".format(tag))

    revision = prompt("Git revision to deploy:")

    rev_exists_cmd = subprocess.Popen(["git", "cat-file", "-t", revision], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    rev_exists_cmd.communicate()

    if rev_exists_cmd.returncode != 0:
        raise Exception("{} is not a valid git revision!".format(revision))

    return revision

@task
def deploy():
    with(hide('stdout')):
        deploy_time = datetime.now().strftime("%Y%m%d%H%M%S")
        revision = get_revision()

        sudo("chown {user}:{user} {path}".format(user=env.user, path=git_checkout_path ))
        with cd(git_checkout_path):
            run("git fetch --tags {}".format(git_repo))
            run("git checkout {}".format(revision))


        revision_directory = "{}/revisions/{}".format(deploy_location, deploy_time)
        sudo("mkdir {}".format(revision_directory), user="manager")
        sudo("rsync -ac {}/ {}".format(git_checkout_path, revision_directory), user="manager")

        current_directory = "{}/current".format(deploy_location)
        sudo("ln -sfT {} {}".format(revision_directory, current_directory), user="manager")
        sudo("service megagame_manager restart")

        with cd("{}/revisions".format(deploy_location)):
            sudo('ls | sort -r | awk "NR > 6 {print}" | xargs rm -rf', user="manager")
