# RPM spec file for OpenStack on RHEL 6 and 7
# Some bits borrowed from the katello-selinux package

%global moduletype	services
%global modulenames	os-ovs os-swift os-nova os-neutron os-mysql os-glance os-rsync os-rabbitmq os-keepalived os-keystone os-haproxy os-mongodb os-ipxe os-redis os-cinder

# Usage: _format var format
#   Expand 'modulenames' into various formats as needed
#   Format must contain '$x' somewhere to do anything useful
%global _format() export %1=""; for x in %{modulenames}; do %1+=%2; %1+=" "; done;

# Version of SELinux we were using
%global selinux_policyver 3.13.1-102.el7

# Package information
Name:			openstack-selinux
Version:		XXX
Release:		XXX
License:		GPLv2
Group:			System Environment/Base
Summary:		SELinux Policies for OpenStack
BuildArch:		noarch
URL:			https://github.com/redhat-openstack/%{name}
Requires:		policycoreutils
Requires(post):		selinux-policy-base >= %{selinux_policyver}, selinux-policy-targeted >= %{selinux_policyver}, policycoreutils, policycoreutils-python
Requires(postun):	policycoreutils
BuildRequires:		selinux-policy selinux-policy-devel
Source:			https://github.com/redhat-openstack/%{name}/archive/%{version}.tar.gz#/%{name}-%{version}.tar.gz

%description
SELinux policy modules for use with OpenStack


%package devel
Summary:		Development files (interfaces) for %{name}
Requires:		selinux-policy-devel
Requires:		%{name} = %{version}-%{release}

%description devel
Development files (interfaces) for %{name}


%package test
Summary:		AVC Tests for %{name}
Requires:		policycoreutils-python, bash
Requires:		%{name} = %{version}-%{release}

%description test
AVC tests for %{name}


%prep
%setup -q

%build
make DATADIR="%{_datadir}" TARGETS="%{modulenames}"

%install
install -d %{buildroot}%{_datadir}/%{name}/%{version}
install -p -m 755 local_settings.sh %{buildroot}%{_datadir}/%{name}/%{version}

# Install SELinux interfaces
%_format INTERFACES $x.if
install -d %{buildroot}%{_datadir}/selinux/devel/include/%{moduletype}
install -p -m 644 $INTERFACES \
	%{buildroot}%{_datadir}/selinux/devel/include/%{moduletype}

# Install policy modules
%_format MODULES $x.pp.bz2
install -d %{buildroot}%{_datadir}/selinux/packages
install -m 0644 $MODULES \
	%{buildroot}%{_datadir}/selinux/packages

# Test package files
install -d %{buildroot}%{_datadir}/%{name}/%{version}/tests
install -m 0644 tests/bz* %{buildroot}%{_datadir}/%{name}/%{version}/tests
install -m 0755 tests/check_all %{buildroot}%{_datadir}/%{name}/%{version}/tests

%post
BINDIR=%{_bindir} \
SBINDIR=%{_sbindir} \
LOCALSTATEDIR=%{_localstatedir} \
DATADIR=%{_datadir} \
SHAREDSTATEDIR=%{_sharedstatedir} \
%{_datadir}/%{name}/%{version}/local_settings.sh -m "%{modulenames}" -q


%preun
if [ $1 -eq 0 ]; then
BINDIR=%{_bindir} \
SBINDIR=%{_sbindir} \
LOCALSTATEDIR=%{_localstatedir} \
DATADIR=%{_datadir} \
SHAREDSTATEDIR=%{_sharedstatedir} \
%{_datadir}/%{name}/%{version}/local_settings.sh -xm "%{modulenames}" -q
fi


%files
%license COPYING
%dir %{_datadir}/%{name}
%dir %{_datadir}/%{name}/%{version}
%attr(0755,root,root) %{_datadir}/%{name}/%{version}/local_settings.sh
%attr(0644,root,root) %{_datadir}/selinux/packages/*.pp.bz2

%files test
%dir %{_datadir}/%{name}/%{version}/tests
%attr(0755,root,root) %{_datadir}/%{name}/%{version}/tests/check_all
%attr(0644,root,root) %{_datadir}/%{name}/%{version}/tests/bz*

%files devel
%attr(0644,root,root) %{_datadir}/selinux/devel/include/%{moduletype}/*.if


%changelog
