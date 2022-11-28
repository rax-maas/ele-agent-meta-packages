#!/usr/bin/env python

from optparse import OptionParser
from pkgutils import git_describe
from os.path import exists as file_exists

# Generate versions for RPM/dpkg without dashes from git describe
# make release 0 if tag matches exactly
# PKG_VERLIST = $(filter-out dirty,$(subst -, ,$(VERSION))) 0
# PKG_VERSION = $(word 1,$(PKG_VERLIST))
# PKG_RELEASE = $(word 2,$(PKG_VERLIST))

# Below code is commented out because whatever the output of this file is used as meta version and it makes it redundant. 
# We kept this code because if later we need to identify the name of machine, we can simply uncomment the code and get the details.
# Output contents of /etc/os-release file
# If no file exists, output that so that we can make changes in future accordingly.
#if file_exists('/etc/os-release'):
#    with open('/etc/os-release', 'r') as f:
#        print('/etc/os-release file contains:')
#        print(f.read())
#        print('=========================')
#else:
#    print('/etc/os-release file does not exist')

# If there is no release then it is zero
def zero_release(version):
    if len(version) == 1:
        version.append("0")
        return version

    return version


def git_describe_fields(version):
    fields = ["tag", "release", "hash", "major", "minor", "patch"]
    version.extend(version[0].split('.'))
    return dict(zip(fields, version))


def version(sep='-', cwd=None):
    # import pdb; pdb.set_trace()
    version = git_describe(is_exact=False, split=True, cwd=cwd)
    zeroed = zero_release(version)
    fields = git_describe_fields(zeroed)

    if sep:
        return sep.join(zeroed[:2])

    return fields


def full_version(sep='-', cwd=None):
    return version(sep, cwd)


if __name__ == "__main__":


# Below all code comment out because earlier we are getting meta version by running the git describe on version and it was returning different version if someone had made any commit because it increate the no in version. If we get a new version, we new to run build for every buildslave because we need build for every agent on that version and doing so is hard thing because most of the agents are offline.
# So we decided to go with a static meta version which is defined in file config.txt

    # reading the data from the file
    with open('config.txt') as f:
        data = f.read()

    # reconstructing the data as a dictionary
    js = json.loads(data)
    print(js['META_VERSION'])

#    usage = "usage: %prog [field] [--sep=.]"
#    parser = OptionParser(usage=usage)
#    parser.add_option("-s", "--seperator", dest="seperator", default=None, help="version seperator")
#    parser.add_option("-d", "--directory", dest="directory", default=None, help="path to directory ")
#    (options, args) = parser.parse_args()

#    v = version(options.seperator, options.directory)
#    if v['tag'] and v['release']:
#        print("%s-%s" % (v['tag'], v['release']))
#    else:
#        print("%s" % (v['hash']))
