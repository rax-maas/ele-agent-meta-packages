RPMBUILD = `which rpmbuild`
PLATFORM = `python tools/get_platform.py`

all:
	@python gen.py
	[ -x ${RPMBUILD} ] && ${RPMBUILD} --define '_topdir $(PWD)/' -bb SPECS/master.spec || exit 0
	[ -x ${RPMBUILD} ] && ${RPMBUILD} --define '_topdir $(PWD)/' -bb SPECS/unstable.spec || exit 0
	[ -x ${RPMBUILD} ] && ${RPMBUILD} --define '_topdir $(PWD)/' -bb SPECS/stable.spec || exit 0
	@rm -rf ../rpms && mkdir -p ../rpms/${PLATFORM} && cp RPMS/noarch/* ../rpms/${PLATFORM}

.PHONY: all
