RPMBUILD = `which rpmbuild`
DPKGBUILD = `which dpkg-buildpackage`
PLATFORM = `python tools/get_platform.py`

PKG_TYPE=$(shell python tools/pkgutils.py)

all:
	@python gen.py
	@$(MAKE) $(PKG_TYPE)

rpm:
	[ -x ${RPMBUILD} ] && ${RPMBUILD} --define '_topdir $(PWD)/' -bb SPECS/master.spec || exit 0
	[ -x ${RPMBUILD} ] && ${RPMBUILD} --define '_topdir $(PWD)/' -bb SPECS/stable.spec || exit 0
	[ -x ${RPMBUILD} ] && ${RPMBUILD} --define '_topdir $(PWD)/' -bb SPECS/unstable.spec || exit 0
	@rm -rf ../rpms && mkdir -p ../rpms/${PLATFORM} && cp RPMS/noarch/* ../rpms/${PLATFORM}

deb:
	[ -x ${DPKGBUILD} ] && cd DEB/rackspace-cloud-monitoring-meta-stable-1.0 && ${DPKGBUILD} -us -uc || exit 0
	[ -x ${DPKGBUILD} ] && cd DEB/rackspace-cloud-monitoring-meta-master-1.0 && ${DPKGBUILD} -us -uc || exit 0
	[ -x ${DPKGBUILD} ] && cd DEB/rackspace-cloud-monitoring-meta-unstable-1.0 && ${DPKGBUILD} -us -uc || exit 0
	@rm -rf ../debs && mkdir -p ../debs/${PLATFORM} && cp DEB/*.deb ../debs/${PLATFORM}

.PHONY: all rpm deb
