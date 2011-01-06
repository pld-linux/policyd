%include	/usr/lib/rpm/macros.perl
Summary:	Policyd - an anti-spam plugin for Postfix
Summary(pl.UTF-8):	Policyd - wtyczka antyspamowa dla Postfiksa
Name:		policyd
Version:	2.0.10
Release:	0.10
License:	GPL v2
Group:		Networking
Source0:	http://downloads.sourceforge.net/policyd/cluebringer-%{version}.tar.bz2
# Source0-md5:	cdff8f8e7c0e95143f7108159aed80c6
Source1:	apache.conf
Source2:	%{name}.sysconfig
Source3:	%{name}.conf
Source4:	%{name}.init
Patch0:		config.patch
URL:		http://www.policyd.org/
BuildRequires:	bash
BuildRequires:	rpm-perlprov >= 4.1-13
Requires(pre):	/bin/id
Requires(pre):	/usr/bin/getgid
Requires(pre):	/usr/sbin/groupadd
Requires(pre):	/usr/sbin/useradd
Requires(post,preun):	/sbin/chkconfig
Requires(postun):	/usr/sbin/groupdel
Requires(postun):	/usr/sbin/userdel
Requires:	perl-Net-CIDR
Requires:	perl-cbp = %{version}-%{release}
Requires:	rc-scripts
Provides:	group(policyd)
Provides:	user(policyd)
BuildArch:	noarch
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%define		_webapps	/etc/webapps
%define		_webapp		%{name}
%define		_webappdir	%{_datadir}/%{name}-webui

%description
Policyd v2 (codenamed "cluebringer") is a multi-platform policy server
for popular MTAs. This policy daemon is designed mostly for large
scale mail hosting environments. The main goal is to implement as many
spam combating and email compliance features as possible while at the
same time maintaining the portability, stability and performance
required for mission critical email hosting of today. Most of the
ideas and methods implemented in Policyd v2 stem from Policyd v1
aswell as the authors' long time involvement in large scale mail
hosting industry.

%description -l pl.UTF-8
Policyd to wtyczka antyspamowa dla Postfiksa obsługująca szare listy,
tłumienie (liczby lub objętości wiadomości w ciągu jednostki czasu)
oparte na nadawcy (według koperty, uwierzytelnienia SASL albo
hosta/IP), ograniczanie częstotliwości dostarczania do nadawcy,
monitorowanie/dodawanie do czarnej listy pułapek spamowych,
automatyczne dodawanie do czarnej listy HELO i zapobieganie losowemu
HELO.

%package -n perl-cbp
Summary:	Policyd "ClueBringer" Perl Libraries
Group:		Development/Languages/Perl

%description -n perl-cbp
Policyd "ClueBringer" Perl Libraries.

%package webui
Summary:	Policyd Web Administration
Group:		Applications/WWW
Requires:	php-pdo
Requires:	webapps
Requires:	webserver(access)
Requires:	webserver(alias)
Requires:	webserver(php)

%description webui
Policyd Web Administration.

%prep
%setup -q -n cluebringer-%{version}
%patch0 -p1

%build
cd database
for db_type in mysql4 mysql pgsql sqlite; do
	./convert-tsql $db_type core.tsql > policyd.$db_type.sql
	for file in $(find . -name '*.tsql' -and -not -name core.tsql); do
		./convert-tsql $db_type $file
	done >> policyd.$db_type.sql
	cd whitelists
		./parse-checkhelo-whitelist >> policyd.$db_type.sql
		./parse-greylisting-whitelist >> policyd.$db_type.sql
	cd ..
done

%install
rm -rf $RPM_BUILD_ROOT
# perl lib
install -d $RPM_BUILD_ROOT%{perl_vendorlib}
cp -a cbp $RPM_BUILD_ROOT%{perl_vendorlib}
# cbpolicyd
install -d $RPM_BUILD_ROOT{%{_sysconfdir}/policyd,%{_sbindir},/etc/{rc.d/init.d,sysconfig},/var/run/%{name}}
install -p cbpolicyd cbpadmin database/convert-tsql $RPM_BUILD_ROOT%{_sbindir}
cp -a cluebringer.conf $RPM_BUILD_ROOT%{_sysconfdir}/policyd/cluebringer.conf
install -p %{SOURCE4} $RPM_BUILD_ROOT/etc/rc.d/init.d/%{name}
cp -a %{SOURCE2} $RPM_BUILD_ROOT/etc/sysconfig/%{name}

# Webui
install -d $RPM_BUILD_ROOT{%{_webapps}/%{_webapp},%{_webappdir}}
cp -R webui/* $RPM_BUILD_ROOT%{_webappdir}
cp -a %{SOURCE1} $RPM_BUILD_ROOT%{_webapps}/%{_webapp}/apache.conf
cp -a $RPM_BUILD_ROOT%{_webapps}/%{_webapp}/{apache,httpd}.conf
# Move config into %{_sysconfdir}
mv $RPM_BUILD_ROOT%{_webappdir}/includes/config.php $RPM_BUILD_ROOT%{_webapps}/%{_webapp}
ln -s %{_webapps}/%{_webapp}/config.php $RPM_BUILD_ROOT%{_webappdir}/includes

%clean
rm -rf $RPM_BUILD_ROOT

%pre
%groupadd -g 121 -r policyd
%useradd -M -o -r -u 121 -d / -s /bin/false -g policyd -c "Postfix Policy Daemon" policyd

%post
/sbin/chkconfig --add policyd
%service policyd restart

%preun
if [ "$1" = "0" ]; then
	%service policyd stop
	/sbin/chkconfig --del policyd
fi

%postun
if [ "$1" = "0" ]; then
	%userremove policyd
	%groupremove policyd
fi

%triggerin webui -- apache1 < 1.3.37-3, apache1-base
%webapp_register apache %{_webapp}

%triggerun webui -- apache1 < 1.3.37-3, apache1-base
%webapp_unregister apache %{_webapp}

%triggerin webui -- apache < 2.2.0, apache-base
%webapp_register httpd %{_webapp}

%triggerun webui -- apache < 2.2.0, apache-base
%webapp_unregister httpd %{_webapp}

%triggerin webui -- lighttpd
%webapp_register lighttpd %{_webapp}

%triggerun webui -- lighttpd
%webapp_unregister lighttpd %{_webapp}

%files
%defattr(644,root,root,755)
%doc AUTHORS CHANGELOG INSTALL TODO WISHLIST
%doc database/*.sql
%doc contrib/amavisd-new
%attr(755,root,root) %{_sbindir}/cbpadmin
%attr(755,root,root) %{_sbindir}/cbpolicyd
%attr(755,root,root) %{_sbindir}/convert-tsql
%dir %attr(750,root,policyd) %{_sysconfdir}/%{name}
%config(noreplace) %verify(not md5 mtime size) %attr(640,root,policyd) %{_sysconfdir}/%{name}/cluebringer.conf
%attr(754,root,root) /etc/rc.d/init.d/%{name}
%config(noreplace) %verify(not md5 mtime size) /etc/sysconfig/%{name}
%dir %attr(775,root,policyd) /var/run/%{name}

%files -n perl-cbp
%defattr(644,root,root,755)
%{perl_vendorlib}/cbp

%files webui
%defattr(644,root,root,755)
%dir %attr(750,root,http) %{_webapps}/%{_webapp}
%attr(640,root,root) %config(noreplace) %verify(not md5 mtime size) %{_webapps}/%{_webapp}/apache.conf
%attr(640,root,root) %config(noreplace) %verify(not md5 mtime size) %{_webapps}/%{_webapp}/httpd.conf
%attr(640,root,http) %config(noreplace) %verify(not md5 mtime size) %{_webapps}/%{_webapp}/config.php
%{_webappdir}
