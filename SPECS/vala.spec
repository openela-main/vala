%global api_ver 0.40
%global priority 90

Name:           vala
Version:        0.40.19
Release:        2%{?dist}
Summary:        A modern programming language for GNOME

# Most files are LGPLv2.1+, curses.vapi is 2-clause BSD
License:        LGPLv2+ and BSD
URL:            https://wiki.gnome.org/Projects/Vala
Source0:        https://download.gnome.org/sources/vala/0.40/vala-%{version}.tar.xz

BuildRequires:  flex
BuildRequires:  bison
BuildRequires:  glib2-devel
BuildRequires:  gobject-introspection-devel
BuildRequires:  graphviz-devel
BuildRequires:  libxslt
# only if Vala source files are patched
#BuildRequires:  vala

# for tests
BuildRequires:  dbus-x11

# alternatives
%global vala_binaries vala valac vala-gen-introspect vapigen
%global vala_manpages valac vala-gen-introspect vapigen
Requires(posttrans):   %{_sbindir}/alternatives
Requires(preun):       %{_sbindir}/alternatives

# For GLib-2.0 and GObject-2.0 .gir files
Requires: gobject-introspection-devel

# Removed in F25
Obsoletes: vala-tools < 0.34.0
Conflicts: vala-tools < 0.34.0
Provides: vala-tools = %{version}-%{release}

Provides: vala(api) = %{api_ver}

%description
Vala is a new programming language that aims to bring modern programming
language features to GNOME developers without imposing any additional
runtime requirements and without using a different ABI compared to
applications and libraries written in C.

valac, the Vala compiler, is a self-hosting compiler that translates
Vala source code into C source and header files. It uses the GObject
type system to create classes and interfaces declared in the Vala source
code. It's also planned to generate GIDL files when gobject-
introspection is ready.

The syntax of Vala is similar to C#, modified to better fit the GObject
type system.


%package        devel
Summary:        Development files for %{name}
Requires:       %{name}%{?_isa} = %{version}-%{release}

%description    devel
Vala is a new programming language that aims to bring modern programming
language features to GNOME developers without imposing any additional
runtime requirements and without using a different ABI compared to
applications and libraries written in C.

This package contains development files for %{name}. This is not
necessary for using the %{name} compiler.


%package        doc
Summary:        Documentation for %{name}
License:        LGPLv2+

BuildArch:      noarch
Requires:       %{name} = %{version}-%{release}
Requires:       devhelp

%description    doc
Vala is a new programming language that aims to bring modern programming
language features to GNOME developers without imposing any additional
runtime requirements and without using a different ABI compared to
applications and libraries written in C.

This package contains documentation in a devhelp HTML book.


%package -n     valadoc
Summary:        Vala documentation generator
Requires:       %{name}%{?_isa} = %{version}-%{release}

%description -n valadoc
Valadoc is a documentation generator for generating API documentation from Vala
source code.


%package -n     valadoc-devel
Summary:        Development files for valadoc
Requires:       valadoc%{?_isa} = %{version}-%{release}

%description -n valadoc-devel
Valadoc is a documentation generator for generating API documentation from Vala
source code.

The valadoc-devel package contains libraries and header files for
developing applications that use valadoc.


%prep
%autosetup -p1


%build
%configure
# Don't use rpath!
sed -i 's|/lib /usr/lib|/lib /usr/lib /lib64 /usr/lib64|' libtool
make %{?_smp_mflags}


%install
%make_install
# remove symlinks, using alternatives
for f in %{vala_binaries}
do
    rm $RPM_BUILD_ROOT%{_bindir}/$f
    touch $RPM_BUILD_ROOT%{_bindir}/$f
done
for f in %{vala_manpages}
do
    rm $RPM_BUILD_ROOT%{_mandir}/man1/$f.1*
    touch $RPM_BUILD_ROOT%{_mandir}/man1/$f.1.gz
done

# Avoid multilib conflicts in vala-gen-introspect
mv %{buildroot}%{_bindir}/vala-gen-introspect-%{api_ver}{,-`uname -m`}
echo -e '#!/bin/sh\nexec %{_bindir}/vala-gen-introspect-%{api_ver}-`uname -m` "$@"' > \
  %{buildroot}%{_bindir}/vala-gen-introspect-%{api_ver}
  chmod +x %{buildroot}%{_bindir}/vala-gen-introspect-%{api_ver}

# own this directory for third-party *.vapi files
mkdir -p $RPM_BUILD_ROOT%{_datadir}/vala/vapi
find %{buildroot} -name '*.la' -exec rm -f {} ';'


%check
make check


%posttrans
for f in %{vala_binaries};
do
    %{_sbindir}/alternatives --install %{_bindir}/$f \
      $f %{_bindir}/$f-%{api_ver} %{priority} || :
done
for f in %{vala_manpages};
do
    %{_sbindir}/alternatives --install %{_mandir}/man1/$f.1.gz \
      $f.1.gz %{_mandir}/man1/$f-%{api_ver}.1.gz %{priority} || :
done

%preun
for f in %{vala_binaries};
do
    %{_sbindir}/alternatives --remove $f \
      %{_bindir}/$f-%{api_ver} || :
done
for f in %{vala_manpages};
do
    %{_sbindir}/alternatives --remove $f.1.gz \
      %{_mandir}/man1/$f-%{api_ver}.1.gz || :
done


%files
%license COPYING
%ghost %{_bindir}/vala
%ghost %{_bindir}/valac
%ghost %{_bindir}/vala-gen-introspect
%ghost %{_bindir}/vapigen
%{_bindir}/vala-%{api_ver}
%{_bindir}/valac-%{api_ver}
%{_bindir}/vala-gen-introspect-%{api_ver}*
%{_bindir}/vapigen-%{api_ver}
%{_libdir}/pkgconfig/vapigen*.pc
%{_libdir}/vala-%{api_ver}/
%{_libdir}/libvala-%{api_ver}.so.*
%{_datadir}/aclocal/vala.m4
%{_datadir}/aclocal/vapigen.m4
%{_datadir}/vala/
%{_datadir}/vala-%{api_ver}/
%ghost %{_mandir}/man1/valac.1.gz
%ghost %{_mandir}/man1/vala-gen-introspect.1.gz
%ghost %{_mandir}/man1/vapigen.1.gz
%{_mandir}/man1/valac-%{api_ver}.1.gz
%{_mandir}/man1/vala-gen-introspect-%{api_ver}.1.gz
%{_mandir}/man1/vapigen-%{api_ver}.1.gz

%files devel
%{_includedir}/vala-%{api_ver}
%{_libdir}/libvala-%{api_ver}.so
%{_libdir}/pkgconfig/libvala-%{api_ver}.pc

%files doc
%doc %{_datadir}/devhelp/books/vala-%{api_ver}

%files -n valadoc
%{_bindir}/valadoc
%{_bindir}/valadoc-%{api_ver}
%{_libdir}/libvaladoc-%{api_ver}.so.0*
%{_libdir}/valadoc/
%{_datadir}/valadoc/
%{_mandir}/man1/valadoc-%{api_ver}.1*
%{_mandir}/man1/valadoc.1*

%files -n valadoc-devel
%{_includedir}/valadoc-%{api_ver}/
%{_libdir}/libvaladoc-%{api_ver}.so
%{_libdir}/pkgconfig/valadoc-%{api_ver}.pc


%changelog
* Fri Jan 15 2021 Kalev Lember <klember@redhat.com> - 0.40.19-2
- Fix multilib conflicts in vala-gen-introspect
- Resolves: #1853170

* Mon Feb 17 2020 Kalev Lember <klember@redhat.com> - 0.40.19-1
- Update to 0.40.19
- Resolves: #1753520

* Tue Nov 19 2019 Kalev Lember <klember@redhat.com> - 0.40.18-1
- Update to 0.40.18
- Resolves: #1753520

* Mon Nov 18 2019 Kalev Lember <klember@redhat.com> - 0.40.17-1
- Update to 0.40.17
- Resolves: #1753520

* Tue Oct 16 2018 Kalev Lember <klember@redhat.com> - 0.40.10-1
- Update to 0.40.10

* Wed Jul 25 2018 Kalev Lember <klember@redhat.com> - 0.40.8-1
- Update to 0.40.8

* Tue Jun 26 2018 Kalev Lember <klember@redhat.com> - 0.40.7-1
- Update to 0.40.7

* Mon May 21 2018 Kalev Lember <klember@redhat.com> - 0.40.6-1
- Update to 0.40.6

* Mon May 21 2018 Kalev Lember <klember@redhat.com> - 0.40.5-1
- Update to 0.40.5

* Mon Apr 16 2018 Kalev Lember <klember@redhat.com> - 0.40.4-1
- Update to 0.40.4

* Sun Apr 08 2018 Kalev Lember <klember@redhat.com> - 0.40.3-1
- Update to 0.40.3

* Wed Mar 28 2018 Kalev Lember <klember@redhat.com> - 0.40.2-1
- Update to 0.40.2

* Mon Mar 26 2018 Kalev Lember <klember@redhat.com> - 0.40.1-1
- Update to 0.40.1

* Sun Mar 11 2018 Kalev Lember <klember@redhat.com> - 0.40.0-1
- Update to 0.40.0

* Fri Mar 02 2018 Kalev Lember <klember@redhat.com> - 0.39.92-1
- Update to 0.39.92

* Fri Feb 09 2018 Fedora Release Engineering <releng@fedoraproject.org> - 0.39.7-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_28_Mass_Rebuild

* Sun Feb 04 2018 Kalev Lember <klember@redhat.com> - 0.39.7-1
- Update to 0.39.7

* Tue Jan 30 2018 Kalev Lember <klember@redhat.com> - 0.39.6-1
- Update to 0.39.6
- Drop ldconfig scriptlets

* Fri Jan 19 2018 Kalev Lember <klember@redhat.com> - 0.39.5-1
- Update to 0.39.5

* Wed Jan 03 2018 Kalev Lember <klember@redhat.com> - 0.39.3-1
- Update to 0.39.3

* Wed Dec 20 2017 Kalev Lember <klember@redhat.com> - 0.39.2-1
- Update to 0.39.2

* Mon Dec 11 2017 Kalev Lember <klember@redhat.com> - 0.38.4-1
- Update to 0.38.4

* Thu Nov 09 2017 Kalev Lember <klember@redhat.com> - 0.38.3-1
- Update to 0.38.3

* Sun Oct 08 2017 Kalev Lember <klember@redhat.com> - 0.38.2-1
- Update to 0.38.2

* Mon Sep 11 2017 Kalev Lember <klember@redhat.com> - 0.38.1-1
- Update to 0.38.1

* Fri Sep 08 2017 Kalev Lember <klember@redhat.com> - 0.38.0-2
- Backport a patch to fix baobab (bgo#787419)

* Tue Sep 05 2017 Kalev Lember <klember@redhat.com> - 0.38.0-1
- Update to 0.38.0

* Mon Aug 28 2017 Kalev Lember <klember@redhat.com> - 0.37.91-1
- Update to 0.37.91

* Mon Aug 21 2017 Kalev Lember <klember@redhat.com> - 0.37.90-1
- Update to 0.37.90

* Thu Aug 10 2017 Kalev Lember <klember@redhat.com> - 0.37.2-1
- Update to 0.37.2

* Thu Aug 03 2017 Fedora Release Engineering <releng@fedoraproject.org> - 0.36.4-5
- Rebuilt for https://fedoraproject.org/wiki/Fedora_27_Binutils_Mass_Rebuild

* Thu Jul 27 2017 Fedora Release Engineering <releng@fedoraproject.org> - 0.36.4-4
- Rebuilt for https://fedoraproject.org/wiki/Fedora_27_Mass_Rebuild

* Wed Jul 19 2017 Kalev Lember <klember@redhat.com> - 0.36.4-3
- Enable self tests

* Wed Jul 19 2017 Kalev Lember <klember@redhat.com> - 0.36.4-2
- Rebuilt for a s390x binutils issue

* Tue Jul 18 2017 Kalev Lember <klember@redhat.com> - 0.36.4-1
- Update to 0.36.4

* Fri May 05 2017 Kalev Lember <klember@redhat.com> - 0.36.3-1
- Update to 0.36.3

* Tue Apr 25 2017 Kalev Lember <klember@redhat.com> - 0.36.2-1
- Update to 0.36.2

* Mon Apr 03 2017 Kalev Lember <klember@redhat.com> - 0.36.1-1
- Update to 0.36.1

* Mon Mar 20 2017 Kalev Lember <klember@redhat.com> - 0.36.0-1
- Update to 0.36.0

* Thu Mar 16 2017 Kalev Lember <klember@redhat.com> - 0.35.90-1
- Update to 0.35.90

* Tue Mar 07 2017 Kalev Lember <klember@redhat.com> - 0.35.7-1
- Update to 0.35.7

* Mon Feb 27 2017 Kalev Lember <klember@redhat.com> - 0.35.6-1
- Update to 0.35.6

* Tue Feb 14 2017 Richard Hughes <rhughes@redhat.com> - 0.35.5-1
- Update to 0.35.5

* Mon Feb 13 2017 Richard Hughes <rhughes@redhat.com> - 0.35.3-1
- Update to 0.35.3

* Sat Feb 11 2017 Fedora Release Engineering <releng@fedoraproject.org> - 0.34.4-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_26_Mass_Rebuild

* Mon Dec 05 2016 Kalev Lember <klember@redhat.com> - 0.34.4-1
- Update to 0.34.4

* Fri Dec 02 2016 Kalev Lember <klember@redhat.com> - 0.34.3-3
- Backport a patch to support fixed-size array as return-value (#1398738)

* Thu Dec 01 2016 Kalev Lember <klember@redhat.com> - 0.34.3-2
- codegen: Add function-prototypes for all register-type calls

* Tue Nov 22 2016 Kalev Lember <klember@redhat.com> - 0.34.3-1
- Update to 0.34.3

* Mon Oct 24 2016 Kalev Lember <klember@redhat.com> - 0.34.2-1
- Update to 0.34.2

* Sun Oct 09 2016 Kalev Lember <klember@redhat.com> - 0.34.1-1
- Update to 0.34.1

* Wed Sep 28 2016 Kalev Lember <klember@redhat.com> - 0.34.0-4
- Make scriptlets failsafe (#1247971)

* Thu Sep 22 2016 Kalev Lember <klember@redhat.com> - 0.34.0-3
- Require gobject-introspection-devel for GLib and GObject .gir files
- Drop old obsoletes

* Thu Sep 22 2016 Kalev Lember <klember@redhat.com> - 0.34.0-2
- Merge vala-tools into main vala package

* Thu Sep 22 2016 Kalev Lember <klember@redhat.com> - 0.34.0-1
- Update to 0.34.0

* Tue Sep 13 2016 Kalev Lember <klember@redhat.com> - 0.33.1-1
- Update to 0.33.1
- Update project URLs

* Wed Jun 22 2016 Richard Hughes <rhughes@redhat.com> - 0.32.1-1
- Update to 0.32.1

* Tue Mar 22 2016 Kalev Lember <klember@redhat.com> - 0.32.0-1
- Update to 0.32.0

* Tue Feb 16 2016 Richard Hughes <rhughes@redhat.com> - 0.31.1-1
- Update to 0.31.1

* Fri Feb 05 2016 Fedora Release Engineering <releng@fedoraproject.org> - 0.30.0-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_24_Mass_Rebuild

* Fri Sep 18 2015 Kalev Lember <klember@redhat.com> - 0.30.0-1
- Update to 0.30.0

* Wed Aug 12 2015 Kalev Lember <klember@redhat.com> - 0.29.3-1
- Update to 0.29.3

* Mon Jun 29 2015 Kalev Lember <klember@redhat.com> - 0.29.2-1
- Update to 0.29.2

* Fri Jun 19 2015 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.29.1-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_23_Mass_Rebuild

* Wed May 27 2015 Kalev Lember <kalevlember@gmail.com> - 0.29.1-1
- Update to 0.29.1

* Mon May 25 2015 Kalev Lember <kalevlember@gmail.com> - 0.28.0-2
- Add a vala(api) virtual provide that xfce-vala can depend on

* Sun Mar 22 2015 Kalev Lember <kalevlember@gmail.com> - 0.28.0-1
- Update to 0.28.0

* Wed Mar 18 2015 Kalev Lember <kalevlember@gmail.com> - 0.27.2-1
- Update to 0.27.2
- Use license macro for the COPYING file

* Sat Feb 21 2015 Kalev Lember <kalevlember@gmail.com> - 0.27.1-2
- Drop emacs bindings that no longer build

* Mon Jan 19 2015 Richard Hughes <rhughes@redhat.com> - 0.27.1-1
- Update to 0.27.1

* Sun Nov 16 2014 Kalev Lember <kalevlember@gmail.com> - 0.26.1-2
- Obsolete compat-vala022 from rhughes-f20-gnome-3-12 copr

* Mon Oct 13 2014 Kalev Lember <kalevlember@gmail.com> - 0.26.1-1
- Update to 0.26.1

* Mon Sep 22 2014 Kalev Lember <kalevlember@gmail.com> - 0.26.0-1
- Update to 0.26.0

* Mon Sep 15 2014 Kalev Lember <kalevlember@gmail.com> - 0.25.4-1
- Update to 0.25.4

* Mon Sep 01 2014 Kalev Lember <kalevlember@gmail.com> - 0.25.3-1
- Update to 0.25.3

* Sun Aug 24 2014 Kalev Lember <kalevlember@gmail.com> - 0.25.2-1
- Update to 0.25.2

* Mon Aug 18 2014 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.25.1-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_21_22_Mass_Rebuild

* Wed Jul 23 2014 Kalev Lember <kalevlember@gmail.com> - 0.25.1-1
- Update to 0.25.1

* Fri Jun 27 2014 Yaakov Selkowitz <yselkowi@redhat.com> - 0.24.0-3
- Fix clutter-gst-1.0 deps (#1106673, #1112424)

* Sun Jun 08 2014 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.24.0-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_21_Mass_Rebuild

* Mon Mar 24 2014 Richard Hughes <rhughes@redhat.com> - 0.24.0-1
- Update to 0.24.0

* Thu Feb 20 2014 Kalev Lember <kalevlember@gmail.com> - 0.23.3-2
- Move Makefile.vapigen to the -tools subpackage (#1030543)
- Don't ship huge ChangeLog file

* Wed Feb 19 2014 Richard Hughes <rhughes@redhat.com> - 0.23.3-1
- Update to 0.23.3

* Wed Feb 05 2014 Richard Hughes <rhughes@redhat.com> - 0.23.2-1
- Update to 0.23.2

* Sun Jan 26 2014 Peter Robinson <pbrobinson@fedoraproject.org> 0.23.1-2
- Fix FTBFS

* Wed Jan 08 2014 Richard Hughes <rhughes@redhat.com> - 0.23.1-1
- Update to 0.23.1

* Thu Nov 14 2013 Richard Hughes <rhughes@redhat.com> - 0.22.1-1
- Update to 0.22.1

* Wed Sep 25 2013 Kalev Lember <kalevlember@gmail.com> - 0.22.0-1
- Update to 0.22.0

* Wed Sep 18 2013 Kalev Lember <kalevlember@gmail.com> - 0.21.2-1
- Update to 0.21.2

* Mon Aug 19 2013 Kalev Lember <kalevlember@gmail.com> - 0.21.1-1
- Update to 0.21.1

* Sun Aug 04 2013 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.20.1-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_20_Mass_Rebuild

* Tue Apr  9 2013 Michel Salim <salimma@fedoraproject.org> - 0.20.1-1
- Update to 0.20.1

* Tue Mar 26 2013 Kalev Lember <kalevlember@gmail.com> - 0.20.0-1
- Update to 0.20.0

* Thu Feb 28 2013 Colin Walters <walters@verbum.org> - 0.19.0-2
- Ensure tools pull in gobject-introspection-devel, since vapigen
  needs .gir files.

* Fri Feb 22 2013 Kalev Lember <kalevlember@gmail.com> - 0.19.0-1
- Update to 0.19.0

* Wed Feb 20 2013 Kalev Lember <kalevlember@gmail.com> - 0.18.1-4
- Temporarily BR vala itself to build with the patch applied

* Wed Feb 20 2013 Kalev Lember <kalevlember@gmail.com> - 0.18.1-3
- Ignore the "instance-parameter" tag emitted by new g-ir-scanner

* Fri Feb 15 2013 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.18.1-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_19_Mass_Rebuild

* Tue Nov 13 2012 Kalev Lember <kalevlember@gmail.com> - 0.18.1-1
- Update to 0.18.1

* Tue Sep 25 2012 Kalev Lember <kalevlember@gmail.com> - 0.18.0-1
- Update to 0.18.0

* Wed Sep 19 2012 Kalev Lember <kalevlember@gmail.com> - 0.17.7-1
- Update to 0.17.7

* Sat Sep  8 2012 Michel Salim <salimma@fedoraproject.org> - 0.17.6-1
- Update to 0.17.6

* Sun Sep  2 2012 Michel Salim <salimma@fedoraproject.org> - 0.17.5-1
- Update to 0.17.5

* Mon Aug 20 2012 Michel Salim <salimma@fedoraproject.org> - 0.17.4-1
- Update to 0.17.4

* Fri Aug  3 2012 Michel Salim <salimma@fedoraproject.org> - 0.17.3-1
- Update to 0.17.3

* Sun Jul 22 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.17.2-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_18_Mass_Rebuild

* Mon Jun 25 2012 Michel Salim <salimma@fedoraproject.org> - 0.17.2-1
- Update to 0.17.2

* Mon Jun  4 2012 Michel Salim <salimma@fedoraproject.org> - 0.17.1-1
- Update to 0.17.1
- Remove "Group" field
- Make subpackages' dependencies on main package arch-specific

* Sat May 12 2012 Michel Salim <salimma@fedoraproject.org> - 0.17.0-2
- Spec clean-ups

* Thu May  3 2012 Michel Salim <salimma@fedoraproject.org> - 0.17.0-1
- Update to 0.17.0

* Fri Apr  6 2012 Michel Salim <salimma@fedoraproject.org> - 0.16.0-3
- Disable coverage analysis, build-time paths get hard-coded

* Thu Apr  5 2012 Michel Salim <salimma@fedoraproject.org> - 0.16.0-2
- Update vala-mode.el to April 2011 release
- Fix registration of Vala alternatives

* Wed Apr 04 2012 Kalev Lember <kalevlember@gmail.com> - 0.16.0-1
- Update to 0.16.0

* Tue Mar 27 2012 Ray Strode <rstrode@redhat.com> 0.15.2-2
- Add back Makefile.vapigen.  It's needed by various projects
  build systems to enable vala support.

* Wed Mar 21 2012 Richard Hughes <rhughes@redhat.com> - 0.15.2-1
- Update to 0.15.2

* Mon Feb  6 2012 Michel Salim <salimma@fedoraproject.org> - 0.15.1-3
- Enable coverage analysis
- Drop redundant --enable-vapigen, it's now the default

* Fri Feb  3 2012 Michel Salim <salimma@fedoraproject.org> - 0.15.1-2
- Support parallel installation with other Vala versions

* Mon Jan 30 2012 Michel Salim <salimma@fedoraproject.org> - 0.15.1-1
- Update to 0.15.1

* Sat Jan 14 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.15.0-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_17_Mass_Rebuild

* Fri Dec 23 2011 Matthias Clasen <mclasen@redhat.com> - 0.15.0-1
- Update to 0.15.0

* Tue Sep 20 2011 Matthias Clasen <mclasen@redhat.com> - 0.14.0-1
- Update to 0.14.0

* Tue Aug 30 2011 Matthias Clasen <mclasen@redhat.com> - 0.13.3-1
- Update to 0.13.3

* Thu Jul  7 2011 Michel Salim <salimma@fedoraproject.org> - 0.13.1-1
- Update to 0.13.1

* Fri Jun 17 2011 Tomas Bzatek <tbzatek@redhat.com> - 0.12.1-1
- Update to 0.12.1

* Tue Apr  5 2011 Michel Salim <salimma@fedoraproject.org> - 0.12.0-2
- Allow access to length of constant array in constant initializer lists

* Sun Apr  3 2011 Christopher Aillon <caillon@redhat.com> - 0.12.0-1
- Update to 0.12.0

* Thu Mar 17 2011 Michel Salim <salimma@fedoraproject.org> - 0.11.7-1
- Update to 0.11.7

* Mon Feb 21 2011 Peter Robinson <pbrobinson@gmail.com> - 0.11.6-1
- Update to 0.11.6

* Mon Feb 07 2011 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.11.5-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_15_Mass_Rebuild

* Mon Feb  7 2011 Michel Salim <salimma@fedoraproject.org> - 0.11.5-2
- Own %%{_datadir}/vala directory (# 661603)

* Wed Feb  2 2011 Christopher Aillon <caillon@redhat.com> - 0.11.5-1
- Update to 0.11.5

* Mon Jan 17 2011 Matthias Clasen <mclasen@redhat.com> - 0.11.4-1
- Update to 0.11.4

* Fri Jan  7 2011 Peter Robinson <pbrobinson@gmail.com> - 0.11.3-1
- Update to 0.11.3
- disable make check as its currently broken

* Tue Nov  9 2010 Peter Robinson <pbrobinson@gmail.com> - 0.11.2-1
- Update to 0.11.2

* Sun Nov  7 2010 Michel Salim <salimma@fedoraproject.org> - 0.11.1-2
- Improved rpath handling, allowing test suite to run

* Sat Nov  6 2010 Michel Salim <salimma@fedoraproject.org> - 0.11.1-1
- Update to 0.11.1
- Drop unneeded build requirements

* Tue Oct 19 2010 Michel Salim <salimma@fedoraproject.org> - 0.11.0-1
- Update to 0.11.0

* Wed Sep 29 2010 jkeating - 0.10.0-2
- Rebuilt for gcc bug 634757

* Wed Sep 22 2010 Matthias Clasen <mclasen@redhat.com> - 0.10.0-1
- Update to 0.10.0
- Work with gobject-introspection >= 0.9.5

* Sun Sep 12 2010 Michel Salim <salimma@fedoraproject.org> - 0.9.8-1
- Update to 0.9.8
- Make -doc subpackage noarch
- Mark -doc files as %%doc

* Wed Aug 25 2010 Brian Pepple <bpepple@fedoraproject.org> - 0.9.7-1
- Update to 0.9.7.
- Remove clean section & buildroot. No longer needed.

* Mon Aug  9 2010 Michel Salim <salimma@fedoraproject.org> - 0.9.5-1
- Update to 0.9.5

* Mon Aug  2 2010 Peter Robinson <pbrobinson@gmail.com> - 0.9.4-1
- Update to 0.9.4

* Thu Jul 15 2010 Michel Salim <salimma@fedoraproject.org> - 0.9.3-1
- Update to 0.9.3

* Mon Jul 12 2010 Michel Salim <salimma@fedoraproject.org> - 0.9.2-2
- Add COPYING file to emacs-vala

* Sat Jul  3 2010 Michel Salim <salimma@fedoraproject.org> - 0.9.2-1
- Update to 0.9.2

* Sun Jun 13 2010 Michel Salim <salimma@fedoraproject.org> - 0.9.1-1
- Update to 0.9.1
- Make emacs-vala subpackage noarch; split off source file to -el subpackage
  according to Emacs packaging guidelines

* Tue Apr 27 2010 Michel Salim <salimma@fedoraproject.org> - 0.8.1-1
- Update to 0.8.1

* Fri Apr  9 2010 Peter Robinson <pbrobinson@gmail.com> - 0.8.0-1
- Update to new major release 0.8.0

* Tue Mar  2 2010 Peter Robinson <pbrobinson@gmail.com> - 0.7.10-1
- Update to 0.7.10

* Tue Jan  5 2010 Peter Robinson <pbrobinson@gmail.com> - 0.7.9-1
- Update to 0.7.9

* Tue Nov 17 2009 Peter Robinson <pbrobinson@gmail.com> - 0.7.8-1
- Update to 0.7.8

* Sat Oct  3 2009 Michel Salim <salimma@fedoraproject.org> - 0.7.7-1
- Update to 0.7.7

* Thu Aug 20 2009 Michel Salim <salimma@fedoraproject.org> - 0.7.5-1
- Update to 0.7.5

* Sun Jul 26 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.7.4-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_12_Mass_Rebuild

* Tue Jul 14 2009 Michel Salim <salimma@fedoraproject.org> - 0.7.4-2
- Patch broken ModuleInit attribute (upstream bug 587444)

* Tue Jul  7 2009 Michel Salim <salimma@fedoraproject.org> - 0.7.4-1
- Update to 0.7.4

* Wed Jun  3 2009 Peter Robinson <pbrobinson@gmail.com> - 0.7.3-1
- Update to 0.7.3

* Sat Apr 18 2009 Michel Salim <salimma@fedoraproject.org> - 0.6.1-1
- Update to 0.6.1

* Mon Feb 23 2009 Michel Salim <salimma@fedoraproject.org> - 0.5.7-1
- Update to 0.5.7

* Tue Jan 27 2009 Michel Salim <salimma@fedoraproject.org> - 0.5.6-1
- Update to 0.5.6

* Tue Dec 16 2008 Michel Salim <salimma@fedoraproject.org> - 0.5.3-1
- Update to 0.5.3

* Mon Dec 15 2008 Michel Salim <salimma@fedoraproject.org> - 0.5.2-3
- Fix bug in Emacs version detection

* Sat Dec 13 2008 Michel Salim <salimma@fedoraproject.org> - 0.5.2-2
- Use buildsystem variables to determine available Emacs version
- BR on gecko-devel >= 1.9, since older version is also in RHEL repo

* Sat Dec 13 2008 Michel Salim <salimma@fedoraproject.org> - 0.5.2-1
- Update to 0.5.2

* Sun Nov 23 2008 Michel Salim <salimma@fedoraproject.org> - 0.5.1-1
- Update to 0.5.1

* Fri Aug 22 2008 Michel Salim <salimma@fedoraproject.org> - 0.3.5-1
- Update to 0.3.5

* Tue Jul 15 2008 Michel Salim <salimma@fedoraproject.org> - 0.3.4-2
- Add vala-mode for editing Vala code in Emacs

* Tue Jul  1 2008 Lennart Poettering <lpoetter@redhat.com> - 0.3.4-1
- Update to 0.3.4

* Wed Jun  4 2008 Michel Salim <salimma@fedoraproject.org> - 0.3.3-1
- Update to 0.3.3

* Fri May 16 2008 Michel Salim <salimma@fedoraproject.org> - 0.3.2-1
- Update to 0.3.2

* Thu Apr 10 2008 Michel Salim <salimma@fedoraproject.org> - 0.2.0-1
- Update to 0.2.0

* Wed Mar  5 2008 Michel Salim <salimma@fedoraproject.org> - 0.1.7-1
- Update to 0.1.7
- -tool subpackage now requires gnome-common, intltool and libtoolize
  for out-of-the-box vala-gen-project support

* Tue Feb 19 2008 Fedora Release Engineering <rel-eng@fedoraproject.org> - 0.1.6-2
- Autorebuild for GCC 4.3

* Sat Jan 19 2008 Michel Salim <salimma@fedoraproject.org> - 0.1.6-1
- Update to 0.1.6
- Revert vapi addition, needed declarations have been inlined (r846)
- Rename -docs subpackage to -doc, to comply with guidelines

* Tue Jan 15 2008 Michel Salim <salimma@fedoraproject.org> - 0.1.5-5
- Manually add Gee vapi file to package (bz #428692)

* Tue Dec  4 2007 Michel Salim <salimma@fedoraproject.org> - 0.1.5-4
- Backport patch to autodetect location of automake shared files

* Tue Dec  4 2007 Michel Salim <salimma@fedoraproject.org> - 0.1.5-3
- Add build dependency on gtk2-devel

* Tue Dec  4 2007 Michel Salim <salimma@fedoraproject.org> - 0.1.5-2
- Enable project generator tool

* Tue Nov 27 2007 Michel Salim <salimma@fedoraproject.org> - 0.1.5-1
- Update to 0.1.5

* Sun Nov 11 2007 Michel Salim <salimma@fedoraproject.org> - 0.1.4-2
- Add build dependency on devhelp

* Fri Oct 19 2007 Michel Salim <salimma@fedoraproject.org> - 0.1.4-1
- Update to 0.1.4
- Put newly-added documentation in its own subpackage (depends on devhelp)

* Mon Sep 17 2007 Michel Salim <salimma@fedoraproject.org> - 0.1.3-5
- vapigen subpackage: add missing Require: on perl-XML-Twig

* Sat Sep  8 2007 Michel Salim <salimma@fedoraproject.org> - 0.1.3-4
- Split -vapigen subpackage. It is functionally self-contained and the license
  is more restricted
- Updated license declarations

* Wed Sep  5 2007 Michel Salim <salimma@fedoraproject.org> - 0.1.3-3
- Licensing and URL updates

* Tue Sep  4 2007 Michel Salim <salimma@fedoraproject.org> - 0.1.3-2
- Enable binding generation tools

* Sun Sep  2 2007 Michel Salim <salimma@fedoraproject.org> - 0.1.3-1
- Update to 0.1.3

* Sun Mar 25 2007 Michel Salim <salimma@fedoraproject.org> - 0.0.8-1
- Update to 0.0.8

* Wed Mar  7 2007 Michel Salim <salimma@fedoraproject.org> - 0.0.7-1
- Update to 0.0.7

* Wed Feb 28 2007 Michel Salim <salimma@fedoraproject.org> - 0.0.6-1
- Update to 0.0.6

* Mon Nov  6 2006 Michel Salim <salimma@fedoraproject.org> - 0.0.5-1
- Initial package
