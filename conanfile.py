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
from conan import ConanFile
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import get, rename

required_conan_version = ">=1.53.0"


class ResiprocateConan(ConanFile):
    build_policy = "missing"
    name = "resiprocate"
    description = "The project is dedicated to maintaining a complete, correct, and commercially usable implementation of SIP and a few related protocols. "
    topics = ("sip", "voip", "communication", "signaling")
    homepage = "https://www.resiprocate.org"
    license = "VSL-1.0"
    settings = "os", "compiler", "build_type", "arch"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_webrtc": [True, False],
        "with_resample": [True, False],
        "enable_android": [True, False],
        "enable_ipv6": [True, False],
        "enable_dtls": [True, False],
        "pedantic_stack": [True, False],
        "enable_dso_plugins": [True, False],
        "enable_test": [True, False],
    }

    default_options = {
        "shared": False,
        "fPIC": True,
        "with_webrtc": False,
        "with_resample": False,
        "enable_android": False,
        "enable_ipv6": True,
        "enable_dtls": True,
        "pedantic_stack": False,
        "enable_dso_plugins": True,
        "enable_test": False,
    }

    exports_sources = (
        "CMakeListsConan.cmake",
        "CMakeLists.txt",
        "config.h.cmake",
        "build/*",
        "media/*",
        "reflow/*",
        "resip/*",
        "reTurn/*",
        "rutil/*",
        "resiprocate.spec.in",
    )

    def layout(self):
        cmake_layout(self)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC
        if self.settings.os == "Android":
            self.options.enable_android = True
    def source(self):
        rename(self, "CMakeLists.txt", "CMakeLists.original")
        rename(self, "CMakeListsConan.cmake", "CMakeLists.txt")

    def generate(self):
        deps = CMakeDeps(self)
        deps.check_components_exist = True
        deps.generate()

        tc = CMakeToolchain(self)
        # POPT -----------------------------------------------------------
        tc.variables["USE_POPT"] = "ON" if self.options.shared else "OFF"
        # SHARED OR STATIC LIBRARIES -------------------------------------
        if self.options.shared:
            tc.variables["BUILD_SHARED_LIBS_DEFAULT"] = "ON" if self.options.shared else "OFF"
            tc.variables["BUILD_SHARED_LIBS"] = "ON" if self.options.shared else "OFF"
        # WITH_RESAMPLE --------------------------------------------------
        if self.options.with_resample:
            tc.variables["REGENERATE_MEDIA_SAMPLES"] = "ON" if self.options.with_resample else "OFF"
        # ENABLE_TEST ----------------------------------------------------
        tc.preprocessor_definitions["ENABLE_TEST"] = 1 if self.options.enable_test else 0
        # ENABLE_RECON ---------------------------------------------------
        tc.variables["BUILD_RECON"] = "ON"
        tc.preprocessor_definitions["BUILD_RECON"] = 1
        # ENABLE_RETURN --------------------------------------------------
        tc.variables["BUILD_RETURN"] = "ON"
        tc.preprocessor_definitions["BUILD_RETURN"] = 1
        # SSL ------------------------------------------------------------
        tc.variables["WITH_SSL"] = "ON"
        tc.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        cmake = CMake(self)
        cmake.install()

    def package_info(self):
        self.cpp_info.libs = ["resip", "rutil", "dum", "resipares", "resipmedia", "recon", "reflow", "reTurnClient", "reTurnCommon"]
        if self.settings.os in ("Linux", "FreeBSD"):
            self.cpp_info.system_libs = ["pthread"]

        self.cpp_info.set_property("cmake_file_name", "resiprocate")

        # Component reTurnCommon
        self.cpp_info.components["reTurnCommon"].set_property("cmake_target_name", "reTurnCommon")
        self.cpp_info.components["reTurnCommon"].libs = ["reTurnCommon"]

        # Component reTurnClient
        self.cpp_info.components["reTurnClient"].set_property("cmake_target_name", "reTurnClient")
        self.cpp_info.components["reTurnClient"].libs = ["reTurnClient"]

        # Component reflow
        self.cpp_info.components["reflow"].set_property("cmake_target_name", "reflow")
        self.cpp_info.components["reflow"].libs = ["reflow"]

        # Component recon
        self.cpp_info.components["recon"].set_property("cmake_target_name", "recon")
        self.cpp_info.components["recon"].libs = ["recon"]

        # Component rutil
        self.cpp_info.components["rutil"].set_property("cmake_target_name", "rutil")
        self.cpp_info.components["rutil"].libs = ["rutil"]

        # Component resipmedia
        self.cpp_info.components["resipmedia"].set_property("cmake_target_name", "resipmedia")
        self.cpp_info.components["resipmedia"].libs = ["resipmedia"]

        # Component resip
        self.cpp_info.components["resip"].set_property("cmake_target_name", "resip")
        self.cpp_info.components["resip"].libs = ["resip"]

        # Component dum
        self.cpp_info.components["dum"].set_property("cmake_target_name", "dum")
        self.cpp_info.components["dum"].libs = ["dum"]

        # Component resipares
        self.cpp_info.components["resipares"].set_property("cmake_target_name", "resipares")
        self.cpp_info.components["resipares"].libs = ["resipares"]

    def requirements(self):
        self.requires("openssl/1.1.1t")
        self.requires("c-ares/1.19.1", transitive_headers=True)
        self.requires("libsrtp/2.4.2")
        self.requires("soxr/0.1.3")
        self.requires("asio/1.28.1")
        self.requires("boost/1.80.0")
        self.requires("popt/1.9.1@nerd4ever")
