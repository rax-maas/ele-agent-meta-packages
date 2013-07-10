all:
	@python gen.py
	rpmbuild --define '_topdir $(PWD)/' -bb SPECS/master.spec
	rpmbuild --define '_topdir $(PWD)/' -bb SPECS/unstable.spec
	rpmbuild --define '_topdir $(PWD)/' -bb SPECS/stable.spec

.PHONY: all
