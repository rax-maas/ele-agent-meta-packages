#!/usr/bin/env python
"""Package utility module to read various data """
import os
import errno
import platform
import sys
import json
import subprocess

# Figure out what type of package to build based on platform info
#
# Below is the task to_do but did not add annotation as it is giving warning in pylint code analysis
# Windows does MSI?

DEB = ['debian', 'ubuntu']
RPM = ['redhat', 'fedora', 'suse', 'opensuse', 'centos']

DIST = platform.dist()[0].lower()

def read_config():
    """ Module to read config. """
    config = {}
    path = os.path.join(os.path.dirname(__file__), '..', 'config.json')
    try:
        data = open(path).read()
        config = json.loads(data)
    except IOError as _:
        pass
    return config

def get_pkg_type():
    """Module to get package type """
    if DIST in DEB:
        return "DEB"

    if DIST in RPM:
        return "RPM"

    if sys.platform == "win32":
        return "windows"

    return None

def pkg_dir():
    """Module package directory """
    system = platform.system().lower()
    machine = platform.machine().lower()
    addon = ""
    config = read_config()

    # override distribution if configuration is set
    distribution = config.get('distribution', None)
    if distribution:
        return distribution

    if system == "freebsd":
        system = system + platform.release().lower()[0]
    if system == "linux":
        platform_dist = platform.dist()

        if platform_dist[0] == 'debian':
            if platform_dist[1][0] == '6':
                platform_dist = [platform_dist[0], 'squeeze']
            elif platform_dist[1][0] == '7':
                platform_dist = [platform_dist[0], 'wheezy']
            elif platform_dist[1][0] == '8':
                platform_dist = [platform_dist[0], 'jessie']
            elif platform_dist[1][0] == '9':
                platform_dist = [platform_dist[0], 'stretch']
            # starting with 10/buster
            else:
                # use the major numerical version rather than forever maintaining mapping
                platform_dist = [platform_dist[0], platform_dist[1].split(".")[0]]
        # Lower case everything (looking at you Ubuntu)
        platform_dist = tuple([x.lower() for x in platform_dist])

        # Treat all redhat 5.* versions the same
        # redhat-5.5 becomes redhat-5
        if (platform_dist[0] == "redhat" or platform_dist[0] == "centos"):
            major = platform_dist[1].split(".")[0]
            distro = platform_dist[0]

            os_file = open('/etc/redhat-release')
            new_dist = os_file.read().lower().split(" ")[0]
            if new_dist == "rocky":
                distro = "rockylinux"
            else:
                distro = new_dist

            platform_dist = (distro, major)

        platform_dist = "%s-%s" % platform_dist[:2]
        return "%s-%s" % (platform_dist, machine)

    return "%s-%s%s" % (system, machine, addon)

def sh_cmd(cmd):
    """Module running shell commands. """
    print cmd
    res_val = subprocess.call(cmd, shell=True)
    if res_val != 0:
        print "Exit Code: %s" % (res_val)
        sys.exit(1)

def mkdir_p(path):
    """Module to make directories """
    try:
        os.makedirs(path)
    except OSError as exc:  # Python >2.5
        if exc.errno == errno.EEXIST:
            pass
        else:
            raise

def package_binary():
    """Module to get package binary """
    pkg_type = get_pkg_type()
    if pkg_type == 'windows':
        return 'virgo.msi'
    return 'rackspace-monitoring-agent'

def system_info():
    """Module to get system info"""
    # gather system, machine, and distro info
    machine = platform.machine()
    system = platform.system().lower()
    return (machine, system, pkg_dir())

def _git_describe(is_exact, git_dir, cwd):
    """Method running git commands to fetch version """
    describe = "git "
    if cwd:
        describe = "%s --git-dir=%s/.git --work-tree=%s " % (describe, git_dir, cwd)

    if is_exact:
        options = "--exact-match"
    else:
        options = "--always"

    describe = "%s describe --tags %s" % (describe, options)

    git_process = subprocess.Popen(describe,
                                   stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE,
                                   shell=True,
                                   cwd=cwd)

    version, errors = git_process.communicate()

    if errors:
        raise ValueError("The command failed:\n%s\n%s" % (describe, errors))

    return version


# git describe return "0.1-143-ga554734"
# git_describe() returns {'release': '143', 'tag': '0.1', 'hash': 'ga554734'}
def git_describe(is_exact=False, split=True, cwd=None):
    """Running git describe command """
    try:
        version = _git_describe(is_exact, cwd, cwd)
    except ValueError:
        version = ""

    if not version:
        version = _git_describe(is_exact, "..", cwd)

    version = version.strip()
    if split:
        version = version.split('-')

    return version

def git_head():
    """ Module getting git_head"""
    git_process = subprocess.Popen('git rev-parse HEAD',
                                   stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE,
                                   shell=True)
    version, _ = git_process.communicate()
    return version.strip()

def package_builder_dir():
    """returns the directory that is packaged into rpms/debs.
    This is useful because the builders maybe specifiy different cflags, etc, which
    interfere with generating symbols files."""

    pkg_type = get_pkg_type()
    base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))

    if pkg_type == 'DEB':
        build_dir_args = [base_path, 'out', 'Debug']
    elif pkg_type == 'RPM':
        git_version = git_describe()
        build_dir_args = [base_path, 'out']
        build_dir_args += ('rpmbuild', 'BUILD', "rackspace-monitoring-agent-%s" % git_version[0])
        build_dir_args += ('out', 'Debug')
    elif pkg_type == 'windows':
        build_dir_args = [base_path, 'base\\Release']
    else:
        raise AttributeError('Unsupported pkg type, %s' % (pkg_type))

    return os.path.join(*build_dir_args)

if __name__ == "__main__":
    print get_pkg_type()
