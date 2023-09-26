# ------------------------------------------------------------------------------
# conanfile.py for resiprocate project
# Created by Sileno de Oliveira Brito on 22/09/2023.
# -----------------------------------------------------------------------------
# In this `conanfile.py`, we're adopting certain naming conventions for options:
#
# - The prefix `with_` is used to denote items that rely on external libraries.
# - The prefix `enable_` is employed to activate functionalities that don't
#   modify external libraries and to include additional binaries from other projects.
# - Elements are kept without a prefix, following a standard convention that's
#   well-known across many packages.
#
# As this is the initial version of these conventions, they might undergo
# changes throughout the project's development.
#
# The reasoning behind the `with_` prefix is to bring heightened awareness
# when utilizing external libraries. It aids in identifying both external
# dependencies and potential licensing changes. The adoption of certain licenses,
# such as GPL, can influence the overall project license. We aim to ensure clarity
# when evaluating library combinations. For instance, with Conan, it's simple to
# swap a static library for a shared one. In the scenario of an LGPLv3 library,
# this could inadvertently affect the licensing aspect of the project.
# -----------------------------------------------------------------------------
# Note: This Conan recipe is licensed under the MIT License.
# The resiprocate project and its associated components may be licensed differently.
# Please see the project's root license for those details.
#
# MIT License:
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
# ------------------------------------------------------------------------------
import os
import glob
import shutil
from conan import ConanFile
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import get, chdir

required_conan_version = ">=2.0.0"

class ResiprocateConan(ConanFile):
    build_policy = "missing"
    name = "resiprocate"
    version = "1.12.0-conan"
    settings = "os", "compiler", "build_type", "arch"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_c_ares": [True, False],
        "with_ssl": [True, False],
        "with_popt": [True, False],
        "with_soci_postgresql": [True, False],
        "with_soci_mysql": [True, False],
        "with_netsnmp": [True, False],
        "with_srtp": [True, False],
        "with_webrtc": [True, False],
        "with_syslog": [True, False],
        "with_resample": [True, False],
        "with_fmt": [True, False],
        "enable_android": [True, False],
        "enable_ipv6": [True, False],
        "enable_dtls": [True, False],
        "pedantic_stack": [True, False],
        "enable_repro": [True, False],  # <- Build repro SIP prox
        "enable_dso_plugins": [True, False],
        "enable_return": [True, False],
        "enable_telepathy_cm": [True, False],
        "enable_qpid_proton": [True, False],
        "enable_recon": [True, False],
        "enable_test": [True, False],
    }

    default_options = {
        "shared": False,
        "fPIC": True,
        "with_popt": False,
        "with_ssl": True,
        "with_soci_postgresql": False,
        "with_soci_mysql": False,
        "with_c_ares": False,
        "with_fmt": False,
        "with_netsnmp": False,
        "with_srtp": True,
        "with_webrtc": False,
        "with_syslog": False,
        "with_resample": False,
        "enable_android": False,
        "enable_ipv6": True,
        "enable_dtls": True,
        "pedantic_stack": False,
        "enable_repro": False,
        "enable_recon": False,
        "enable_dso_plugins": True,
        "enable_return": False,
        "enable_telepathy_cm": False,
        "enable_qpid_proton": False,
        "enable_test": False,
    }
    generators = "CMakeDeps"
    exports_sources = (
        "CMakeLists.txt",
        "config.h.cmake",
        "apps/*",
        "build/*",
        "contrib/*",
        "debian/*",
        "emacs/*",
        "media/*",
        "p2p/*",
        "reflow/*",
        "repro/*",
        "resip/*",
        "reTurn/*",
        "rutil/*",
        "snmp/*",
        "tfm/*",
        "tools/*",
        "resiprocate.spec.in",
    )

    def source(self):
        # self.run("git clone https://github.com/resiprocate/resiprocate.git")
        self.run("git clone -b conan-recipe-feature https://github.com/nerd4ever/resiprocate.git")

    # url = self.conan_data["sources"][self.version]["url"]
    # get(self, url, strip_root=True)

    def layout(self):
        cmake_layout(self)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC
        if self.settings.os == "Android":
            self.options.enable_android = True

    def generate(self):
        tc = CMakeToolchain(self)
        # SHARED OR STATIC LIBRARIES -------------------------------------
        if self.options.shared:
            tc.variables["BUILD_SHARED_LIBS_DEFAULT"] = "ON" if self.options.enable_repro else "OFF"
            tc.variables["BUILD_SHARED_LIBS"] = "ON" if self.options.enable_repro else "OFF"
        # ENABLE_TEST ----------------------------------------------------
        tc.preprocessor_definitions["ENABLE_TEST"] = 1 if self.options.enable_test else 0

        # BUILD_REPRO ----------------------------------------------------
        tc.variables["BUILD_REPRO"] = "ON" if self.options.enable_repro else "OFF"
        tc.variables["BUILD_DSO_PLUGINS"] = "ON" if self.options.enable_dso_plugins else "OFF"
        tc.variables["BUILD_RETURN"] = "ON" if self.options.enable_return else "OFF"
        tc.preprocessor_definitions["BUILD_REPRO"] = 1 if self.options.enable_repro else 0
        # BUILD_TELEPATHY_CM ---------------------------------------------
        tc.preprocessor_definitions["BUILD_TELEPATHY_CM"] = 1 if self.options.enable_telepathy_cm else 0
        tc.variables["BUILD_TELEPATHY_CM"] = "ON" if self.options.enable_telepathy_cm else "OFF"
        # BUILD_RETURN ---------------------------------------------------
        tc.preprocessor_definitions["BUILD_RETURN"] = 1 if self.options.enable_return else 0
        tc.variables["BUILD_RETURN"] = "ON" if self.options.enable_return else "OFF"
        # BUILD_RECON ----------------------------------------------------
        tc.preprocessor_definitions["BUILD_RECON"] = 1 if self.options.enable_recon else 0
        tc.variables["BUILD_RECON"] = "ON" if self.options.enable_recon else "OFF"
        if self.options.enable_recon:
            tc.preprocessor_definitions["USE_SRTP"] = 1
        tc.preprocessor_definitions["BUILD_QPID_PROTON"] = 1 if self.options.enable_qpid_proton else 0
        tc.variables["BUILD_QPID_PROTON"] = "ON" if self.options.enable_qpid_proton else "OFF"
        if self.options.enable_qpid_proton:
            tc.preprocessor_definitions["BUILD_QPID_PROTON"] = 1
        # WITH_RESAMPLE --------------------------------------------------
        if self.options.with_resample:
            tc.variables["REGENERATE_MEDIA_SAMPLES"] = "ON" if self.options.with_resample else "OFF"
        tc.generate()

    def build(self):
        current_dir = os.getcwd()
        print("current dir: " + current_dir)  # Isto deve listar o diretório 'resiprocate'
        print(os.listdir(self.source_folder))  # Isto deve listar o diretório 'resiprocate'
        print(os.listdir(os.path.join(self.source_folder, "resiprocate")))  # Isto deve listar o CMakeLists.txt

        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        cmake = CMake(self)
        cmake.install()

    def package_info(self):
        self.cpp_info.libs = ["resiprocate"]

    def requirements(self):
        if self.options.enable_repro:
            self.requires("libdb/5.3.28")
            self.requires("pcre/8.45")
            self.requires("cajun-jsonapi/2.1.1")
        if self.options.enable_return:
            self.requires("asio/1.28.1")
        if self.options.with_netsnmp:
            self.requires("net-snmp/5.9.1")
        if self.options.with_ssl:
            self.requires("openssl/1.1.1t")
        if self.options.with_popt:
            self.requires("popt/1.16")
        if self.options.with_soci_postgresql or self.options.with_soci_mysql:
            self.requires("soci/4.0.3")
            if self.options.with_soci_postgresql:
                self.requires("libpq/15.4")
            if self.options.with_soci_mysql:
                self.requires("libmysqlclient/8.1.0")
        if self.options.with_popt:
            self.requires("c-ares/1.19.1")
        if self.options.with_fmt:
            self.requires("fmt/10.1.1")
        if self.options.with_srtp:
            self.requires("libsrtp/2.4.2")
        if self.options.with_resample:
            self.requires("soxr/0.1.3")
        if self.options.enable_recon:
            self.requires("libsrtp/2.4.2")
        if self.options.enable_telepathy_cm:
            self.requires("qt/5.15.10")
        if self.options.enable_qpid_proton:
            # No publication has been made so far from the library, a fictitious name is being used
            self.requires("libqpid-proton/0.39.0")
