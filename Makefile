RPMBUILD = `which rpmbuild`

all:
	@python gen.py
	[ -x ${RPMBUILD} ] && ${RPMBUILD} --define '_topdir $(PWD)/' -bb SPECS/master.spec || exit 0
	[ -x ${RPMBUILD} ] && ${RPMBUILD} --define '_topdir $(PWD)/' -bb SPECS/unstable.spec || exit 0
	[ -x ${RPMBUILD} ] && ${RPMBUILD} --define '_topdir $(PWD)/' -bb SPECS/stable.spec || exit 0
	@rm -rf ../rpms && mkdir -p ../rpms && cp RPMS/noarch/* ../rpms

.PHONY: all
