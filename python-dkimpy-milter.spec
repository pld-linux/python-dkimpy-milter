#
# Conditional build:
%bcond_with	tests	# unit tests
%bcond_with	python2 # CPython 2.x module
%bcond_without	python3 # CPython 3.x module

%if %{with python3}
%undefine with_python2
%endif

# NOTES:
# - 'module' should match the Python import path (first component?)
# - 'egg_name' should equal to Python egg name
# - 'pypi_name' must match the Python Package Index name
%define		module		dkimpy-milter
Summary:	DKIM signing and verification milter
Name:		python-%{module}
Version:	1.2.3
Release:	1
License:	BSD-like
Group:		Libraries/Python
Source0:	https://files.pythonhosted.org/packages/source/d/dkimpy-milter/%{module}-%{version}.tar.gz
# Source0-md5:	80af06b5fb348b7d1a762a9418ab9e00
Source1:	dkimpy-milter.init
Patch0:		paths.patch
Patch1:		config.patch
URL:		https://launchpad.net/dkimpy-milter
%if %{with python2}
BuildRequires:	python-modules >= 1:2.5
BuildRequires:	python-setuptools
%if %{with tests}
BuildRequires:	python-PyNaCl
BuildRequires:	python-aiodns
BuildRequires:	python-authres
BuildRequires:	python-dns >= 1.16
BuildRequires:	python-pymilter
%endif
%endif
%if %{with python3}
BuildRequires:	python3-modules >= 1:3.2
BuildRequires:	python3-setuptools
%if %{with tests}
BuildRequires:	python3-PyNaCl
BuildRequires:	python3-aiodns
BuildRequires:	python3-authres
BuildRequires:	python3-dns >= 1.16
BuildRequires:	python3-pymilter
%endif
%endif
BuildRequires:	rpm-pythonprov
BuildRequires:	rpmbuild(macros) >= 1.714
Requires:	python-modules >= 1:2.5
Requires:	python-setuptools
Conflicts:	python3-dkimpy-milter
BuildArch:	noarch
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%description
DKIM signing and verification milter.

%package -n python3-%{module}
Summary:	DKIM signing and verification milter
Group:		Libraries/Python
Requires:	python3-modules >= 1:3.2
Requires:	python3-setuptools
Conflicts:	python-dkimpy-milter

%description -n python3-%{module}
DKIM signing and verification milter

%prep
%setup -q -n %{module}-%{version}
%patch0 -p1
%patch1 -p1

%build
%if %{with python2}
%py_build %{?with_tests:test}
%endif

%if %{with python3}
%py3_build %{?with_tests:test}
%endif

%install
rm -rf $RPM_BUILD_ROOT

install -d $RPM_BUILD_ROOT{/etc/{dkimpy-milter/keys,rc.d/init.d},/usr/sbin}
install %{SOURCE1} $RPM_BUILD_ROOT/etc/rc.d/init.d/dkimpy-milter
touch $RPM_BUILD_ROOT/etc/dkimpy-milter/{KeyTable,KeyTableEd25519,SigningTable}

%if %{with python2}
%py_install

%py_ocomp $RPM_BUILD_ROOT%{py_sitedir}
%py_comp $RPM_BUILD_ROOT%{py_sitedir}
%py_postclean
%endif

%if %{with python3}
%py3_install
%endif

%{__mv} $RPM_BUILD_ROOT/usr/etc/dkimpy-milter/dkimpy-milter.conf $RPM_BUILD_ROOT/etc/dkimpy-milter/dkimpy-milter.conf
%{__mv} $RPM_BUILD_ROOT/usr/bin/dkimpy-milter $RPM_BUILD_ROOT/usr/sbin/dkimpy-milter

%clean
rm -rf $RPM_BUILD_ROOT

%pre
%groupadd -g 346 dkimpy-milter
%useradd -u 346 -d /usr/share/empty -g dkimpy-milter -c "dkimpy-milter daemon user" dkimpy-milter

%post
/sbin/chkconfig --add dkimpy-milter
%service dkimpy-milter restart

%postun
if [ "$1" = "0" ]; then
	%userremove dkimpy-milter
	%groupremove dkimpy-milter
fi

%preun
if [ "$1" = "0" ]; then
        %service dkimpy-milter stop
        /sbin/chkconfig --del dkimpy-milter
fi

%pre -n python3-%{module}
%groupadd -g 346 dkimpy-milter
%useradd -u 346 -d /usr/share/empty -g dkimpy-milter -c "dkimpy-milter daemon user" dkimpy-milter

%post -n python3-%{module}
/sbin/chkconfig --add dkimpy-milter
%service dkimpy-milter restart

%postun -n python3-%{module}
if [ "$1" = "0" ]; then
	%userremove dkimpy-milter
	%groupremove dkimpy-milter
fi

%preun -n python3-%{module}
if [ "$1" = "0" ]; then
        %service dkimpy-milter stop
        /sbin/chkconfig --del dkimpy-milter
fi

%if %{with python2}
%files
%defattr(644,root,root,755)
%doc README.md CHANGES
%attr(640,dkimpy-milter,dkimpy-milter) %config(noreplace) %verify(not md5 mtime size) /etc/dkimpy-milter/dkimpy-milter.conf
%attr(640,dkimpy-milter,dkimpy-milter) %config(noreplace) %verify(not md5 mtime size) /etc/dkimpy-milter/KeyTable
%attr(640,dkimpy-milter,dkimpy-milter) %config(noreplace) %verify(not md5 mtime size) /etc/dkimpy-milter/KeyTableEd25519
%attr(640,dkimpy-milter,dkimpy-milter) %config(noreplace) %verify(not md5 mtime size) /etc/dkimpy-milter/SigningTable
%dir %attr(750,dkimpy-milter,dkimpy-milter) /etc/dkimpy-milter
%dir %attr(750,dkimpy-milter,dkimpy-milter) /etc/dkimpy-milter/keys
%attr(754,root,root) /etc/rc.d/init.d/dkimpy-milter
%attr(755,root,root) %{_sbindir}/dkimpy-milter
%{_mandir}/man5/dkimpy-milter.conf.5*
%{_mandir}/man8/dkimpy-milter.8*
%{py_sitescriptdir}/dkimpy_milter
%{py_sitescriptdir}/dkimpy_milter-%{version}-py*.egg-info
%endif

%if %{with python3}
%files -n python3-%{module}
%defattr(644,root,root,755)
%doc README.md CHANGES
%attr(640,dkimpy-milter,dkimpy-milter) %config(noreplace) %verify(not md5 mtime size) /etc/dkimpy-milter/dkimpy-milter.conf
%attr(640,dkimpy-milter,dkimpy-milter) %config(noreplace) %verify(not md5 mtime size) /etc/dkimpy-milter/KeyTable
%attr(640,dkimpy-milter,dkimpy-milter) %config(noreplace) %verify(not md5 mtime size) /etc/dkimpy-milter/KeyTableEd25519
%attr(640,dkimpy-milter,dkimpy-milter) %config(noreplace) %verify(not md5 mtime size) /etc/dkimpy-milter/SigningTable
%dir %attr(750,dkimpy-milter,dkimpy-milter) /etc/dkimpy-milter
%dir %attr(750,dkimpy-milter,dkimpy-milter) /etc/dkimpy-milter/keys
%attr(754,root,root) /etc/rc.d/init.d/dkimpy-milter
%attr(755,root,root) %{_sbindir}/dkimpy-milter
%{_mandir}/man5/dkimpy-milter.conf.5*
%{_mandir}/man8/dkimpy-milter.8*
%{py3_sitescriptdir}/dkimpy_milter
%{py3_sitescriptdir}/dkimpy_milter-%{version}-py*.egg-info
%endif
