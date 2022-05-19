#
# Conditional build:
%bcond_without	python2	# CPython 2.x module
%bcond_without	python3	# CPython 3.x module

Summary:	iSCSI - SCSI over IP
Summary(pl.UTF-8):	iSCSI - SCSI po IP
Name:		open-iscsi
Version:	2.1.7
Release:	1
License:	GPL v2
Group:		Networking/Daemons
#Source0Download: https://github.com/open-iscsi/open-iscsi/releases
Source0:	https://github.com/open-iscsi/open-iscsi/archive/%{version}/%{name}-%{version}.tar.gz
# Source0-md5:	87f37b0968ff91ed0253d53d497da4cb
Source1:	%{name}.init
Source2:	%{name}.sysconfig
Source3:	%{name}-devices.init
Source4:	iscsiuio.logrotate
# Fedora patches
Patch1:		0001-unit-file-tweaks.patch
# idmb_rec_write refactoring skipped, see 75c46b011d7485a4b5676d824c7f3cdea2076f49
Patch5:		0005-update-initscripts-and-docs.patch
# use-var-for-config, use-red-hat-for-name skipped
Patch8:		0008-libiscsi.patch
Patch9:		0009-Add-macros-to-release-GIL-lock.patch
Patch10:	0010-libiscsi-introduce-sessions-API.patch
Patch11:	0011-libiscsi-fix-discovery-request-timeout-regression.patch
Patch12:	0012-libiscsi-format-security-build-errors.patch
Patch13:	0013-libiscsi-fix-build-to-use-libopeniscsiusr.patch
Patch14:	0014-libiscsi-fix-build-against-latest-upstream-again.patch
Patch15:	0015-remove-the-offload-boot-supported-ifdef.patch
Patch16:	0016-Revert-iscsiadm-return-error-when-login-fails.patch
# dont-install-scripts, use-var-lib-iscsi-in-libopeniscsiusr skipped
Patch19:	0019-Coverity-scan-fixes.patch
# fix-upstream-build-breakage-of-iscsiuio-LDFLAGS obsolete in 2.1.7
# use-Red-Hat-version-string-to-match-RPM-package-vers skipped
Patch22:	0022-iscsi_if.h-replace-zero-length-array-with-flexible-a.patch
Patch23:	0023-stop-using-Werror-for-now.patch
Patch24:	0024-minor-service-file-updates.patch
# Remove-dependences-from-iscsi-init.service obsolete in 2.1.7
# PLD specific
Patch100:	%{name}-systemd.patch
Patch101:	%{name}-libiscsi.patch
URL:		https://www.open-iscsi.com/
BuildRequires:	kmod-devel
BuildRequires:	open-isns-devel
BuildRequires:	openssl-devel
%{?with_python2:BuildRequires:	python-devel >= 1:2.5}
%{?with_python3:BuildRequires:	python3-devel >= 1:3.2}
BuildRequires:	rpm-pythonprov
BuildRequires:	rpmbuild(macros) >= 1.714
Requires(post,preun):	/sbin/chkconfig
Requires(post,preun,postun):	systemd-units >= 38
Requires:	%{name}-libs = %{version}-%{release}
Requires:	rc-scripts
Requires:	systemd-units >= 38
Suggests:	multipath-tools
Provides:	group(iscsi)
Provides:	user(iscsi)
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%define		_sbindir	/sbin

%description
The Linux iSCSI driver acts as an iSCSI protocol initiator to
transport SCSI requests and responses over an IP network between the
client and an iSCSI-enabled target device such as a Cisco SN 5420
storage router. The iSCSI protocol is an IETF-defined protocol for IP
storage. For more information about the iSCSI protocol, refer to the
IETF standards for IP storage at <http://www.ietf.org/>.

%description -l pl.UTF-8
Sterownik Linux iSCSI zachowuje się jak inicjator protokołu iSCSI do
transportu zleceń SCSI i odpowiedzi po sieci IP między klientem a
urządzeniem docelowym obsługującym iSCSI, takim jak Cisco SN 5420.
Protokół iSCSI jest zdefiniowany przez IETF do składowania IP. Więcej
informacji o protokole iSCSI znajduje się w standardach IETF na
<http://www.ietf.org/>.

%package libs
Summary:	Open-iSCSI shared libraries
Summary(pl.UTF-8):	Biblioteki współdzielone Open-iSCSI
Group:		Libraries

%description libs
Open-iSCSI shared libraries.

%description libs -l pl.UTF-8
Biblioteki współdzielone Open-iSCSI.

%package devel
Summary:	Header files for Open-iSCSI libraries
Summary(pl.UTF-8):	Pliki nagłówkowe bibliotek Open-iSCSI
Group:		Development/Libraries
Requires:	%{name}-libs = %{version}-%{release}

%description devel
Header files for Open-iSCSI libraries.

%description devel -l pl.UTF-8
Pliki nagłówkowe bibliotek Open-iSCSI.

%package -n python-pyiscsi
Summary:	Python 2 interface to Open-iSCSI library
Summary(pl.UTF-8):	Interfejs Pythona 2 do biblioteki Open-iSCSI
Group:		Libraries/Python
Requires:	%{name}-libs = %{version}-%{release}

%description -n python-pyiscsi
Python 2 interface to Open-iSCSI library.

%description -n python-pyiscsi -l pl.UTF-8
Interfejs Pythona 2 do biblioteki Open-iSCSI.

%package -n python3-pyiscsi
Summary:	Python 3 interface to Open-iSCSI library
Summary(pl.UTF-8):	Interfejs Pythona 3 do biblioteki Open-iSCSI
Group:		Libraries/Python
Requires:	%{name}-libs = %{version}-%{release}

%description -n python3-pyiscsi
Python 3 interface to Open-iSCSI library.

%description -n python3-pyiscsi -l pl.UTF-8
Interfejs Pythona 3 do biblioteki Open-iSCSI.

%prep
%setup -q
%patch1 -p1
%patch5 -p1
%patch8 -p1
%patch9 -p1
%patch10 -p1
%patch11 -p1
%patch12 -p1
%patch13 -p1
%patch14 -p1
%patch15 -p1
%patch16 -p1
%patch19 -p1
%patch22 -p1
%patch23 -p1
%patch24 -p1
%patch100 -p1
%patch101 -p1

%build
cd iscsiuio
%{__libtoolize}
%{__aclocal}
%{__autoconf}
%{__autoheader}
%{__automake}
%configure
cd ..

%{__make} \
	CC="%{__cc}" \
	OPTFLAGS="%{rpmcflags} %{rpmcppflags}" \
	SED=sed \
	KSUBLEVEL=0

cd libiscsi
%if %{with python2}
%py_build
%endif
%if %{with python3}
%py3_build
%endif

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT%{_sysconfdir}/iscsi/{nodes,send_targets,static,isns,slp,ifaces} \
	$RPM_BUILD_ROOT/etc/{rc.d/init.d,sysconfig,logrotate.d} \
	$RPM_BUILD_ROOT%{systemdunitdir} \
	$RPM_BUILD_ROOT{/sbin,/lib/systemd/pld-helpers.d}

%{__make} -j1 install_programs install_doc install_etc install_libopeniscsiusr install_iscsiuio \
	DESTDIR=$RPM_BUILD_ROOT \
	LIB_DIR=%{_libdir} \
	RULESDIR=/lib/udev/rules.d

:> $RPM_BUILD_ROOT%{_sysconfdir}/iscsi/initiatorname.iscsi

install %{SOURCE1} $RPM_BUILD_ROOT/etc/rc.d/init.d/iscsid
cp -p %{SOURCE2} $RPM_BUILD_ROOT/etc/sysconfig/iscsi
install %{SOURCE3} $RPM_BUILD_ROOT/etc/rc.d/init.d/iscsi
# or use upstream file instead?
cp -p %{SOURCE4} $RPM_BUILD_ROOT/etc/logrotate.d/iscsiuio
%{__rm} $RPM_BUILD_ROOT/etc/logrotate.d/iscsiuiolog

install usr/iscsistart $RPM_BUILD_ROOT%{_sbindir}
cp -p doc/iscsistart.8 $RPM_BUILD_ROOT%{_mandir}/man8
#install doc/iscsi-iname.8 $RPM_BUILD_ROOT%{_mandir}/man8

cp -p etc/systemd/iscsi.service $RPM_BUILD_ROOT%{systemdunitdir}
cp -p etc/systemd/iscsi-init.service $RPM_BUILD_ROOT%{systemdunitdir}
cp -p etc/systemd/iscsi-onboot.service $RPM_BUILD_ROOT%{systemdunitdir}
cp -p etc/systemd/iscsi-shutdown.service $RPM_BUILD_ROOT%{systemdunitdir}
cp -p etc/systemd/iscsid.service $RPM_BUILD_ROOT%{systemdunitdir}
cp -p etc/systemd/iscsid.socket $RPM_BUILD_ROOT%{systemdunitdir}
cp -p etc/systemd/iscsiuio.service $RPM_BUILD_ROOT%{systemdunitdir}
cp -p etc/systemd/iscsiuio.socket $RPM_BUILD_ROOT%{systemdunitdir}

install etc/systemd/iscsi-mark-root-nodes $RPM_BUILD_ROOT/lib/systemd/pld-helpers.d

# rename to resolve conflict with already existing libiscsi from libiscsi.spec
install -p libiscsi/libopeniscsi.so.0 $RPM_BUILD_ROOT%{_libdir}
ln -sf libopeniscsi.so.0 $RPM_BUILD_ROOT%{_libdir}/libopeniscsi.so
cp -p libiscsi/libiscsi.h $RPM_BUILD_ROOT%{_includedir}/libopeniscsi.h

cd libiscsi
%if %{with python2}
%py_install
%endif
%if %{with python3}
%py3_install
%endif

%clean
rm -rf $RPM_BUILD_ROOT

%pre
%groupadd -g 223 iscsi
%useradd -u 223 -d /tmp -s /bin/false -c "iSCSI Daemon" -g iscsi iscsi

%post
if ! grep -q "^InitiatorName=[^ \t\n]" %{_sysconfdir}/iscsi/initiatorname.iscsi 2>/dev/null; then
	echo "InitiatorName=$(iscsi-iname)" >> %{_sysconfdir}/iscsi/initiatorname.iscsi
fi
/sbin/chkconfig --add iscsi
/sbin/chkconfig --add iscsid
NORESTART=1
%systemd_post iscsi.service iscsid.service iscsiuio.service iscsid.socket iscsiuio.socket iscsi-onboot.service iscsi-init.service iscsi-shutdown.service

%preun
if [ "$1" = "0" ]; then
	%service iscsid stop
	%service iscsi stop
	/sbin/chkconfig --del iscsid
	/sbin/chkconfig --del iscsi
fi
%systemd_preun iscsi.service iscsid.service iscsiuio.service iscsid.socket iscsiuio.socket iscsi-onboot.service iscsi-init.service iscsi-shutdown.service

%postun
if [ "$1" = "0" ]; then
	%userremove iscsi
	%groupremove iscsi
fi
%systemd_reload

%triggerpostun -- %{name} < 2.0.873-1
%systemd_trigger iscsi.service iscsid.service iscsiuio.service
/bin/systemctl --quiet enable iscsid.socket || :
/bin/systemctl --quiet enable iscsiuio.socket || :

%post	libs -p /sbin/ldconfig
%postun	libs -p /sbin/ldconfig

%files
%defattr(644,root,root,755)
%doc Changelog README THANKS TODO
%dir %{_sysconfdir}/iscsi
%dir %{_sysconfdir}/iscsi/ifaces
%dir %{_sysconfdir}/iscsi/isns
%dir %{_sysconfdir}/iscsi/nodes
%dir %{_sysconfdir}/iscsi/send_targets
%dir %{_sysconfdir}/iscsi/slp
%dir %{_sysconfdir}/iscsi/static
%config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/iscsi/iscsid.conf
%config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/iscsi/initiatorname.iscsi
%attr(640,root,root) %config(noreplace) %verify(not md5 mtime size) /etc/sysconfig/iscsi
%attr(640,root,root) %config(noreplace) %verify(not md5 mtime size) /etc/logrotate.d/iscsiuio
%attr(754,root,root) /etc/rc.d/init.d/iscsi
%attr(754,root,root) /etc/rc.d/init.d/iscsid
/lib/udev/rules.d/50-iscsi-firmware-login.rules
%{systemdunitdir}/iscsi.service
%{systemdunitdir}/iscsi-init.service
%{systemdunitdir}/iscsi-onboot.service
%{systemdunitdir}/iscsi-shutdown.service
%{systemdunitdir}/iscsid.service
%{systemdunitdir}/iscsid.socket
%{systemdunitdir}/iscsiuio.service
%{systemdunitdir}/iscsiuio.socket
%attr(755,root,root) /lib/systemd/pld-helpers.d/iscsi-mark-root-nodes
%attr(755,root,root) %{_sbindir}/brcm_iscsiuio
%attr(755,root,root) %{_sbindir}/iscsi-gen-initiatorname
%attr(755,root,root) %{_sbindir}/iscsi-iname
%attr(755,root,root) %{_sbindir}/iscsi_discovery
%attr(755,root,root) %{_sbindir}/iscsi_fw_login
%attr(755,root,root) %{_sbindir}/iscsi_offload
%attr(755,root,root) %{_sbindir}/iscsiadm
%attr(755,root,root) %{_sbindir}/iscsid
%attr(755,root,root) %{_sbindir}/iscsistart
%attr(755,root,root) %{_sbindir}/iscsiuio
%{_mandir}/man8/iscsi-gen-initiatorname.8*
%{_mandir}/man8/iscsi-iname.8*
%{_mandir}/man8/iscsi_discovery.8*
%{_mandir}/man8/iscsi_fw_login.8*
%{_mandir}/man8/iscsiadm.8*
%{_mandir}/man8/iscsid.8*
%{_mandir}/man8/iscsistart.8*
%{_mandir}/man8/iscsiuio.8*

%files libs
%defattr(644,root,root,755)
%attr(755,root,root) %{_libdir}/libopeniscsi.so.0
%attr(755,root,root) %{_libdir}/libopeniscsiusr.so.*.*.*
%attr(755,root,root) %ghost %{_libdir}/libopeniscsiusr.so.0

%files devel
%defattr(644,root,root,755)
%attr(755,root,root) %{_libdir}/libopeniscsi.so
%attr(755,root,root) %{_libdir}/libopeniscsiusr.so
%{_includedir}/libopeniscsi.h
%{_includedir}/libopeniscsiusr*.h
%{_pkgconfigdir}/libopeniscsiusr.pc
%{_mandir}/man3/iscsi_*.3*
%{_mandir}/man3/libopeniscsiusr.h.3*

%if %{with python2}
%files -n python-pyiscsi
%defattr(644,root,root,755)
%attr(755,root,root) %{py_sitedir}/libiscsi.so
%{py_sitedir}/PyIscsi-1.0-py*.egg-info
%endif

%if %{with python3}
%files -n python3-pyiscsi
%defattr(644,root,root,755)
%attr(755,root,root) %{py3_sitedir}/libiscsi.cpython-*.so
%{py3_sitedir}/PyIscsi-1.0-py*.egg-info
%endif
