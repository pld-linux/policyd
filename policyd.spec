# $Id: policyd.spec,v 1.4 2005-11-15 12:58:57 hns Exp $
#
# TODO: optflags
#
# TODO: upgrade database smooth
# smart updates tables from older to newer version of policyd
#
# TODO: mysql and postfix info, see:
# /etc/rc.d/init.d/policyd init
#
# Not Finished Yet, reject STBR.
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
BuildRequires:	zlib-devel
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
Policyd to wtyczka antyspamowa dla Postfiksa obs�uguj�ca szare listy,
t�umienie (liczby lub obj�to�ci wiadomo�ci w ci�gu jednostki czasu)
oparte na nadawcy (wed�ug koperty, uwierzytelnienia SASL albo
hosta/IP), ograniczanie cz�stotliwo�ci dostarczania do nadawcy,
monitorowanie/dodawanie do czarnej listy pu�apek spamowych,
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
	echo "Run \"/etc/rc.d/init.d/policyd init\" to read howto setup policy daemon." >&2
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
%dir %{_sysconfdir}/%{name}
%doc *.txt *.mysql doc/*.sql doc/*.txt
%doc %{_sysconfdir}/%{name}/%{name}.conf-dist
%config(noreplace) %verify(not md5 mtime size) %attr(640,root,root) %{_sysconfdir}/%{name}/%{name}.conf
%config(noreplace) %verify(not md5 mtime size) %attr(755,root,root) /etc/cron.hourly/%{name}
%config(noreplace) %verify(not md5 mtime size) /etc/sysconfig/%{name}
%{_sysconfdir}/rc.d/init.d/%{name}

%changelog
* %{date} PLD Team <feedback@pld-linux.org>
All persons listed below can be reached at <cvs_login>@pld-linux.org

$Log: policyd.spec,v $
Revision 1.4  2005-11-15 12:58:57  hns
- policyd.init: show howto setup new policyd install (``init'' param)
- policyd.cron: move this to policyd.init (``cron'' param)
- work in progress..

Revision 1.3  2005/10/28 17:53:35  qboosh
- pl, cleanups, config flags fixes

Revision 1.2  2005/10/28 09:56:22  eothane
- up to 1.69, cosmetics ...

Revision 1.1  2005/10/28 08:29:43  eothane
- made by Mikolaj Kucharski <build[at]kompuart[dot]pl>
- NFY
