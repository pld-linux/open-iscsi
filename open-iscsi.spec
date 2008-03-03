%define		_rc  865.15
%define		_rel 2
Summary:	iSCSI - SCSI over IP
Summary(pl.UTF-8):	iSCSI - SCSI po IP
Name:		open-iscsi
Version:	2.0
Release:	0.%{_rc}.%{_rel}
License:	GPL
Group:		Networking/Daemons
Source0:	http://www.open-iscsi.org/bits/%{name}-%{version}-%{_rc}.tar.gz
# Source0-md5:	2efff8c813ec84677a80c3e881942ffc
Source1:	%{name}.init
Source2:	%{name}.sysconfig
URL:		http://www.open-iscsi.org/
BuildRequires:	db-devel
BuildRequires:	rpmbuild(macros) >= 1.379
Requires(post,preun):	/sbin/chkconfig
Requires:	rc-scripts
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
%setup -q -n %{name}-%{version}-%{_rc}

%build
for i in usr utils utils/fwparam_ibft; do
	%{__make} -C $i \
		CC="%{__cc}" \
		CFLAGS="%{rpmcflags} -I../include -DLinux -DNETLINK_ISCSI=12 -D_GNU_SOURCE"
done

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT{%{_sbindir},%{_mandir}/man8,/etc/{iscsi/ifaces,iscsi/nodes,iscsi/send_targets,rc.d/init.d,sysconfig}}

install %{SOURCE1} $RPM_BUILD_ROOT/etc/rc.d/init.d/iscsi
install %{SOURCE2} $RPM_BUILD_ROOT/etc/sysconfig/iscsi

install etc/iscsid.conf $RPM_BUILD_ROOT%{_sysconfdir}/iscsi
:> $RPM_BUILD_ROOT%{_sysconfdir}/iscsi/initiatorname.iscsi

install usr/{iscsid,iscsiadm,iscsistart} utils/iscsi-iname $RPM_BUILD_ROOT%{_sbindir}
install utils/fwparam_ibft/fwparam_ibft $RPM_BUILD_ROOT%{_sbindir}

install doc/*.8 $RPM_BUILD_ROOT/%{_mandir}/man8

%clean
rm -rf $RPM_BUILD_ROOT

%pre
%groupadd -g 223 iscsi
%useradd -u 223 -d /tmp -s /bin/false -c "iSCSI Daemon" -g iscsi iscsi

%post
if ! grep -q "^InitiatorName=[^ \t\n]" %{_sysconfdir}/initiatorname.iscsi 2>/dev/null ; then
	echo "InitiatorName=$(iscsi-iname)" >> %{_sysconfdir}/initiatorname.iscsi
fi
/sbin/chkconfig --add iscsi

%preun
if [ "$1" = "0" ]; then
	%service iscsi stop
	/sbin/chkconfig --del iscsi
fi

%postun
if [ "$1" = "0" ]; then
	%userremove iscsi
	%groupremove iscsi
fi

%files
%defattr(644,root,root,755)
%doc ChangeLog README THANKS
%dir %{_sysconfdir}/iscsi
%dir %{_sysconfdir}/iscsi/ifaces
%dir %{_sysconfdir}/iscsi/nodes
%dir %{_sysconfdir}/iscsi/send_targets
%config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/iscsi/iscsid.conf
%config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/iscsi/initiatorname.iscsi
%attr(640,root,root) %config(noreplace) %verify(not md5 mtime size) /etc/sysconfig/iscsi
%attr(754,root,root) /etc/rc.d/init.d/iscsi
%attr(755,root,root) %{_sbindir}/*
%{_mandir}/man8/*
