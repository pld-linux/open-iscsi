#
# Conditional build:
%bcond_without	dist_kernel	# allow non-distribution kernel
%bcond_without	kernel		# don't build kernel modules
%bcond_without	smp		# don't build SMP module
%bcond_without	userspace	# don't build userspace module
%bcond_with	verbose		# verbose build (V=1)
#
Summary:	iSCSI - SCSI over IP
Summary(pl):	iSCSI - SCSI po IP
Name:		open-iscsi
Version:	0.3
%define		_rc  rc7-383
%define		_rel 0.1
Release:	%{_rel}
License:	GPL
Group:		Base/Kernel
Source0:	http://www.open-iscsi.org/bits/%{name}-%{version}%{_rc}.tar.gz
# Source0-md5:	5009c7f2756b8c08d1000dee6dc600c1
Source1:	%{name}.init
Source2:	%{name}.sysconfig
URL:		http://www.open-iscsi.org/
%{?with_dist_kernel:BuildRequires:	kernel-headers >= 2.6.0}
BuildRequires:	db-devel
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%define		_sbindir	/sbin

%description
The Linux iSCSI driver acts as an iSCSI protocol initiator to
transport SCSI requests and responses over an IP network between the
client and an iSCSI-enabled target device such as a Cisco SN 5420
storage router. The iSCSI protocol is an IETF-defined protocol for IP
storage. For more information about the iSCSI protocol, refer to the
IETF standards for IP storage at <http://www.ietf.org/>.

%description -l pl
Sterownik Linux iSCSI zachowuje siê jak inicjator protoko³u iSCSI do
transportu zleceñ SCSI i odpowiedzi po sieci IP miêdzy klientem a
urz±dzeniem docelowym obs³uguj±cym iSCSI, takim jak Cisco SN 5420.
Protokó³ iSCSI jest zdefiniowany przez IETF do sk³adowania IP. Wiêcej
informacji o protokole iSCSI znajduje siê w standardach IETF na
<http://www.ietf.org/>.

%package -n kernel-iscsi
Summary:	ISCSI kernel module
Summary(pl):	Modu³ j±dra ISCSI
Release:	%{_rel}@%{_kernel_ver_str}
Group:		Base/Kernel
Requires:	%{name} = %{version}-%{_rel}

%description -n kernel-iscsi
IP over SCSI kernel module.

%description -n kernel-iscsi -l pl
Modu³ j±dra dla protoko³u IP over SCSI.

%package -n kernel-smp-iscsi
Summary:	ISCSI SMP kernel module
Summary(pl):	Modu³ j±dra SMP ISCSI
Release:	%{_rel}@%{_kernel_ver_str}
Group:		Base/Kernel
Requires:	%{name} = %{version}-%{_rel}

%description -n kernel-smp-iscsi
IP over SCSI SMP kernel module.

%description -n kernel-smp-iscsi -l pl
Modu³ j±dra SMP dla protoko³u IP over SCSI.

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

:> $RPM_BUILD_ROOT/etc/initiatorname.iscsi

install etc/iscsid.conf $RPM_BUILD_ROOT/etc

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
/sbin/chkconfig --add iscsi
#if [ -f /var/lock/subsys/iscsi ]; then
#	/etc/rc.d/init.d/iscsi restart 1>&2
#else
#	echo "Type \"/etc/rc.d/init.d/iscsi start\" to start iscsi" 1>&2
#fi

if ! grep -q "^InitiatorName=[^ \t\n]" /etc/initiatorname.iscsi 2>/dev/null ; then
	echo "InitiatorName=$(hostname -f)" >> /etc/initiatorname.iscsi
fi

%preun
if [ "$1" = "0" ]; then
#	if [ -f /var/lock/subsys/iscsi ]; then
#		/etc/rc.d/init.d/iscsi stop >&2
#	fi
	/sbin/chkconfig --del iscsi
fi

%if %{with userspace}
%files
%defattr(644,root,root,755)
%doc README THANKS TODO
%attr(755,root,root) %{_sbindir}/*
%attr(750,root,root) %config(noreplace) %verify(not md5 mtime size) /etc/iscsid.conf
%attr(644,root,root) %config(noreplace) %verify(not md5 mtime size) /etc/initiatorname.iscsi
%attr(754,root,root) /etc/rc.d/init.d/iscsi            
%attr(640,root,root) %config(noreplace) %verify(not md5 mtime size) /etc/sysconfig/iscsi
%endif

%if %{with kernel}
%files -n kernel-iscsi
%defattr(644,root,root,755)
%attr(644,root,root) /lib/modules/%{_kernel_ver}/misc/*

%if %{with smp} && %{with dist_kernel}
%files -n kernel-smp-iscsi
%defattr(644,root,root,755)
%attr(644,root,root) /lib/modules/%{_kernel_ver}smp/misc/*
%endif
%endif
