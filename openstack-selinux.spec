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
Version:		0.8.5
Release:		1%{?dist}
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
* Thu Mar 02 2017 Lon Hohberger <lon@redhat.com> 0.8.5-1
- Update to 0.8.5
- Fix neutron-openvswitch-agent startup failures
- Set port 8000 to http_port_t
- Resolves: rhbz#1396553 rhbz#1419418 rhbz#1420134

* Fri Feb 17 2017 Lon Hohberger <lon@redhat.com> 0.8.4-1
- Update to 0.8.4
- Allow Glance access to privsep bits
- Make Designate bind9 files named_zone_t
- Resolves: rhbz#1395240 rhbz#1353227
- [important] Fix preun scriptlet to only fire when
  uninstalling instead of upgrading

* Wed Feb 15 2017 Lon Hohberger <lon@redhat.com> 0.8.3-1
- Update to 0.8.2
- Use -q option to local_settings.sh
- Fix selinux policy version
- Drop unnecessary macro in spec file
- Use DATADIR instead of SHAREDIR for build
- Drop useless SHAREDIR when calling local_settings.sh
- Move interfaces to -devel package

* Tue Feb 14 2017 Lon Hohberger <lon@redhat.com> 0.8.0-1
- Upgrade to 0.8.0
- Use local_settings.sh from openstack-selinux instead of including 
  a lot of settings in the spec file.

* Tue Jan 3 2017 Lon Hohberger <lhh@redhat.com> 0.7.13-3
- Fix source URL

* Thu Dec 8 2016 Ryan Hallisey <rhallise@redhat.com> 0.7.13-2
- Turn on httpd_use_openstack boolean
- Resolves: rhbz#1402926

* Tue Nov 29 2016 Lon Hohberger <lon@redhat.com> 0.7.13-1
- Allow DPDK operation for OpenVSwitch
- Resolves: rhbz#1397537

* Wed Nov 02 2016 Lon Hohberger <lon@redhat.com> 0.7.12-1
- Transition to iscsid_exec_t from cinder_backup_t
- Resolves: rhbz#1384472

* Tue Nov 01 2016 Lon Hohberger <lon@redhat.com> 0.7.11-2
- Label WSGI app.log files as httpd_log_t
- Resolves: rhbz#1387347

* Wed Oct 12 2016 Ryan Hallisey <rhallise@redhat.com> 0.7.11-1
- Reverting ovs rules to connect to clamd_port_t

* Tue Oct 11 2016 Ryan Hallisey <rhallise@redhat.com> 0.7.10-2
- Run a restorecon of /var/run/redis
- Resolves: rhbz#1383775

* Thu Oct 6 2016 Ryan Hallisey <rhallise@redhat.com> 0.7.10-1
- Allow ovs to connect to clamd_port_t
- Resolves: rhbz#1382372

* Thu Sep 15 2016 Ryan Hallisey <rhallise@redhat.com> 0.7.9-1
- Allow virtlogd_t to have the dac_override cap
- Resolves: rhbz#1377272

* Thu Sep 15 2016 Ryan Hallisey <rhallise@redhat.com> 0.7.8-2
- Use selinux-polxiy-3.13.1-93.el7
- Resolves: rhbz#1375766

* Thu Sep 15 2016 Ryan Hallisey <rhallise@redhat.com> 0.7.8-1
- Allow Nova to use virtlogd_t and bump the selinux base
- policy version
- Resolves: rhbz#1375766

* Fri Sep 2 2016 Ryan Hallisey <rhallise@redhat.com> 0.7.7-1
- Allow openvswitch to connect to the vpn port
- Resolves: rhbz#1372453

* Mon Aug 29 2016 Ryan Hallisey <rhallise@redhat.com> 0.7.6-1
- Allow openvswitch to connect to its own port
- Resolves: rhbz#1334732

* Wed Aug 3 2016 Ryan Hallisey <rhallise@redhat.com> 0.7.5-1
- Allow glance registry to connect to memcached
- Resolves: rhbz#1362609

* Tue Jul 26 2016 Ryan Hallisey <rhallise@redhat.com> 0.7.4-2
- Port over some selinux policy scripted in the undercloud
- Resolves: rhbz#1360434

* Thu Apr 21 2016 Ryan Hallisey <rhallise@redhat.com> 0.7.4-1
- Neutron needs to be able to connect to neutron-openvsw
- Resolves: rhbz#1357961

* Thu Apr 21 2016 Ryan Hallisey <rhallise@redhat.com> 0.7.3-3
- Swift needs its network boolean enabled
- Resolves: rhbz#1329038

* Mon Apr 18 2016 Ryan Hallisey <rhallise@redhat.com> 0.7.3-2
- Horizon needs the ability to access its shared secret
- Resolves: rhbz#1328177

* Fri Apr 15 2016 Ryan Hallisey <rhallise@redhat.com> 0.7.3-1
- Allow keystone to use memcache as a backend
- Resolves: rhbz#1327609

* Tue Apr 12 2016 Ryan Hallisey <rhallise@redhat.com> 0.7.2-1
- Allow httpd to create Cinders log file
- Resolves: rhbz#1325623

* Tue Apr 12 2016 Ryan Hallisey <rhallise@redhat.com> 0.7.1-1
- Allow httpd to write to Cinders log
- Resolves: rhbz#1325623

* Sun Apr 10 2016 Ryan Hallisey <rhallise@redhat.com> 0.7.0-1
- Add a Cinder module and allow httpd to open the Cinder log
- Resolves: rhbz#1325623

* Thu Mar 10 2016 Ryan Hallisey <rhallise@redhat.com> 0.6.58-1
- Glance needs to talk with tmpfs
- Resolves: rhbz#1313617

* Tue Mar 8 2016 Ryan Hallisey <rhallise@redhat.com> 0.6.57-1
- Nova API needs to be able to start in WSGI with Apache
- Resolves: rhbz#1315457

* Mon Mar 7 2016 Ryan Hallisey <rhallise@redhat.com> 0.6.56-1
- Nova API needs to be able to start in WSGI with Apache
- Resolves: rhbz#1315457

* Tue Feb 23 2016 Ryan Hallisey <rhallise@redhat.com> 0.6.55-1
- Swift needs to exec rsync
- Resolves: rhbz#1302312

* Mon Feb 22 2016 Ryan Hallisey <rhallise@redhat.com> 0.6.54-1
- OVS needs to connect to a reserved port
- Resolves: rhbz#1310383

* Thu Feb 11 2016 Ryan Hallisey <rhallise@redhat.com> 0.6.53-1
- Allow nova to talk to the glance registry
- Resolves: rhbz#1306525

* Wed Jan 13 2016 Ryan Hallisey <rhallise@redhat.com> 0.6.52-1
- Allow OVS to listen on its db port
- Resolves: rhbz#1284268

* Wed Jan 13 2016 Ryan Hallisey <rhallise@redhat.com> 0.6.51-1
- Allow neutron use ipv6
- Resolves: rhbz#1294420

* Thu Dec 17 2015 Ryan Hallisey <rhallise@redhat.com> 0.6.50-1
- Allow neutron to use all executables
- Resolves: rhbz#1284268

* Wed Dec 9 2015 Ryan Hallisey <rhallise@redhat.com> 0.6.49-1
- Some services need to be able to interact with the cluster
- log file
- Resolves: rhbz#1283674

* Mon Nov 30 2015 Ryan Hallisey <rhallise@redhat.com> 0.6.48-1
- Allow ovs to interact with a tun tap device
- Resolves: rhbz#1284268

* Tue Nov 24 2015 Ryan Hallisey <rhallise@redhat.com> 0.6.47-1
- Fix policy regression for mysql.  Allow mysql to
- read cluster dirs and write to cluster tmp files.
- Resolves: rhbz#1284672

* Mon Nov 23 2015 Ryan Hallisey <rhallise@redhat.com> 0.6.46-1
- Allow keepalived to check the status of services
- Allow redis to connect to its own port
- Allow ovs to read and write tun tap device
- Resolves: rhbz#1284436 rhbz#1278430 rhbz#1284268

* Wed Nov 18 2015 Ryan Hallisey <rhallise@redhat.com> 0.6.45-1
- Optional nova_t policy to let nova execmem itself
- Resolves: rhbz#1280101

* Wed Nov 18 2015 Ryan Hallisey <rhallise@redhat.com> 0.6.44-1
- Optional nova_t policy to let nova-novncproxy use httpd
- Resolves: rhbz#1281547

* Wed Nov 11 2015 Ryan Hallisey <rhallise@redhat.com> 0.6.43-1
- Neutron needs to be able to search http directories
- Resolves: rhbz#1260202

* Mon Nov 9 2015 Ryan Hallisey <rhallise@redhat.com> 0.6.42-2
- Openvswitch port is changing to 6653
- Resolves: rhbz#1260202

* Fri Nov 6 2015 Ryan Hallisey <rhallise@redhat.com> 0.6.42-1
- OVS needs to be able to connect to unreserved ports
- Glance needs to be able to interact with nfs
- Resolves: rhbz#1259419 rhbz#1219406

* Tue Sep 29 2015 Lon Hohberger <lon@redhat.com> 0.6.41-1
- Add keystone execmem boolean
- Resolves: rhbz#1249685

* Mon Sep 21 2015 Lon Hohberger <lon@redhat.com> 0.6.39-2
- More execmem booleans
- Resolves: rhbz#1249685

* Fri Sep 18 2015 Lon Hohberger <lon@redhat.com> 0.6.39-1
- Add nova_use_execmem
- Turn on nova_use_execmem and httpd_execmem
- Resolves: rhbz#1249685

* Thu Jul 16 2015 Lon Hohberger <lon@redhat.com> 0.6.37-1
- Allow haproxy to monitor keepalived via systemctl
- Resolves: rhbz#1243039

* Thu Jul 9 2015 Ryan Hallisey <rhallise@redhat.com> 0.6.35-3
- Neutron needs neutron-vpn-agent to be given the proper
- label when in /usr/bin
- Resolves: rhbz#1240647

* Tue Jun 23 2015 Ryan Hallisey <rhallise@redhat.com> 0.6.35-1
- OVS needs to be able to open unreserved ports
- Resolves: rhbz#1233154

* Wed Jun 17 2015 Ryan Hallisey <rhallise@redhat.com> 0.6.34-1
- Tripleo selinux needs to merge into openstack-selinux
- Resolves: rhbz#1232892 rhbz#1231868

* Fri Jun 12 2015 Lon Hohberger <lon@redhat.com> 0.6.32-1
- Allow neutron_t to manage neutron_tmp_t sockets
- Resolves: rhbz#1230900

* Fri Jun 12 2015 Lon Hohberger <lhh@redhat.com> 0.6.31-2
- Set neutron-rootwrap-daemon to the right context
- Resolves: rhbz#1230900

* Wed Apr 29 2015 Ryan Hallisey <rhallise@redhat.com> 0.6.31-1
- Missing var_lib_t type
- Resolves: rhbz#1210271

* Wed Apr 29 2015 Ryan Hallisey <rhallise@redhat.com> 0.6.30-1
- Glance needs some more permissions to symlink to /home
- Resolves: rhbz#1210271

* Wed Apr 15 2015 Ryan Hallisey <rhallise@redhat.com> 0.6.29-1
- Svirt needs the ability to write to nova_var_lib_t
- Resolves: rhbz#1211628

* Mon Apr 13 2015 Ryan Hallisey <rhallise@redhat.com> 0.6.28-1
- Glance and Nova will be allowed to create sys links
- Resolves: rhbz#1210271

* Wed Apr 8 2015 Ryan Hallisey <rhallise@redhat.com> 0.6.27-2
- In order to run NFS need to turn on a boolean
- Resolves: rhbz#1209237

* Wed Apr 1 2015 Ryan Hallisey <rhallise@redhat.com> 0.6.27-1
- Keepalived is trying to talk to neutron_var_lib_t and needs permission
- Resolves: rhbz#1206148

* Tue Mar 31 2015 Ryan Hallisey <rhallise@redhat.com> 0.6.26-1
- Keepalived is trying to talk to sysfs_t and needs permission
- Resolves: rhbz#1206148

* Tue Mar 10 2015 Ryan Hallisey <rhallise@redhat.com> 0.6.25-1
- Swift needs permission to interact with rabbit
- Resolves: rhbz#1200591

* Tue Mar 10 2015 Ryan Hallisey <rhallise@redhat.com> 0.6.24-1
- Swift need to be able to open var_log_t
- Resolves: rhbz#1200591

* Thu Feb 26 2015 Lon Hohberger <lhh@redhat.com> 0.6.23-3
- Do everything except port opens in one transaction, but
- don't apply new policy unless selinux is enabled

* Thu Feb 26 2015 Lon Hohberger <lhh@redhat.com> 0.6.23-2
- Rebuild against older selinux-policy
- Speed up boolean enable/disable

* Mon Feb 23 2015 Ryan Hallisey <rhallise@redhat.com> 0.6.23-1
- Mongodb needs selinux permissions to prevent seg fault
- Resolves: rhbz#1192049

* Mon Feb 23 2015 Ryan Hallisey <rhallise@redhat.com> 0.6.22-1
- Allow haproxy_t to talk to the filesystem
- Resolves: rhbz#1195215

* Tue Feb 17 2015 Lon Hohberger <lhh@redhat.com> 0.6.21-1
- Update to 0.6.21
- Use optional_policy for elasticsearch_port_t in case foreman-selinux
  is installed
- Resolves: rhbz#1192575

* Fri Feb 13 2015 Ryan Hallisey <rhallise@redhat.com> - 0.6.20-5
- Make the modules are loaded
- Resolves: rhbz#1191172

* Fri Feb 13 2015 Ryan Hallisey <rhallise@redhat.com> - 0.6.20-4
- Revert back to the slower policy until an issue with tripleo
- installation is resolved
- Resolves: rhbz#1191172

* Fri Feb 13 2015 Lon Hohberger <lhh@redhat.com> - 0.6.20-3
- Don't use temp file when doing single-transaction installation
- Add missing booleans
- Resolves: rhbz#1191172

* Thu Feb 12 2015 Ryan Hallisey <rhallise@redhat.com> - 0.6.20-1
- Remove policy conflict in the Glance module
- Resolves: rhbz#1192042

* Tue Feb 10 2015 Ryan Hallisey <rhallise@redhat.com> - 0.6.19-1
- Speedup openstack-selinux installation
- Resolves: rhbz#1191172

* Wed Jan 28 2015 Lon Hohberger <lon@redhat.com> - 0.6.18-2
- Require latest policy from RHEL 7.0
- Resolves: rhbz#1186628

* Mon Jan 26 2015 Ryan Hallisey <rhallise@redhat.com> - 0.6.18-1
- Rabbitmq needs a policy update in order to function
- Resolves: rhbz#1185444

* Mon Jan 19 2015 Ryan Hallisey <rhallise@redhat.com> - 0.6.17-1
- Keepalived needs to be able to kill neutron
- Resolves: rhbz#1180881

* Wed Jan 14 2015 Ryan Hallisey <rhallise@redhat.com> - 0.6.16-1
- Keepalived needs additional policy to run
- Resolves: rhbz#1180881

* Tue Jan 13 2015 Ryan Hallisey <rhallise@redhat.com> - 0.6.15-1
- Libvirt needs to be able to transition to iscsi
- Resolves: rhbz#1181428

* Tue Jan 13 2015 Ryan Hallisey <rhallise@redhat.com> - 0.6.14-1
- Add additional optional policy for keystone_cgi_script_exec_t
- Resolves: rhbz#1181677

* Mon Jan 12 2015 Ryan Hallisey <rhallise@redhat.com> - 0.6.13-1
- Keepalived needs a lot of permissions so that the files
- it creates on the fly will run with selinux
- Resolves: rhbz#1180679 rhbz#1180881

* Fri Jan 9 2015 Ryan Hallisey <rhallise@redhat.com> - 0.6.12-1
- Nova Network needs to be able to write to its own keys
- Resolves: rhbz#1180373

* Fri Jan 9 2015 Ryan Hallisey <rhallise@redhat.com> - 0.6.11-1
- Keepalived needs to be able to transition to Neutron
- Resolves: rhbz#1180679

* Thu Jan 8 2015 Ryan Hallisey <rhallise@redhat.com> - 0.6.10-1
- Add optional policy for keystone_cgi_script_exec_t
- Resolves: rhbz#1176842

* Thu Jan 8 2015 Ryan Hallisey <rhallise@redhat.com> - 0.6.9-1
- Http needs to be able to interect with keystone
- Resolves: rhbz#1180230

* Tue Jan 6 2015 Ryan Hallisey <rhallise@redhat.com> - 0.6.8-1
- Rabbitmq needs to link to rabbitmq_var_lib_t files
- Resolves: rhbz#1179040

* Mon Jan 5 2015 Ryan Hallisey <rhallise@redhat.com> - 0.6.7-1
- Allow neutron to interact with radvd files
- Resolves: rhbz#1168526 rhbz#1176830

* Tue Dec 23 2014 Ryan Hallisey <rhallise@redhat.com> - 0.6.6-1
- Allow neutron to execute radvd files and getattr from 
- file systems.
- Resolves: rhbz#1168526 rhbz#1176830

* Wed Dec 17 2014 Ryan Hallisey <rhallise@redhat.com> - 0.6.5-2
- Turn on httpd boolean to allow Horizon to connect to Keystone
- Resolves: rhbz#1174977

* Mon Dec 15 2014 Ryan Hallisey <rhallise@redhat.com> - 0.6.5-1
- Neutron needs to be allowed to interact with netlink socket
- Resolves: rhbz#1171458

* Tue Dec 9 2014 Ryan Hallisey <rhallise@redhat.com> - 0.6.4-1
- Nova network needs the ability to interact with netutils
- Allow Nova network to interact with packet sockets
- Resolves: rhbz#1170839

* Mon Dec 8 2014 Ryan Hallisey <rhallise@redhat.com> - 0.6.3-1
- The keystone policy file had a syntax error causing the module
- to fail
- Resolves: rhbz#1171827

* Mon Dec 8 2014 Ryan Hallisey <rhallise@redhat.com> - 0.6.2-1
- Neutron needs to transition to keepalived
- Allow Neutron to exec files from neutron_var_lib_t
- Resolves: rhbz#1169859 rhbz#1171460 rhbz#1171458

* Thu Dec 4 2014 Ryan Hallisey <rhallise@redhat.com> - 0.6.1-2
- In order for Neutron to run, mysql_safe_t needs to be able
- to interact with cluster types.
- Resolves: rhbz#1170367

* Mon Nov 24 2014 Ryan Hallisey <rhallise@redhat.com> - 0.6.1-1
- Allow Keystone to signal processes labelled keystone_t
- Resolves: rhbz#1167073

* Tue Nov 18 2014 Ryan Hallisey <rhallise@redhat.com> - 0.6.0-1
- Nova needs to be able to name_connect to memcache_port_t
- Add new file os-keepalived.te
- Allow Neutron to connect to http
- Resolves: rhbz#1162761 rhbz#1158213 rhbz#1145886 rhbz#1144199

* Fri Oct 17 2014 Lon Hohberger <lhh@redhat.com> 0.5.19-2
- Drop bad upgrade error

* Thu Oct 16 2014 Ryan Hallisey <rhallise@redhat.com> - 0.5.19-1
- Allow neutron_t to kill dnsmasq
- Resolves: rhbz#1153656

* Wed Sep 17 2014 Lon Hohberger <lhh@redhat.com> - 0.5.16-2
- Drop incorrect AVC checks (e.g. leaked FDs, or incorrect contexts)
- Allow glance to execmem/execstack until we have the proper boolean
- Resolves: rhbz#1130212

* Fri Sep 12 2014 Ryan Hallisey <rhallise@redhat.com> - 0.5.16-1
- Turn on booleans rsync_full_access and rsync_client
- Add new files os-rsync and os-rabbitmq
- Minor changes to testpolicy script
- Updated AVCs for regression testing
- Resolves: rhbz#1135637

* Wed Aug 20 2014 Ryan Hallisey <rhallise@redhat.com> - 0.5.15-1
- Turn on boolean glance_use_execmem
- Updated AVCs for regression testing
- Resolves: rhbz#1130212

* Wed Jul 23 2014 Ryan Hallisey <rhallise@redhat.com> - 0.5.14-4
- Added new tool to sort and save AVCs for regression testing
- Updated AVCs for regression testing
- Resolves:

* Wed Jul 16 2014 Ryan Hallisey <rhallise@redhat.com> - 0.5.14-3
- Port 4444 is now labeled as mysqld_port_t
- Resolves: rhbz#1118859

* Wed Jul 16 2014 Ryan Hallisey <rhallise@redhat.com> - 0.5.14-2
- Added virt_use_execmem and glance_use_execmem bools
- Resolves: rhbz#1119845 rhbz#1119400

* Tue Jul 15 2014 Ryan Hallisey <rhallise@redhat.com> - 0.5.14-1
- Allow mysqld_t to read from mysqld_safe_exec_t files
- Added glance.te file
- Add new avcs to regression test
- Resolves: rhbz#1118859 rhbz#1119151

* Mon Jul 14 2014 Ryan Hallisey <rhallise@redhat.com> - 0.5.13-1
- Allow mysqld_t to execute lsof
- Resolves: rhbz#1118859

* Tue Jul 08 2014 Ryan Hallisey <rhallise@redhat.com> - 0.5.12-1
- Allow ssh to open and getattr from nova_var_lib_t
- Resolves: rhbz#1117301

* Mon Jul 07 2014 Ryan Hallisey <rhallise@redhat.com> - 0.5.11-1
- Allow neutron_t to talk to haproxy_t
- Resolves: rhbz#1116755

* Wed Jul 02 2014 Ryan Hallisey <rhallise@redhat.com> - 0.5.10-1
- Allow neutron_t to kill haproxy_t processes
- Allow neutron_t to unmount a proc_t filesystem
- Resolves: rhbz#1115724

* Tue Jul 01 2014 Lon Hohberger <lhh@redhat.com> - 0.5.9-1
- Allow haproxy to access its configuration after transition
- Resolves: rhbz#1114254

* Tue Jul 01 2014 Lon Hohberger <lhh@redhat.com> - 0.5.8-1
- Add test subpackage
- Add domain transition to haproxy for os-neutron
- Remove cluster-mode from manual workarounds

* Tue Jul 01 2014 Lon Hohberger <lhh@redhat.com> - 0.5.7-3
- Quiet errors on upgrade in case of duplicate/new modules

* Tue Jul 01 2014 Lon Hohberger <lhh@redhat.com> - 0.5.7-2
- Add os-neutron and os-mysql to install targets

* Mon Jun 30 2014 Ryan Hallisey <rhallise@redhat.com> - 0.5.7-1
- Give mysqld_t permission to search nfs_t directories
- Allowing neutron_t to connect to all tcp ports
- Allow mysqld_t to bind and connect to tram_port
- Resolves: rhbz#1110263 rhbz#1114581 rhbz#1114254

* Fri Jun 27 2014 Ryan Hallisey <rhallise@redhat.com> - 0.5.6-1
- Allow sshd_t to read from nova_var_lib_t
- Added file os-mysql.te with new policy
- Resolves: rhbz#1113723 rhbz#1081544

* Wed Jun 25 2014 Ryan Hallisey <rhallise@redhat.com> - 0.5.5-3
- Turned on boolean haproxy_connect_any
- Resolves: rhbz#1108937

* Wed Jun 25 2014 Ryan Hallisey <rhallise@redhat.com> - 0.5.5-2
- Turned on boolean nis_enabled
- Resolves: rhbz#1112631

* Tue Jun 24 2014 Ryan Hallisey <rhallise@redhat.com> - 0.5.5-1
- Turned on boolean glance_use_fusefs
- Changes made to os-neutron to allow neutron_t to connect to httpd_port_t
- Changes made to os-nova to read initrc_var_run_t
- Resolves: rhbz#1111990 rhbz#1083609

* Mon Jun 23 2014 Ryan Hallisey <rhallise@redhat.com> - 0.5.4-1
- Added os-neutron policy 
- Changes made to os-swift to read httpd_config_t
- Resolves: rhbz#1105344 rhbz#1110263

* Tue Jun 17 2014 Lon Hohberger <lhh@redhat.com> - 0.5.2-2
- Add proper file contexts neutron-metadata-agent, neutron-netns-cleanup,
  and neutron-ns-metadata-proxy
- Drop monitoring-plugins tweaks in RPM post; not needed any more
- Resolves: rhbz#1110263

* Fri Jun 13 2014 Lon Hohberger <lhh@redhat.com> - 0.5.2-1
- Additional tweak for nova networking
- Resolves: rhbz#1095869

* Fri Jun 13 2014 Lon Hohberger <lhh@redhat.com> - 0.5.1-3
- Require SELinux policy from 7.0 updates
- Turn on swift and nova modules

* Fri Jun 13 2014 Lon Hohberger <lhh@redhat.com> - 0.5.1-1
- Import 0.5.1 to work around Nova network issues
- Resolves: rhbz#1095869

* Fri Jun 13 2014 Lon Hohberger <lhh@redhat.com> - 0.5.0-3
- Set check_ping to the correct context

* Fri Jun 13 2014 Lon Hohberger <lhh@redhat.com> - 0.5.0-2
- Turn on virt_use_fusefs in RPM post
- Resolves: rhbz#1052971

* Fri Jun 13 2014 Lon Hohberger <lhh@redhat.com> - 0.5.0-1
- Set port 15672/tcp to amqp_port_t
- Resolves: rhbz#1107873

* Thu Jun 12 2014 Lon Hohberger <lhh@redhat.com> - 0.5.0-0
- Initial build
- Resolves: rhbz#1108187

* Mon Dec 09 2013 Lon Hohberger <lhh@redhat.com> - 0.1.3-2
- Set neutron-vpn-agent to neutron_exec_t
- Require RHEL 6.5 selinux-policy
  Resolves: rhbz#1039204

* Thu Nov 14 2013 Lon Hohberger <lhh@redhat.com> - 0.1.3-1
- Remove unnecessary policy for LBaaS
- Rebase to 0.1.3
- Correct file contexts in RPM post for now
  Resolves: rhbz#1020052

* Tue Nov 12 2013 Lon Hohberger <lhh@redhat.com> - 0.1.2-13
- Additional policy additions for LBaaS
  Resolves: rhbz#1020052

* Fri Nov 08 2013 Lon Hohberger <lhh@redhat.com> - 0.1.2-12
- Add Neutron LBaaS tunable
  Resolves: rhbz#1020052

* Wed Mar 20 2013 Lon Hohberger <lhh@redhat.com> - 0.1.2-11
- Add BuildRequires for selinux-policy-devel
- Fix directory permissions

* Wed Mar 20 2013 Lon Hohberger <lhh@redhat.com> - 0.1.2-10
- Depend on later release of selinux-policy since it contains
  fixes for OpenStack Swift's use of GlusterFS 
  Resolves: rhbz#923426

* Tue Mar 19 2013 Lon Hohberger <lhh@redhat.com> - 0.1.2-9
- Depend on later release of selinux-policy since it contains
  fixes for OpenStack Quantum
  Resolves: rhbz#923426

* Mon Mar 18 2013 Lon Hohberger <lhh@redhat.com> - 0.1.2-8
- Call restorecon on /srv to ensure that previously-created
  Swift objects have the correct SELinux context
  Resolves: rhbz#918721

* Wed Mar 06 2013 Lon Hohberger <lhh@redhat.com> - 0.1.2-7
- Add a type and path for swift when using rsync
  Resolves: rhbz#918721

* Tue Mar 05 2013 Lon Hohberger <lhh@redhat.com> - 0.1.2-6
- Allow dnsmasq_t to write to quantum's DHCP directory
  Resolves: rhbz#915906

* Fri Feb 22 2013 Lon Hohberger <lhh@redhat.com> - 0.1.2-5
- Allow rsync to deal with lock files
  Resolves: rhbz#885529

* Thu Feb 21 2013 Lon Hohberger <lhh@redhat.com> - 0.1.2-4
- Fix up changelog for wrong bug
- Ancillary patch for dnsmasq AVC denial
- Resolves: rhbz#889782

* Tue Feb 12 2013 Lon Hohberger <lhh@redhat.com> - 0.1.2-3
- Spec file cleanups

* Tue Feb 12 2013 Lon Hohberger <lhh@redhat.com> - 0.1.2-2
- Spec file cleanups 

* Tue Feb 12 2013 Lon Hohberger <lhh@redhat.com> - 0.1.2-1
- Add policy for swift to resolve rsync issues
- Resolves: rhbz#885529

* Tue Feb 12 2013 Lon Hohberger <lhh@redhat.com> - 0.1.1-1
- Add policy for quantum to resolve DHCP lease issues
- Resolves: rhbz#889782

* Mon Feb 11 2013 Lon Hohberger <lhh@redhat.com> - 0.1.0-2
- Fix URL and Source identifiers

* Mon Feb 11 2013 Lon Hohberger <lhh@redhat.com> - 0.1.0-1
- First Build, addreses openstack nova issues
- Resolves: rhbz#913197
