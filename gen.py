import shutil
import platform
import sys
from string import Template

SPEC_IN = 'repo.spec.in'
SPEC_FMT = 'SPECS/%s.spec'

REPO_IN = 'SOURCES/repos/rackspace-cloud-monitoring-%s.repo.in'
REPO_FMT = 'SOURCES/repos/rackspace-cloud-monitoring-%s.repo'

rpm = ['redhat', 'fedora', 'suse', 'opensuse', 'centos']


def get_dist():
    return platform.dist()[0].lower()


def get_directory_name():
    dist = platform.dist()
    version = dist[1][0]
    dist = "%s-%s" % (platform.dist()[0], version)
    return "%s-%s" % (dist, platform.machine().lower())


def generate_spec(tmpl, channel):
    data = {
        'channel': channel,
        'system': platform.system().lower(),
        'machine': platform.machine().lower(),
        'dist': get_dist(),
        'directory_name': get_directory_name()
    }

    dist = get_dist()
    if dist == 'redhat' or dist == 'centos':
        dist = platform.dist()

        major = dist[1].split(".")[0]
        distro = dist[0]

        # http://bugs.centos.org/view.php?id=5197
        # CentOS 5.7 identifies as redhat
        if int(major) <= 5 and distro == "redhat":
            f = open('/etc/redhat-release')
            new_dist = f.read().lower().split(" ")[0]
            if new_dist == "centos":
                distro = "centos"

        if major == '5':
            data['key'] = 'centos-5.asc'
        else:
            data['key'] = 'linux.asc'

    elif dist == 'fedora':
        data['key'] = 'linux.asc'

    tmpl = Template(tmpl)

    spec = open(SPEC_FMT % channel, "w")
    spec.write(tmpl.safe_substitute(data))
    spec.close()

    repo_in = open(REPO_IN % channel).read()

    tmpl = Template(repo_in)
    repo = open(REPO_FMT % channel, "w")
    repo.write(tmpl.safe_substitute(data))
    repo.close()

if __name__ == '__main__':
    if get_dist() not in rpm:
        sys.exit(0)

    channels = ['stable', 'unstable', 'master']
    spec_tmpl = open(SPEC_IN).read()
    for channel in channels:
        generate_spec(spec_tmpl, channel)
