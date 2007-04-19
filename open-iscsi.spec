#
# Conditional build:
%bcond_without	dist_kernel	# allow non-distribution kernel
%bcond_without	kernel		# don't build kernel modules
%bcond_without	userspace	# don't build userspace module
%bcond_with	verbose		# verbose build (V=1)
#
%define		_rc  -754
%define		_rel 0.1
Summary:	iSCSI - SCSI over IP
Summary(pl.UTF-8):	iSCSI - SCSI po IP
Name:		open-iscsi
Version:	2.0
Release:	%{_rel}
License:	GPL
Group:		Base/Kernel
Source0:	http://www.open-iscsi.org/bits/%{name}-%{version}%{_rc}.tar.gz
# Source0-md5:	2e7ce941ea4e4eda7c82f0b272a33bf9
Source1:	%{name}.init
Source2:	%{name}.sysconfig
URL:		http://www.open-iscsi.org/
BuildRequires:	db-devel
%{?with_dist_kernel:BuildRequires:	kernel-headers >= 2.6.20.2}
BuildRequires:	rpmbuild(macros) >= 1.379
Requires(post,preun):	/sbin/chkconfig
Requires:	rc-scripts
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%define		_sbindir	/sbin
%define		_moddir		kernel/2.6.20

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

%package -n kernel-iscsi
Summary:	ISCSI kernel module
Summary(pl.UTF-8):	Moduł jądra ISCSI
Release:	%{_rel}@%{_kernel_ver_str}
Group:		Base/Kernel
%{?with_dist_kernel:%requires_releq_kernel}

%description -n kernel-iscsi
IP over SCSI kernel module.

%description -n kernel-iscsi -l pl.UTF-8
Moduł jądra dla protokołu IP over SCSI.

%prep
%setup -q -n %{name}-%{version}%{_rc}

cat > %{_moddir}/Makefile << EOF
EXTRA_CFLAGS += -I%{_moddir} -I$PWD/include

obj-m += scsi_transport_iscsi.o
obj-m += libiscsi.o
obj-m += iscsi_tcp.o
EOF

%build
%if %{with kernel}
%build_kernel_modules -C %{_moddir} -m scsi_transport_iscsi,libiscsi,iscsi_tcp
%endif

%if %{with userspace}
%{__make} -C usr \
	CC="%{__cc}" \
	CFLAGS="%{rpmcflags} -I../include -DLinux -DNETLINK_ISCSI=12 -D_GNU_SOURCE"
%endif

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT{%{_sbindir},%{_mandir}/man{1,5,8},/etc/{rc.d/init.d,sysconfig}}

%if %{with kernel}
%install_kernel_modules -m %{_moddir}/{iscsi_tcp,libiscsi,scsi_transport_iscsi} -d misc
%endif

%if %{with userspace}
install %{SOURCE1} $RPM_BUILD_ROOT/etc/rc.d/init.d/iscsi
install %{SOURCE2} $RPM_BUILD_ROOT/etc/sysconfig/iscsi

:> $RPM_BUILD_ROOT%{_sysconfdir}/initiatorname.iscsi

install etc/iscsid.conf $RPM_BUILD_ROOT%{_sysconfdir}

install usr/iscsid usr/iscsiadm $RPM_BUILD_ROOT%{_sbindir}
%endif

%clean
rm -rf $RPM_BUILD_ROOT

%post -n kernel-iscsi
%depmod %{_kernel_ver}

%postun -n kernel-iscsi
%depmod %{_kernel_ver}

%post
if ! grep -q "^InitiatorName=[^ \t\n]" %{_sysconfdir}/initiatorname.iscsi 2>/dev/null ; then
	echo "InitiatorName=$(hostname -f)" >> %{_sysconfdir}/initiatorname.iscsi
fi

/sbin/chkconfig --add iscsi
#%%service iscsi restart

%preun
if [ "$1" = "0" ]; then
	%service iscsi stop
	/sbin/chkconfig --del iscsi
fi

%if %{with userspace}
%files
%defattr(644,root,root,755)
%doc README THANKS
%attr(755,root,root) %{_sbindir}/*
%attr(750,root,root) %config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/iscsid.conf
%config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/initiatorname.iscsi
%attr(754,root,root) /etc/rc.d/init.d/iscsi
%attr(640,root,root) %config(noreplace) %verify(not md5 mtime size) /etc/sysconfig/iscsi
%endif

%if %{with kernel}
%files -n kernel-iscsi
%defattr(644,root,root,755)
/lib/modules/%{_kernel_ver}/misc/*
%endif
