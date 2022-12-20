RPMBUILD = `which rpmbuild`
DPKGBUILD = `which dpkg-buildpackage`
PLATFORM = `python tools/get_platform.py`

PKG_TYPE=$(shell python tools/pkgutils.py)
DESTDIR=../payload
PYTHON=python

all:
	@rm -f config.json
ifdef DISTRIBUTION
	@$(PYTHON) gen.py --distribution=${DISTRIBUTION}
else
	@$(PYTHON) gen.py
endif
	@$(MAKE) $(PKG_TYPE)

RPM:
	[ -x ${RPMBUILD} ] && ${RPMBUILD} --define '_topdir $(PWD)/' -bb SPECS/master.spec || exit 0
	[ -x ${RPMBUILD} ] && ${RPMBUILD} --define '_topdir $(PWD)/' -bb SPECS/stable.spec || exit 0
	[ -x ${RPMBUILD} ] && ${RPMBUILD} --define '_topdir $(PWD)/' -bb SPECS/unstable.spec || exit 0
	@rm -rf ${DESTDIR} && mkdir -p ${DESTDIR}/${PLATFORM} && cp RPMS/noarch/* ${DESTDIR}/${PLATFORM}

DEB:
	[ -x ${DPKGBUILD} ] && cd DEB/rackspace-cloud-monitoring-meta-stable-1.0 && ${DPKGBUILD} -us -uc || exit 0
	[ -x ${DPKGBUILD} ] && cd DEB/rackspace-cloud-monitoring-meta-master-1.0 && ${DPKGBUILD} -us -uc || exit 0
	[ -x ${DPKGBUILD} ] && cd DEB/rackspace-cloud-monitoring-meta-unstable-1.0 && ${DPKGBUILD} -us -uc || exit 0
	@rm -rf ${DESTDIR} && mkdir -p ${DESTDIR}/${PLATFORM} && cp DEB/*.deb ${DESTDIR}/${PLATFORM}

.PHONY: all RPM DEB
