# $Id: policyd.spec,v 1.11 2010-12-20 15:08:25 glen Exp $
#
# TODO:
# - upgrade database smooth
#   smart updates tables from older to newer version of policyd
# TODO
# - mysql and postfix info, see:
#   /etc/rc.d/init.d/policyd init
#
Summary:	Policyd - an anti-spam plugin for Postfix
Summary(pl.UTF-8):	Policyd - wtyczka antyspamowa dla Postfiksa
Name:		policyd
Version:	2.0.10
Release:	0.1
License:	GPL v2
Group:		Networking
Source0:	http://downloads.sourceforge.net/policyd/cluebringer-%{version}.tar.bz2
# Source0-md5:	cdff8f8e7c0e95143f7108159aed80c6
Source1:	%{name}.cron
Source2:	%{name}.sysconfig
Source3:	%{name}.conf
Source4:	%{name}.init
URL:		http://www.policyd.org/
BuildRequires:	mysql-devel
BuildRequires:	zlib-devel
Requires(pre):	/bin/id
Requires(pre):	/usr/bin/getgid
Requires(pre):	/usr/sbin/groupadd
Requires(pre):	/usr/sbin/useradd
Requires(post,preun):	/sbin/chkconfig
Requires(postun):	/usr/sbin/groupdel
Requires(postun):	/usr/sbin/userdel
Requires:	rc-scripts
Provides:	group(policyd)
Provides:	user(policyd)
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

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

%prep
%setup -q -n cluebringer-%{version}

%build
%{__make} build \
	CC="%{__cc}" \
	CPPFLAGS="-I/usr/include/mysql" \
	CFLAGS="%{rpmcflags} -W -Wall -DMAXFDS=1023" \
	lib=

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT{%{_libdir}/%{name},%{_sysconfdir}/%{name},/etc/rc.d/init.d,/etc/sysconfig,/etc/cron.hourly}
install -p policyd cleanup $RPM_BUILD_ROOT%{_libdir}/%{name}
cp -a policyd.conf $RPM_BUILD_ROOT%{_sysconfdir}/%{name}/%{name}.conf-dist
cp -a %{SOURCE1} $RPM_BUILD_ROOT/etc/cron.hourly/%{name}
cp -a %{SOURCE2} $RPM_BUILD_ROOT/etc/sysconfig/%{name}
cp -a %{SOURCE3} $RPM_BUILD_ROOT%{_sysconfdir}/%{name}/%{name}.conf
install -p %{SOURCE4} $RPM_BUILD_ROOT/etc/rc.d/init.d/%{name}

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
%attr(754,root,root) /etc/rc.d/init.d/%{name}
