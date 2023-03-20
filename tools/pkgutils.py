#!/usr/bin/env python
"""Package utility module to read various data """
import os
import sys
import json
import subprocess

# Figure out what type of package to build based on platform info
#
# Below is the task to_do but did not add annotation as it is giving warning in pylint code analysis
# Windows does MSI?

DEB = ['debian', 'ubuntu']
RPM = ['redhat', 'fedora', 'suse', 'opensuse', 'centos']

d = {}
with open("/etc/os-release") as f:
    for line in f:
        if line.strip() == "":
            continue
        k,v = line.lower().rstrip().split("=")
        d[k] = v.replace('"','')

DIST = d.get('name').split(" ")[0]
print(DIST + " DIST")
# In case of redhat distro, there is space in between. SO we only got red.
if DIST == "red":
    DIST = "redhat"

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
    # Using system() method to
    # execute shell commands
    #linux
    system = subprocess.check_output('uname -s', shell=True).strip().lower()
    # x86_64
    machine = subprocess.check_output('uname -m', shell=True).strip()
    version_id = d.get('version_id')
    config = read_config()
    # override distribution if configuration is set
    distribution = config.get('distribution', None)
    if distribution:
        return distribution

    if system == "freebsd":
        # 5.15.0-41-generic
        kernel_release = subprocess.check_output('uname -r', shell=True).strip()
        # 5
        system = system + kernel_release.lower()[0]

    if system == "linux":
        major_version = version_id.split(".")[0]
        platform_dist = (DIST, major_version)
        if DIST == 'debian':
            if major_version == '6':
                platform_dist = [DIST, 'squeeze']
            elif major_version == '7':
                platform_dist = [DIST, 'wheezy']
            elif major_version == '8':
                platform_dist = [DIST, 'jessie']
            elif major_version == '9':
                platform_dist = [DIST, 'stretch']
            # starting with 10/buster
            else:
                # use the major numerical version rather than forever maintaining mapping
                pass
        # Lower case everything (looking at you Ubuntu)
        platform_dist = tuple([x.lower() for x in platform_dist])

        # Treat all redhat 5.* versions the same
        # redhat-5.5 becomes redhat-5
        if (DIST == "redhat" or DIST == "centos"):
            major = version_id.split(".")[0]
            platform_dist = (DIST, major)

        platform_dist = "%s-%s" % platform_dist[:2]
        return "%s-%s" % (platform_dist, machine)

    return "%s-%s%s" % (system, machine, "")


def sh_cmd(cmd):
    """Module running shell commands. """
    print(cmd)
    res_val = subprocess.call(cmd, shell=True)
    if res_val != 0:
        print("Exit Code: %s" % (res_val))
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
    print(get_pkg_type())
