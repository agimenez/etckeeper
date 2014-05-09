# You should configure etckeeper.conf for your distribution before
# installing etckeeper.
CONFFILE=etckeeper.conf
include $(CONFFILE)

DESTDIR?=
prefix=/usr
bindir=${prefix}/bin
etcdir=/etc
mandir=${prefix}/share/man
vardir=/var
CP=cp -R
INSTALL=install 
INSTALL_EXE=${INSTALL}
INSTALL_DATA=${INSTALL} -m 0644

build: etckeeper.spec
	-./etckeeper-bzr/__init__.py build || echo "** bzr support not built"

install:
	mkdir -p $(DESTDIR)$(etcdir)/etckeeper/ $(DESTDIR)$(vardir)/cache/etckeeper/
	$(CP) *.d $(DESTDIR)$(etcdir)/etckeeper/
	$(INSTALL_DATA) $(CONFFILE) $(DESTDIR)$(etcdir)/etckeeper/etckeeper.conf
	mkdir -p $(DESTDIR)$(bindir)
	$(INSTALL_EXE) etckeeper $(DESTDIR)$(bindir)/etckeeper
	mkdir -p $(DESTDIR)$(mandir)/man8
	$(INSTALL_DATA) etckeeper.8 $(DESTDIR)$(mandir)/man8/etckeeper.8
	mkdir -p $(DESTDIR)$(etcdir)/bash_completion.d
	$(INSTALL_DATA) bash_completion $(DESTDIR)$(etcdir)/bash_completion.d/etckeeper
ifeq ($(HIGHLEVEL_PACKAGE_MANAGER),apt)
	mkdir -p $(DESTDIR)$(etcdir)/apt/apt.conf.d
	$(INSTALL_DATA) apt.conf $(DESTDIR)$(etcdir)/apt/apt.conf.d/05etckeeper
	mkdir -p $(DESTDIR)$(etcdir)/cruft/filters-unex
	$(INSTALL_DATA) cruft_filter $(DESTDIR)$(etcdir)/cruft/filters-unex/etckeeper
endif
ifeq ($(LOWLEVEL_PACKAGE_MANAGER),pacman-g2)
	mkdir -p $(DESTDIR)$(etcdir)/pacman-g2/hooks
	$(INSTALL_DATA) pacman-g2.hook $(DESTDIR)$(etcdir)/pacman-g2/hooks/etckeeper
endif
ifeq ($(HIGHLEVEL_PACKAGE_MANAGER),yum)
	mkdir -p $(DESTDIR)$(prefix)/lib/yum-plugins
	$(INSTALL_DATA) yum-etckeeper.py $(DESTDIR)$(prefix)/lib/yum-plugins/etckeeper.py
	mkdir -p $(DESTDIR)$(etcdir)/yum/pluginconf.d
	$(INSTALL_DATA) yum-etckeeper.conf $(DESTDIR)$(etcdir)/yum/pluginconf.d/etckeeper.conf
endif
ifeq ($(HIGHLEVEL_PACKAGE_MANAGER),zypper)
	mkdir -p $(DESTDIR)$(prefix)/lib/zypp/plugins/commit
	$(INSTALL_DATA) zypper-etckeeper.py $(DESTDIR)$(prefix)/lib/zypp/plugins/commit/zypper-etckeeper.py
endif
	-./etckeeper-bzr/__init__.py install --root=$(DESTDIR) ${PYTHON_INSTALL_OPTS} || echo "** bzr support not installed"
	echo "** installation successful"

clean: etckeeper.spec
	rm -rf build

etckeeper.spec:
	sed -i~ "s/Version:.*/Version: $$(perl -e '$$_=<>;print m/\((.*?)\)/'<debian/changelog)/" etckeeper.spec
	rm -f etckeeper.spec~

.PHONY: etckeeper.spec
