# $Id: policyd.spec,v 1.3 2005-10-28 17:53:35 qboosh Exp $
#
# TODO: optflags
# TODO: mysql info
# mysql> GRANT ALL ON policyd.* TO policyd@localhost IDENTIFIED BY 'secret_password';
# mysql> GRANT USAGE ON *.* TO policyd@localhost IDENTIFIED BY 'secret_password';
# $ zcat /usr/share/doc/policyd-%{Version}/DATABASE.mysql.gz | mysql -p -u policyd
#
# TODO: postfix info
#smtpd_recipient_restrictions =
#	permit_mynetworks
#	permit_sasl_authenticated
#	reject_unauth_destination
#	reject_unlisted_recipient
#	check_policy_service inet:127.0.0.1:10031
#
Summary:	Policyd - an anti-spam plugin for Postfix
Summary(pl):	Policyd - wtyczka antyspamowa dla Postfiksa
Name:		policyd
Version:	1.69
Release:	0.1
License:	GPL v2
Group:		Networking
Source0:	http://policyd.sourceforge.net/%{name}-v%{version}.tar.gz
# Source0-md5:	720b88e1f36728c255cc55ebade37ac2
Source1:	policyd.cron
Source2:	policyd.sysconfig
Source3:	policyd.conf
Source4:	policyd.init
URL:		http://policyd.sourceforge.net/
BuildRequires:	mysql-devel
Requires:	mysql-libs
Requires:	zlib
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%description
Policyd is an anti-spam plugin for Postfix that does greylisting,
sender-(envelope, SASL or host/IP)-based throttling (on messages
and/or volume per defined time unit), recipient rate limiting,
spamtrap monitoring/blacklisting, HELO auto blacklisting and HELO
randomization preventation.

%description -l pl
Policyd to wtyczka antyspamowa dla Postfiksa obs³uguj±ca szare listy,
t³umienie (liczby lub objêto¶ci wiadomo¶ci w ci±gu jednostki czasu)
oparte na nadawcy (wed³ug koperty, uwierzytelnienia SASL albo
hosta/IP), ograniczanie czêstotliwo¶ci dostarczania do nadawcy,
monitorowanie/dodawanie do czarnej listy pu³apek spamowych,
automatyczne dodawanie do czarnej listy HELO i zapobieganie losowemu
HELO.

%prep
%setup -q -n %{name}-v%{version}

%build
%{__make} build

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT{%{_libdir}/%{name},%{_sysconfdir}/%{name},/etc/rc.d/init.d,/etc/sysconfig,/etc/cron.hourly}
install policyd cleanup $RPM_BUILD_ROOT%{_libdir}/%{name}
install policyd.conf $RPM_BUILD_ROOT%{_sysconfdir}/%{name}/%{name}.conf-dist
install %{SOURCE1} $RPM_BUILD_ROOT/etc/cron.hourly/%{name}
install %{SOURCE2} $RPM_BUILD_ROOT/etc/sysconfig/%{name}
install %{SOURCE3} $RPM_BUILD_ROOT%{_sysconfdir}/%{name}/%{name}.conf
install %{SOURCE4} $RPM_BUILD_ROOT/etc/rc.d/init.d/%{name}

%clean
rm -rf $RPM_BUILD_ROOT

%pre
%groupadd -g 121 -r policyd
%useradd -M -o -r -u 121 -d / -s /bin/false -g policyd -c "Postfix Policy Daemon" policyd

%post
/sbin/chkconfig --add policyd
if [ -f /var/lock/subsys/policyd ]; then
	/etc/rc.d/init.d/policyd restart >&2 || :
else
	echo "Run \"/etc/rc.d/init.d/policyd start\" to start policy daemon." >&2
fi

%preun
if [ "$1" = "0" ]; then
	if [ -f /var/lock/subsys/policyd ]; then
		/etc/rc.d/init.d/policyd stop >&2
	fi
	/sbin/chkconfig --del policyd
fi

%postun
if [ "$1" = "0" ]; then
	%userremove policyd
	%groupremove policyd
fi

%files
%defattr(644,root,root,755)
%attr(755,root,root) %{_libdir}/%{name}/*
%doc *.txt *.mysql doc/*.sql doc/*.txt
%dir %{_sysconfdir}/%{name}
%config(noreplace) %verify(not md5 mtime size) %attr(640,root,root) %{_sysconfdir}/%{name}/%{name}.conf
# shouldn't be in %doc instead here?
%{_sysconfdir}/%{name}/%{name}.conf-dist
%{_sysconfdir}/rc.d/init.d/%{name}
%config(noreplace) %verify(not md5 mtime size) /etc/sysconfig/%{name}
%config(noreplace) %verify(not md5 mtime size) %attr(755,root,root) /etc/cron.hourly/%{name}

%changelog
* %{date} PLD Team <feedback@pld-linux.org>
All persons listed below can be reached at <cvs_login>@pld-linux.org

$Log: policyd.spec,v $
Revision 1.3  2005-10-28 17:53:35  qboosh
- pl, cleanups, config flags fixes

Revision 1.2  2005/10/28 09:56:22  eothane
- up to 1.69, cosmetics ...

Revision 1.1  2005/10/28 08:29:43  eothane
- made by Mikolaj Kucharski <build[at]kompuart[dot]pl>
- NFY
