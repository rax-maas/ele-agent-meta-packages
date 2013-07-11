all:
	@python gen.py
	[ -x /bin/rpmbuild ] && rpmbuild --define '_topdir $(PWD)/' -bb SPECS/master.spec || exit 0
	[ -x /bin/rpmbuild ] && rpmbuild --define '_topdir $(PWD)/' -bb SPECS/unstable.spec || exit 0
	[ -x /bin/rpmbuild ] && rpmbuild --define '_topdir $(PWD)/' -bb SPECS/stable.spec || exit 0

.PHONY: all
