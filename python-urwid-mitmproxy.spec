# Copyright 2023 Wong Hoi Sing Edison <hswong3i@pantarei-design.com>
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

%global debug_package %{nil}

Name: python-urwid-mitmproxy
Epoch: 100
Version: 2.1.2.1
Release: 1%{?dist}
Summary: Urwid fork used by mitmproxy
License: LGPL-2.1-or-later
URL: https://github.com/mitmproxy/urwid-mitmproxy/tags
Source0: %{name}_%{version}.orig.tar.gz
BuildRequires: fdupes
BuildRequires: python-rpm-macros
BuildRequires: python3-devel
BuildRequires: python3-setuptools

%description
This is an urwid fork with specific patches for mitmproxy.

%prep
%autosetup -T -c -n %{name}_%{version}-%{release}
tar -zx -f %{S:0} --strip-components=1 -C .

%build
%py3_build

%install
%py3_install
find %{buildroot}%{python3_sitearch} -type f -name '*.pyc' -exec rm -rf {} \;
fdupes -qnrps %{buildroot}%{python3_sitearch}

%check

%if 0%{?suse_version} > 1500
%package -n python%{python3_version_nodots}-urwid-mitmproxy
Summary: Urwid fork used by mitmproxy
Requires: python3
Provides: python3-urwid = %{epoch}:%{version}-%{release}
Provides: python3-urwid-mitmproxy = %{epoch}:%{version}-%{release}
Provides: python3dist(urwid-mitmproxy) = %{epoch}:%{version}-%{release}
Provides: python%{python3_version}-urwid-mitmproxy = %{epoch}:%{version}-%{release}
Provides: python%{python3_version}dist(urwid-mitmproxy) = %{epoch}:%{version}-%{release}
Provides: python%{python3_version_nodots}-urwid-mitmproxy = %{epoch}:%{version}-%{release}
Provides: python%{python3_version_nodots}dist(urwid-mitmproxy) = %{epoch}:%{version}-%{release}
Conflicts: python3-urwid < %{epoch}:%{version}-%{release}
Obsoletes: python3-urwid < %{epoch}:%{version}-%{release}

%description -n python%{python3_version_nodots}-urwid-mitmproxy
This is an urwid fork with specific patches for mitmproxy.

%files -n python%{python3_version_nodots}-urwid-mitmproxy
%license COPYING
%{python3_sitearch}/*
%endif

%if 0%{?sle_version} > 150000
%package -n python3-urwid-mitmproxy
Summary: Urwid fork used by mitmproxy
Requires: python3
Provides: python3-urwid = %{epoch}:%{version}-%{release}
Provides: python3-urwid-mitmproxy = %{epoch}:%{version}-%{release}
Provides: python3dist(urwid-mitmproxy) = %{epoch}:%{version}-%{release}
Provides: python%{python3_version}-urwid-mitmproxy = %{epoch}:%{version}-%{release}
Provides: python%{python3_version}dist(urwid-mitmproxy) = %{epoch}:%{version}-%{release}
Provides: python%{python3_version_nodots}-urwid-mitmproxy = %{epoch}:%{version}-%{release}
Provides: python%{python3_version_nodots}dist(urwid-mitmproxy) = %{epoch}:%{version}-%{release}
Conflicts: python3-urwid < %{epoch}:%{version}-%{release}
Obsoletes: python3-urwid < %{epoch}:%{version}-%{release}

%description -n python3-urwid-mitmproxy
This is an urwid fork with specific patches for mitmproxy.

%files -n python3-urwid-mitmproxy
%license COPYING
%{python3_sitearch}/*
%endif

%if !(0%{?suse_version} > 1500) && !(0%{?sle_version} > 150000)
%package -n python3-urwid-mitmproxy
Summary: Urwid fork used by mitmproxy
Requires: python3
Provides: python3-urwid = %{epoch}:%{version}-%{release}
Provides: python3-urwid-mitmproxy = %{epoch}:%{version}-%{release}
Provides: python3dist(urwid-mitmproxy) = %{epoch}:%{version}-%{release}
Provides: python%{python3_version}-urwid-mitmproxy = %{epoch}:%{version}-%{release}
Provides: python%{python3_version}dist(urwid-mitmproxy) = %{epoch}:%{version}-%{release}
Provides: python%{python3_version_nodots}-urwid-mitmproxy = %{epoch}:%{version}-%{release}
Provides: python%{python3_version_nodots}dist(urwid-mitmproxy) = %{epoch}:%{version}-%{release}
Conflicts: python3-urwid < %{epoch}:%{version}-%{release}
Obsoletes: python3-urwid < %{epoch}:%{version}-%{release}

%description -n python3-urwid-mitmproxy
This is an urwid fork with specific patches for mitmproxy.

%files -n python3-urwid-mitmproxy
%license COPYING
%{python3_sitearch}/*
%endif

%changelog
