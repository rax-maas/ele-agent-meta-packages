"""Updates the compat level by running shell command"""

import os
import sys

def update_compat_level():
    """Updates the compat level to the value provided in argument"""
    compat_level = sys.argv[1]
    command_to_execute = "for d in DEB/*/ ; do (cd ""$d"" && echo "+ \
        compat_level+" > debian/compat); done"
    os.system(command_to_execute)

if __name__ == '__main__':
    update_compat_level()
