"""Updates the compat level and control file by running shell command"""
import os
import sys

def update_compat_level_and_control_file():
    """Updates the compat level to the value provided in argument and
    also updates Build Depends property for control file"""
    compat_level = sys.argv[1]
    update_compat_level_command = "for d in DEB/*/ ; do (cd ""$d"" && echo "+ \
        compat_level+" > debian/compat); done"
    build_depends = "debhelper (>= " + compat_level + "~)"
    update_control_file = "for d in DEB/*/ ; do (cd ""$d"" && sed -i 's/debhelper (>= 5~)/" + \
        build_depends + "/g' debian/control); done"
    os.system(update_compat_level_command)
    os.system(update_control_file)

if __name__ == '__main__':
    update_compat_level_and_control_file()
