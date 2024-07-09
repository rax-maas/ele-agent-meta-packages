""" Module gen """
import platform
import sys
import re
import json
import argparse
from string import Template
import distro
from tools import pkgutils

SPEC_IN = 'repo.spec.in'
SPEC_FMT = 'SPECS/%s.spec'

REPO_IN = 'SOURCES/repos/rackspace-cloud-monitoring-%s.repo.in'
REPO_FMT = 'SOURCES/repos/rackspace-cloud-monitoring-%s.repo'

DEB_POSTINST_IN = 'DEB/rackspace-cloud-monitoring-meta-%s-1.0/debian/postinst.in'
DEB_POSTINST = 'DEB/rackspace-cloud-monitoring-meta-%s-1.0/debian/postinst'

RPM = ['redhat', 'fedora', 'suse', 'opensuse', 'centos']
DEB = ['debian', 'ubuntu']
DISTS = RPM + DEB

def get_dist():
    """Get platform distribution in lower case """
    return distro.id().lower()

def get_dist_version():
    """Get platform distribution version """
    return distro.version()

def get_directory_name():
    """Returning package directory"""
    return pkgutils.pkg_dir()

def generate_spec(options_param, tmpl, channel_val):
    """Generating spec"""
    data = {
        'channel': channel_val,
        'system': platform.system().lower(),
        'machine': platform.machine().lower(),
        'dist': get_dist(),
        'directory_name': get_directory_name()
    }

    dist_value = get_dist()
    if dist_value in ('redhat', 'centos'):
        major = get_dist_version().split(".")[0]
        data['directory_name'] = get_redhat_directory_name(data['directory_name'])

        # http://bugs.centos.org/view.php?id=5197
        # CentOS 5.7 identifies as redhat
        if int(major) <= 5 and get_dist() == "redhat":
            with open('/etc/redhat-release', 'r', encoding='utf-8') as os_file:
                new_dist = os_file.read().lower().split(" ")[0]
                if new_dist == "centos":
                    # pylint: disable=unused-variable
                    dist_name = "centos"

        if major == '5':
            data['key'] = 'centos-5.asc'
        else:
            data['key'] = 'linux.asc'

    elif dist_value == 'fedora':
        data['key'] = 'linux.asc'

    if options_param.get('distribution'):
        data['directory_name'] = options_param['distribution']

    tmpl = Template(tmpl)

    with open(SPEC_FMT % channel_val, 'w', encoding='utf-8') as spec:
        spec.write(tmpl.safe_substitute(data))
        spec.close()

    with open(REPO_IN % channel_val, 'r', encoding='utf-8') as repo_in:
        tmpl = Template(repo_in.read())

    with open(REPO_FMT % channel_val, 'w', encoding='utf-8') as repo:
        repo.write(tmpl.safe_substitute(data))
        repo.close()

def get_redhat_directory_name(directory_name):
    """Module to get redhat directory name using regular expression search. """
    if re.search('redhat-6', directory_name):
        directory_name = 'redhat-6-x86_64'
    elif re.search('redhat-7', directory_name):
        directory_name = 'redhat-7-x86_64'
    elif re.search('redhat-5', directory_name):
        directory_name = 'redhat-5-x86_64'
    elif re.search('centos-5', directory_name):
        directory_name = 'centos-5-x86_64'
    elif re.search('centos-6', directory_name):
        directory_name = 'centos-6-x86_64'
    elif re.search('centos-7', directory_name):
        directory_name = 'centos-7-x86_64'
    return directory_name

def get_debian_directory_name(directory_name):
    """Module to get debian directory name using regular expression search. """
    if re.search('debian-7.(.*?)-x86_64', directory_name):
        directory_name = 'debian-wheezy-x86_64'
    elif re.search('debian-6.(.*?)-x86_64', directory_name):
        directory_name = 'debian-squeeze-x86_64'
    elif re.search('debian-8.(.*?)-x86_64', directory_name):
        directory_name = 'debian-jessie-x86_64'
    elif re.search('debian-9.(.*?)-x86_64', directory_name):
        directory_name = 'debian-stretch-x86_64'
    return directory_name

def generate_deb(options_param, channel_val):
    """Generating DEB"""
    data = {
        'channel': channel_val,
        'system': platform.system().lower(),
        'machine': platform.machine().lower(),
        'dist': get_dist(),
        'directory_name': get_directory_name()
    }

    data['directory_name'] = get_debian_directory_name(data['directory_name'])

    if options_param.get('distribution'):
        data['directory_name'] = options_param.get('distribution')

    with open(DEB_POSTINST_IN % channel_val, 'r', encoding='utf-8') as tmpl:
        tmpl = Template(tmpl.read())

    with open(DEB_POSTINST % channel_val, 'w', encoding='utf-8') as postinst:
        postinst.write(tmpl.safe_substitute(data))
        postinst.close()


if __name__ == '__main__':
    PARSER = argparse.ArgumentParser(description='To parse distribution and target arch')
    PARSER.add_argument("-d", "--distribution", dest="distribution", help="Specify distribution")
    PARSER.add_argument("-a", "--target-arch", dest="target_arch", default='x86_64',
                        help="Specify target architecture")
    ARGS = PARSER.parse_args()

    CONFIG = {}
    CONFIG['distribution'] = ARGS.distribution
    CONFIG['target_arch'] = ARGS.target_arch

    with open('config.json', 'w', encoding='utf-8') as config_file:
        json.dump(CONFIG, config_file)
        config_file.close()

    DIST = get_dist()
    if DIST not in DISTS:
        sys.exit(0)

    CHANNELS = ['stable', 'unstable', 'master']

    if DIST in RPM:
        with open(SPEC_IN, 'r', encoding='utf-8') as SPEC_TMPL:
            for channel in CHANNELS:
                generate_spec(CONFIG, SPEC_TMPL.read(), channel)

    if DIST in DEB:
        for channel in CHANNELS:
            generate_deb(CONFIG, channel)
