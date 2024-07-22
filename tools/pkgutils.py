#!/usr/bin/env python
# pylint: disable=invalid-name
"""Package utility module to read various data """
import os
import errno
import platform
import sys
import json
import subprocess
import distro

# Figure out what type of package to build based on platform info
#
# Below is the task to_do but did not add annotation as it is giving warning in pylint code analysis
# Windows does MSI?

DEB = ['debian', 'ubuntu']
RPM = ['redhat', 'fedora', 'suse', 'opensuse', 'centos', 'rocky', 'almalinux']

DIST = distro.id().lower()
DIST_VERSION = distro.version()

def read_config():
    """ Module to read config. """
    config = {}
    path = os.path.join(os.path.dirname(__file__), '..', 'config.json')
    try:
        with open(path, 'r', encoding='utf-8') as data:
            config = json.loads(data.read())
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
        dist_major_version = DIST_VERSION.split(".")[0]
        platform_dist = (DIST, DIST_VERSION)

        if DIST == 'debian':
            if dist_major_version == '6':
                platform_dist = [DIST, 'squeeze']
            elif dist_major_version == '7':
                platform_dist = [DIST, 'wheezy']
            elif dist_major_version == '8':
                platform_dist = [DIST, 'jessie']
            elif dist_major_version == '9':
                platform_dist = [DIST, 'stretch']
            # starting with 10/buster
            else:
                # use the major numerical version rather than forever maintaining mapping
                platform_dist = [DIST, dist_major_version]
        # Lower case everything (looking at you Ubuntu)
        # pylint: disable=consider-using-generator
        platform_dist = tuple([x.lower() for x in platform_dist])

        # Treat all redhat 5.* versions the same
        # redhat-5.5 becomes redhat-5
        if DIST in ('redhat', 'centos', 'rocky', 'almalinux'):
            with open('/etc/redhat-release', 'r', encoding='utf-8') as os_file:
                new_dist = os_file.read().lower().split(" ")[0]
                if new_dist == "rocky":
                    dist_name = "rockylinux"
                else:
                    dist_name = new_dist
                platform_dist = (dist_name, dist_major_version)

        # pylint: disable=consider-using-f-string
        platform_dist = "%s-%s" % platform_dist
        return f"{platform_dist}-{machine}"

    return f"{system}-{machine}{addon}"

def sh_cmd(cmd):
    """Module running shell commands. """
    print(cmd)
    res_val = subprocess.call(cmd, shell=True)
    if res_val != 0:
        print(f"Exit Code: {res_val}")
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
        describe = f"{describe} --git-dir={git_dir}/.git --work-tree={cwd} "

    if is_exact:
        options = "--exact-match"
    else:
        options = "--always"

    describe = f"{describe} describe --tags {options}"

    with subprocess.Popen(describe,
                          stdout=subprocess.PIPE,
                          stderr=subprocess.PIPE,
                          shell=True,
                          cwd=cwd) as git_process:

        version, errors = git_process.communicate()

        if errors:
            raise ValueError(f"The command failed:\n{describe}\n{errors}")

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
    with subprocess.Popen(['git', 'rev-parse', 'HEAD'],
                          stdout=subprocess.PIPE,
                          stderr=subprocess.PIPE,
                          shell=True) as git_process:

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
        build_dir_args += ('rpmbuild', 'BUILD', f"rackspace-monitoring-agent-{git_version[0]}")
        build_dir_args += ('out', 'Debug')
    elif pkg_type == 'windows':
        build_dir_args = [base_path, 'base\\Release']
    else:
        raise AttributeError(f'Unsupported pkg type, {pkg_type}')

    return os.path.join(*build_dir_args)

if __name__ == "__main__":
    print(f"{get_pkg_type()}")
