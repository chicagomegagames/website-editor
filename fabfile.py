from fabric.api import task, env, sudo, run
from fabric.operations import prompt
from fabric.context_managers import cd, hide
from datetime import datetime
import subprocess

env.hosts = [
    "chicagomegagames.com"
]
env.forward_agent = True

git_checkout_path = "/tmp/git_repos/website-editor"
git_repo = "git@gitlab.com:megagames/website-editor.git"
deploy_location = "/home/manager/megagame_manager"

def get_revision():
    git_cmd = subprocess.Popen(["git", "tag"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = git_cmd.communicate()

    if len(err) != 0:
        print("There were errors!")
        print(err.decode("utf8", "strict"))
        raise Exception("Errors in local command `{}`\n{}".format(command, err.decode("utf8", "strict")))

    tags = out.decode("utf8", "strict").strip().split("\n")
    tags.reverse()
    recent_tags = tags[0:5]
    recent_tags.reverse()
    print("Recent git tags:")
    for tag in recent_tags:
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

        output = sudo("ls {}/revisions".format(deploy_location)).strip().split("\n")
        output.reverse()
        for directory in output[5:]:
            sudo("rm -rf {}/revisions/{}".format(deploy_location, directory), user="manager")
