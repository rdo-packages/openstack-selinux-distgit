# RPM spec file for OpenStack on RHEL 6 and 7
# Some bits borrowed from the katello-selinux package

%global moduletype       services

# Version of SELinux we were using
%global selinux_policyver 3.13.1-102.el7

# Package information
Name:                   openstack-selinux
Version:                0.8.34
Release:                1%{?dist}
License:                GPLv2
Group:                  System Environment/Base
Summary:                SELinux Policies for OpenStack
BuildArch:              noarch
URL:                    https://github.com/redhat-openstack/%{name}
Requires:               policycoreutils
Requires(post):         selinux-policy-base >= %{selinux_policyver}
Requires(post):         selinux-policy-targeted >= %{selinux_policyver}
Requires(post):         policycoreutils
Requires(post):         policycoreutils-python-utils
Requires(preun):        policycoreutils
Requires:               container-selinux
BuildRequires:          selinux-policy
BuildRequires:          selinux-policy-devel
BuildRequires:          container-selinux
BuildRequires:          git
Source:                 https://github.com/redhat-openstack/%{name}/archive/%{version}.tar.gz#/%{name}-%{version}.tar.gz

%description
SELinux policy modules for use with OpenStack


%package devel
Summary:                Development files (interfaces) for %{name}
Requires:               selinux-policy-devel
Requires:               %{name} = %{version}-%{release}

%description devel
Development files (interfaces) for %{name}


%package test
Summary:                AVC Tests for %{name}
Requires:               policycoreutils-python-utils
Requires:               bash
Requires:               %{name} = %{version}-%{release}

%description test
AVC tests for %{name}


%prep
%autosetup -Sgit

%build
make DATADIR="%{_datadir}"

%install
make DATADIR="%{buildroot}%{_datadir}" \
     LOCALDIR="%{buildroot}%{_datadir}/%{name}/%{version}" \
     install

%post
BINDIR=%{_bindir} \
SBINDIR=%{_sbindir} \
LOCALSTATEDIR=%{_localstatedir} \
DATADIR=%{_datadir} \
SHAREDSTATEDIR=%{_sharedstatedir} \
%{_datadir}/%{name}/%{version}/local_settings.sh -q


%preun
if [ $1 -eq 0 ]; then
BINDIR=%{_bindir} \
SBINDIR=%{_sbindir} \
LOCALSTATEDIR=%{_localstatedir} \
DATADIR=%{_datadir} \
SHAREDSTATEDIR=%{_sharedstatedir} \
%{_datadir}/%{name}/%{version}/local_settings.sh -x -q
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
%attr(0644,root,root) %{_datadir}/%{name}/%{version}/tests/lp*

%files devel
%attr(0644,root,root) %{_datadir}/selinux/devel/include/%{moduletype}/*.if

%changelog
* Mon Aug 22 2022 Gregory Thiemonge <gthiemon@redhat.com> 0.8.34-1
- Update to 0.8.34

* Mon Jun 14 2021 Tobias Urdin <tobias.urdin@binero.com> 0.8.27-1
- Update to 0.8.27

* Fri May 21 2021 Tobias Urdin <tobias.urdin@binero.com> 0.8.26-1
- Update to 0.8.26

* Mon Nov 02 2020 Tobias Urdin <tobias.urdin@binero.com> 0.8.24-1
- Update to 0.8.24
