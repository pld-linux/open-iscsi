#
# Conditional build:
%bcond_without	dist_kernel	# allow non-distribution kernel
%bcond_without	kernel		# don't build kernel modules
%bcond_without	smp		# don't build SMP module
%bcond_without	userspace	# don't build userspace module
%bcond_with	verbose		# verbose build (V=1)
#
%define		_rc  rc7-383
%define		_rel 0.1
Summary:	iSCSI - SCSI over IP
Summary(pl.UTF-8):   iSCSI - SCSI po IP
Name:		open-iscsi
Version:	0.3
Release:	%{_rel}
License:	GPL
Group:		Base/Kernel
Source0:	http://www.open-iscsi.org/bits/%{name}-%{version}%{_rc}.tar.gz
# Source0-md5:	5009c7f2756b8c08d1000dee6dc600c1
Source1:	%{name}.init
Source2:	%{name}.sysconfig
URL:		http://www.open-iscsi.org/
BuildRequires:	db-devel
%{?with_dist_kernel:BuildRequires:	kernel-headers >= 2.6.0}
BuildRequires:	rpmbuild(macros) >= 1.268
Requires(post,preun):	/sbin/chkconfig
Requires:	rc-scripts
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

%package -n kernel-iscsi
Summary:	ISCSI kernel module
Summary(pl.UTF-8):   Moduł jądra ISCSI
Release:	%{_rel}@%{_kernel_ver_str}
Group:		Base/Kernel
Requires:	%{name} = %{version}-%{_rel}

%description -n kernel-iscsi
IP over SCSI kernel module.

%description -n kernel-iscsi -l pl.UTF-8
Moduł jądra dla protokołu IP over SCSI.

%package -n kernel-smp-iscsi
Summary:	ISCSI SMP kernel module
Summary(pl.UTF-8):   Moduł jądra SMP ISCSI
Release:	%{_rel}@%{_kernel_ver_str}
Group:		Base/Kernel
Requires:	%{name} = %{version}-%{_rel}

%description -n kernel-smp-iscsi
IP over SCSI SMP kernel module.

%description -n kernel-smp-iscsi -l pl.UTF-8
Moduł jądra SMP dla protokołu IP over SCSI.

%prep
%setup -q -n %{name}-%{version}%{_rc}

%build
%if %{with kernel}
cd kernel
%if "%{_kernel_ver}" < "2.6.12.0"
# fix the patch
grep -B 1000 -m 1 'Index: backward-compile-2.6.11.patch' backward-compile-2.6.11.patch > backward-compile-2.6.11n.patch
grep -A 1000 'Index: scsi_transport_iscsi.c' backward-compile-2.6.11.patch >> backward-compile-2.6.11n.patch
patch < backward-compile-2.6.11n.patch
%else
%if  "%{_kernel_ver}" < "2.6.13.0"
patch < backward-compile-2.6.12.patch
%endif
%endif

# kernel module(s)
for cfg in %{?with_dist_kernel:%{?with_smp:smp} up}%{!?with_dist_kernel:nondist}; do
	if [ ! -r "%{_kernelsrcdir}/config-$cfg" ]; then
		exit 1
	fi
	rm -rf include
	install -d include/{linux,config}
	ln -sf %{_kernelsrcdir}/config-$cfg .config
	ln -sf %{_kernelsrcdir}/include/linux/autoconf-$cfg.h include/linux/autoconf.h
	ln -sf %{_kernelsrcdir}/include/asm-%{_target_base_arch} include/asm
	ln -sf %{_kernelsrcdir}/Module.symvers-$cfg Module.symvers
	touch include/config/MARKER

	%{__make} -C %{_kernelsrcdir} clean \
		RCS_FIND_IGNORE="-name '*.ko' -o" \
		M=$PWD O=$PWD \
		%{?with_verbose:V=1}
	%{__make} -C %{_kernelsrcdir} modules \
		CC="%{__cc}" \
		M=$PWD O=$PWD \
		%{?with_verbose:V=1}
	mv iscsi_tcp{,-$cfg}.ko
	mv scsi_transport_iscsi{,-$cfg}.ko
done
cd ..
%endif

%if %{with userspace}
%{__make} -C usr \
	CC="%{__cc}" \
	CFLAGS="%{rpmcflags} -I../include -DLinux -DNETLINK_ISCSI=12"
%endif

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT{%{_sbindir},%{_mandir}/man{1,5,8},/etc/{rc.d/init.d,sysconfig}}

%if %{with kernel}
install -d $RPM_BUILD_ROOT/lib/modules/%{_kernel_ver}{,smp}/misc

install kernel/iscsi_tcp-%{?with_dist_kernel:up}%{!?with_dist_kernel:nondist}.ko \
	$RPM_BUILD_ROOT/lib/modules/%{_kernel_ver}/misc/iscsi_tcp.ko
install kernel/scsi_transport_iscsi-%{?with_dist_kernel:up}%{!?with_dist_kernel:nondist}.ko \
        $RPM_BUILD_ROOT/lib/modules/%{_kernel_ver}/misc/scsi_transport_iscsi.ko

%if %{with smp} && %{with dist_kernel}
install kernel/iscsi_tcp-smp.ko \
	$RPM_BUILD_ROOT/lib/modules/%{_kernel_ver}smp/misc/iscsi_tcp.ko
install kernel/scsi_transport_iscsi-smp.ko \
        $RPM_BUILD_ROOT/lib/modules/%{_kernel_ver}smp/misc/scsi_transport_iscsi.ko
%endif
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

%post -n kernel-smp-iscsi
%depmod %{_kernel_ver}smp

%postun -n kernel-smp-iscsi
%depmod %{_kernel_ver}smp

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
%doc README THANKS TODO
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

%if %{with smp} && %{with dist_kernel}
%files -n kernel-smp-iscsi
%defattr(644,root,root,755)
/lib/modules/%{_kernel_ver}smp/misc/*
%endif
%endif
