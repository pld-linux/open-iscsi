# Conditional build:
%bcond_without	dynamic		# link utilities dynamically
#
%define		ver	2.0
%define		subver	873
Summary:	iSCSI - SCSI over IP
Summary(pl.UTF-8):	iSCSI - SCSI po IP
Name:		open-iscsi
Version:	%{ver}.%{subver}
Release:	2
License:	GPL v2
Group:		Networking/Daemons
Source0:	http://www.open-iscsi.org/bits/%{name}-%{ver}-%{subver}.tar.gz
# Source0-md5:	8b8316d7c9469149a6cc6234478347f7
Source1:	%{name}.init
Source2:	%{name}.sysconfig
Source3:	%{name}-devices.init
Source4:	iscsiuio.logrotate
Patch0:		%{name}-git.patch
Patch1:		%{name}-build.patch
Patch2:		%{name}-systemd.patch
Patch31:	0043-idmb_rec_write-check-for-tpgt-first.patch
Patch32:	0044-iscsid-add-initrd-option-to-set-run-from-initrd-hint.patch
Patch33:	0045-idbm_rec_write-seperate-old-and-new-style-writes.patch
Patch34:	0046-idbw_rec_write-pick-tpgt-from-existing-record.patch
Patch35:	0047-iscsiadm-iscsid-newroot-command-to-survive-switch_ro.patch
Patch36:	0047-iscsiuio-systemd-socket-activation-support.patch
Patch37:	0048-iscsiadm-param-parsing-for-advanced-node-creation.patch
Patch38:	0049-update-systemd-service-files-add-iscsi.service-for-s.patch
Patch39:	0050-iscsi-boot-related-service-file-updates.patch
Patch40:	0058-iscsiuio-IPC-newroot-command.patch
Patch41:	0059-iscsiuio-systemd-unit-files.patch
Patch42:	0062-Don-t-check-for-autostart-sessions-if-iscsi-is-not-u.patch
Patch43:	0063-fix-order-of-setting-uid-gid-and-drop-supplementary-.patch
Patch44:	0065-fix-hardened-build-of-iscsiuio.patch
Patch45:	0066-start-socket-listeners-on-iscsiadm-command.patch
URL:		http://www.open-iscsi.org/
BuildRequires:	kmod-devel
BuildRequires:	openssl-devel
BuildRequires:	rpmbuild(macros) >= 1.671
%if %{with dynamic}
BuildRequires:	openslp-devel
BuildRequires:	sed >= 4.0
Requires:	openslp >= 2.0.0
%else
BuildRequires:	glibc-static
BuildRequires:	openslp-static
%endif
Requires(post,preun):	/sbin/chkconfig
Requires(post,preun,postun):	systemd-units >= 38
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

%prep
%setup -q -n %{name}-%{ver}-%{subver}
%patch0 -p1
%patch31 -p1
%patch32 -p1
%patch33 -p1
%patch34 -p1
%patch35 -p1
%patch36 -p1
%patch37 -p1
%patch38 -p1
%patch39 -p1
%patch40 -p1
%patch41 -p1
%patch42 -p1
%patch43 -p1
%patch44 -p1
%patch45 -p1
%patch1 -p1
%patch2 -p1

%if %{with dynamic}
sed -i -e 's/-static //' usr/Makefile
%endif

%build
cd iscsiuio
%{__libtoolize}
%{__aclocal}
%{__autoconf}
%{__autoheader}
%{__automake}
%configure

cd ../utils/open-isns
%configure \
	--with-slp \
	--without-security
cd ../..
%{__make} \
	CC="%{__cc}" \
	OPTFLAGS="%{rpmcflags} %{rpmcppflags} -DUSE_KMOD -lkmod" \
	IPC_FLAGS="-DNETLINK_ISCSI=8 -D_GNU_SOURCE" \
	KSUBLEVEL=0

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT%{_sysconfdir}/iscsi/{nodes,send_targets,static,isns,slp,ifaces} \
	$RPM_BUILD_ROOT/etc/{rc.d/init.d,sysconfig,logrotate.d} \
	$RPM_BUILD_ROOT%{systemdunitdir} \
	$RPM_BUILD_ROOT/lib/systemd/pld-helpers.d

%{__make} install_programs install_doc install_etc \
	DESTDIR=$RPM_BUILD_ROOT

:> $RPM_BUILD_ROOT%{_sysconfdir}/iscsi/initiatorname.iscsi

install %{SOURCE1} $RPM_BUILD_ROOT/etc/rc.d/init.d/iscsid
install %{SOURCE2} $RPM_BUILD_ROOT/etc/sysconfig/iscsi
install %{SOURCE3} $RPM_BUILD_ROOT/etc/rc.d/init.d/iscsi
install %{SOURCE4} $RPM_BUILD_ROOT/etc/logrotate.d/iscsiuio

install usr/iscsistart $RPM_BUILD_ROOT%{_sbindir}
install doc/iscsistart.8 $RPM_BUILD_ROOT%{_mandir}/man8
install doc/iscsi-iname.8 $RPM_BUILD_ROOT%{_mandir}/man8

install etc/systemd/iscsi.service $RPM_BUILD_ROOT%{systemdunitdir}
install etc/systemd/iscsid.service $RPM_BUILD_ROOT%{systemdunitdir}
install etc/systemd/iscsid.socket $RPM_BUILD_ROOT%{systemdunitdir}
install etc/systemd/iscsiuio.service $RPM_BUILD_ROOT%{systemdunitdir}
install etc/systemd/iscsiuio.socket $RPM_BUILD_ROOT%{systemdunitdir}

install etc/systemd/iscsi-mark-root-nodes $RPM_BUILD_ROOT/lib/systemd/pld-helpers.d

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
%systemd_post iscsi.service iscsid.service iscsiuio.service iscsid.socket iscsiuio.socket

%preun
if [ "$1" = "0" ]; then
	%service iscsid stop
	%service iscsi stop
	/sbin/chkconfig --del iscsid
	/sbin/chkconfig --del iscsi
fi
%systemd_preun iscsi.service iscsid.service iscsiuio.service iscsid.socket iscsiuio.socket

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

%files
%defattr(644,root,root,755)
%doc Changelog README THANKS
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
%{systemdunitdir}/iscsi.service
%{systemdunitdir}/iscsid.service
%{systemdunitdir}/iscsid.socket
%{systemdunitdir}/iscsiuio.service
%{systemdunitdir}/iscsiuio.socket
%attr(755,root,root) /lib/systemd/pld-helpers.d/iscsi-mark-root-nodes
%attr(755,root,root) %{_sbindir}/iscsi-iname
%attr(755,root,root) %{_sbindir}/iscsiadm
%attr(755,root,root) %{_sbindir}/iscsid
%attr(755,root,root) %{_sbindir}/iscsistart
%attr(755,root,root) %{_sbindir}/iscsi_discovery
%attr(755,root,root) %{_sbindir}/iscsiuio
%{_mandir}/man8/iscsi-iname.8*
%{_mandir}/man8/iscsi_discovery.8*
%{_mandir}/man8/iscsiadm.8*
%{_mandir}/man8/iscsid.8*
%{_mandir}/man8/iscsistart.8*
%{_mandir}/man8/iscsiuio.8*
