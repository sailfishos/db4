%define __soversion 4.8

# switch back to md5 file digests (due to rpm) until the dust settles a bit
%define _source_filedigest_algorithm 0
%define _binary_filedigest_algorithm 0

Summary: The Berkeley DB database library (version 4) for C
Name: db4
Version: 4.8.30
Release: 5
Source0: http://download.oracle.com/berkeley-db/db-%{version}.tar.gz
# other patches
Patch24: db-4.5.20-jni-include-dir.patch
Patch25: db-4-remove-timestamp.patch
Patch26: db4-aarch64.patch
Patch27: db-4.8.30-format-security.patch
Patch28: db-4.8.30-atomic_compare_exchange.patch
URL: https://git.sailfishos.org/mer-core/db4
License: BSD
Group: System/Libraries
BuildRequires: perl, libtool, util-linux

%description
The Berkeley Database (Berkeley DB) is a programmatic toolkit that
provides embedded database support for both traditional and
client/server applications. The Berkeley DB includes B+tree, Extended
Linear Hashing, Fixed and Variable-length record access methods,
transactions, locking, logging, shared memory caching, and database
recovery. The Berkeley DB supports C, C++, Java, and Perl APIs. It is
used by many applications, including Python and Perl, so this should
be installed on all systems.

%package cxx
Summary: The Berkeley DB database library (version 4) for C++
Group: System/Libraries

%description cxx
The Berkeley Database (Berkeley DB) is a programmatic toolkit that
provides embedded database support for both traditional and
client/server applications. The Berkeley DB includes B+tree, Extended
Linear Hashing, Fixed and Variable-length record access methods,
transactions, locking, logging, shared memory caching, and database
recovery. The Berkeley DB supports C, C++, Java, and Perl APIs. It is
used by many applications, including Python and Perl, so this should
be installed on all systems.

%package utils
Summary: Command line tools for managing Berkeley DB (version 4) databases
Group: Applications/Databases
Requires: db4 = %{version}-%{release}

%description utils
The Berkeley Database (Berkeley DB) is a programmatic toolkit that
provides embedded database support for both traditional and
client/server applications. Berkeley DB includes B+tree, Extended
Linear Hashing, Fixed and Variable-length record access methods,
transactions, locking, logging, shared memory caching, and database
recovery. DB supports C, C++, Java and Perl APIs.

%package devel
Summary: C development files for the Berkeley DB (version 4) library
Group: Development/Libraries
Requires: db4 = %{version}-%{release}

%description devel
The Berkeley Database (Berkeley DB) is a programmatic toolkit that
provides embedded database support for both traditional and
client/server applications. This package contains the header files,
libraries, and documentation for building programs which use the
Berkeley DB.

%package devel-static
Summary: Berkeley DB (version 4) static libraries
Group: Development/Libraries

%description devel-static
The Berkeley Database (Berkeley DB) is a programmatic toolkit that
provides embedded database support for both traditional and
client/server applications. This package contains static libraries
needed for applications that require statical linking of
Berkeley DB.

%package tcl
Summary: Development files for using the Berkeley DB (version 4) with tcl
Group: Development/Libraries
Requires: %{name} = %{version}-%{release}

%description tcl
The Berkeley Database (Berkeley DB) is a programmatic toolkit that
provides embedded database support for both traditional and
client/server applications. This package contains the libraries
for building programs which use the Berkeley DB in Tcl.

%prep
%setup -q -n db-%{version}
%patch24 -p1 -b .4.5.20.jni
%patch25 -p1 -b .4timestamp
%patch26 -p1
%patch27 -p1 -b .format-security
%patch28 -p1 -b .atomic_cmpx

# Remove tags files which we don't need.

cd dist
./s_config

%build
CFLAGS="$RPM_OPT_FLAGS -fno-strict-aliasing"; export CFLAGS

build() {
	test -d dist/$1 || mkdir dist/$1

	pushd dist
	popd
	pushd dist/$1
	ln -sf ../configure .
	# XXX --enable-diagnostic should be disabled for production (but is
	# useful).
	# XXX --enable-debug_{r,w}op should be disabled for production.
	%configure -C \
		--enable-shared --enable-static \
		--enable-cxx \
		--disable-java \
		# --enable-diagnostic \
		# --enable-debug --enable-debug_rop --enable-debug_wop \

	# Remove libtool predep_objects and postdep_objects wonkiness so that
	# building without -nostdlib doesn't include them twice.  Because we
	# already link with g++, weird stuff happens if you don't let the
	# compiler handle this.
	perl -pi -e 's/^predep_objects=".*$/predep_objects=""/' libtool
	perl -pi -e 's/^postdep_objects=".*$/postdep_objects=""/' libtool
	perl -pi -e 's/-shared -nostdlib/-shared/' libtool

	make %{?_smp_mflags}

	popd
}

build dist-tls

%install
rm -rf ${RPM_BUILD_ROOT}
mkdir -p ${RPM_BUILD_ROOT}%{_includedir}
mkdir -p ${RPM_BUILD_ROOT}%{_libdir}

%makeinstall -C dist/dist-tls

# XXX Nuke non-versioned archives and symlinks
rm -f ${RPM_BUILD_ROOT}%{_libdir}/{libdb.a,libdb_cxx.a}
rm -f ${RPM_BUILD_ROOT}%{_libdir}/libdb-4.so
rm -f ${RPM_BUILD_ROOT}%{_libdir}/libdb_cxx-4.so
rm -f ${RPM_BUILD_ROOT}%{_libdir}/libdb_tcl-4.so
rm -f ${RPM_BUILD_ROOT}%{_libdir}/libdb_tcl.so

chmod +x ${RPM_BUILD_ROOT}%{_libdir}/*.so*

# Move the header files to a subdirectory, in case we're deploying on a
# system with multiple versions of DB installed.
mkdir -p ${RPM_BUILD_ROOT}%{_includedir}/db4
mv ${RPM_BUILD_ROOT}%{_includedir}/*.h ${RPM_BUILD_ROOT}%{_includedir}/db4/

# Create symlinks to includes so that "use <db.h> and link with -ldb" works.
for i in db.h db_cxx.h; do
	ln -s db4/$i ${RPM_BUILD_ROOT}%{_includedir}
done

# Eliminate installed doco
rm -rf ${RPM_BUILD_ROOT}%{_prefix}/docs

# XXX Avoid Permission denied. strip when building as non-root.
chmod u+w ${RPM_BUILD_ROOT}%{_bindir} ${RPM_BUILD_ROOT}%{_bindir}/*

# remove unneeded .la files (#225675)
rm -f ${RPM_BUILD_ROOT}%{_libdir}/*.la

%clean
rm -rf ${RPM_BUILD_ROOT}

%post -p /sbin/ldconfig

%postun -p /sbin/ldconfig

%post -p /sbin/ldconfig tcl

%postun -p /sbin/ldconfig tcl

%post -p /sbin/ldconfig cxx

%postun -p /sbin/ldconfig cxx

%files
%defattr(-,root,root)
%doc LICENSE
%{_libdir}/libdb-%{__soversion}.so

%files cxx
%defattr(-,root,root)
%{_libdir}/libdb_cxx-%{__soversion}.so

%files utils
%defattr(-,root,root)
%{_bindir}/db*_archive
%{_bindir}/db*_checkpoint
%{_bindir}/db*_deadlock
%{_bindir}/db*_dump*
%{_bindir}/db*_hotbackup
%{_bindir}/db*_load
%{_bindir}/db*_printlog
%{_bindir}/db*_recover
%{_bindir}/db*_sql
%{_bindir}/db*_stat
%{_bindir}/db*_upgrade
%{_bindir}/db*_verify

%files devel
%defattr(-,root,root)
%doc README
#%doc	docs/*
#%doc	examples_c examples_cxx
%{_libdir}/libdb.so
%{_libdir}/libdb_cxx.so
%dir %{_includedir}/%{name}
%{_includedir}/%{name}/db.h
%{_includedir}/%{name}/db_cxx.h
%{_includedir}/db.h
%{_includedir}/db_cxx.h

%files devel-static
%defattr(-,root,root)
%{_libdir}/libdb-%{__soversion}.a
%{_libdir}/libdb_cxx-%{__soversion}.a
#%{_libdir}/libdb_tcl-%{__soversion}.a

