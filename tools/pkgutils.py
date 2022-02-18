#!/usr/bin/env python
import os
import errno
import platform
import sys
import json
import subprocess

# Figure out what type of package to build based on platform info
#
# TODO: Windows does MSI?

deb = ['debian', 'ubuntu']
rpm = ['redhat', 'fedora', 'suse', 'opensuse', 'centos']

dist = platform.dist()[0].lower()

def read_config():
    config = {}
    path = os.path.join(os.path.dirname(__file__), '..', 'config.json')
    try:
        data = open(path).read()
        config = json.loads(data)
    except:
        pass
    return config


def pkg_type():
    if dist in deb:
        return "deb"

    if dist in rpm:
        return "rpm"

    if sys.platform == "win32":
        return "windows"

    return None


def pkg_dir():
    system = platform.system().lower()
    machine = platform.machine().lower()
    addon = ""
    config = read_config()

    # override distribution if configuration is set
    distribution= config.get('distribution', None)
    if distribution:
        return distribution

    if system == "freebsd":
        system = system + platform.release().lower()[0]
    if system == "linux":
        dist = platform.dist()

        if dist[0] == 'debian':
            if dist[1][0] == '6':
                dist = [dist[0], 'squeeze']
            elif dist[1][0] == '7':
                dist = [dist[0], 'wheezy']
            elif dist[1][0] == '8':
                dist = [dist[0], 'jessie']
            elif dist[1][0] == '9':
                dist = [dist[0], 'stretch']
            # starting with 10/buster
            else:
                # use the major numerical version rather than forever maintaining mapping
                dist = [dist[0], dist[1].split(".")[0]]
        # Lower case everything (looking at you Ubuntu)
        dist = tuple([x.lower() for x in dist])

        # Treat all redhat 5.* versions the same
        # redhat-5.5 becomes redhat-5
        if (dist[0] == "redhat" or dist[0] == "centos"):
            major = dist[1].split(".")[0]
            distro = dist[0]

            f = open('/etc/redhat-release')
            new_dist = f.read().lower().split(" ")[0]
            if new_dist == "rocky":
                distro = "rockylinux"
    	    else:
	            distro = new_dist

            dist = (distro, major)

        dist = "%s-%s" % dist[:2]
        return "%s-%s" % (dist, machine)

    return "%s-%s%s" % (system, machine, addon)


def sh(cmd):
    print cmd
    rv = subprocess.call(cmd, shell=True)
    if rv != 0:
        print "Exit Code: %s" % (rv)
        sys.exit(1)


def mkdir_p(path):
    try:
        os.makedirs(path)
    except OSError as exc:  # Python >2.5
        if exc.errno == errno.EEXIST:
            pass
        else:
            raise


def package_binary():
    pkgType = pkg_type()
    if pkgType == 'windows':
        return 'virgo.msi'
    return 'rackspace-monitoring-agent'


def system_info():
    # gather system, machine, and distro info
    machine = platform.machine()
    system = platform.system().lower()
    return (machine, system, pkg_dir())


def _git_describe(is_exact, git_dir, cwd):
    describe = "git "
    if cwd:
        describe = "%s --git-dir=%s/.git --work-tree=%s " % (describe, git_dir, cwd)

    if is_exact:
        options = "--exact-match"
    else:
        options = "--always"

    describe = "%s describe --tags %s" % (describe, options)

    p = subprocess.Popen(describe,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            shell=True,
            cwd=cwd)

    version, errors = p.communicate()

    if errors:
        raise ValueError("The command failed:\n%s\n%s" % (describe, errors))

    return version


# git describe return "0.1-143-ga554734"
# git_describe() returns {'release': '143', 'tag': '0.1', 'hash': 'ga554734'}
def git_describe(is_exact=False, split=True, cwd=None):

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
    p = subprocess.Popen('git rev-parse HEAD',
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        shell=True)
    version, errors = p.communicate()
    return version.strip()


def package_builder_dir():
    """returns the directory that is packaged into rpms/debs.
    This is useful because the builders maybe specifiy different cflags, etc, which
    interfere with generating symbols files."""

    pkgType = pkg_type()
    basePath = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))

    if pkgType == 'deb':
        buildDirArgs = [basePath, 'out', 'Debug']
    elif pkgType == 'rpm':
        v = git_describe()
        buildDirArgs = [basePath, 'out']
        buildDirArgs += ('rpmbuild', 'BUILD', "rackspace-monitoring-agent-%s" % v[0])
        buildDirArgs += ('out', 'Debug')
    elif pkgType == 'windows':
        buildDirArgs = [basePath, 'base\\Release']
    else:
        raise AttributeError('Unsupported pkg type, %s' % (pkgType))

    return os.path.join(*buildDirArgs)

if __name__ == "__main__":
    print pkg_type()
