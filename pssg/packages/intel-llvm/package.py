# Copyright 2013-2024 Lawrence Livermore National Security, LLC and other
# Spack Project Developers. See the top-level COPYRIGHT file for details.
#
# SPDX-License-Identifier: (Apache-2.0 OR MIT)

from spack.package import *

import os


class IntelLlvm(CMakePackage):
    """Intel's version of the LLVM compiler."""

    maintainers("rscohn2")

    homepage = "https://github.com/intel/llvm"
    git = "https://github.com/intel/llvm.git"
    url = "https://github.com/intel/llvm/archive/refs/tags/nightly-2024-01-20.tar.gz"

    license("Apache-2.0")

    generator("ninja")

    version("sycl", branch="sycl")
    version(
        "2024-01-20", sha256="dc5fff15b1cc9600345afac1c865a3a1d7889dc37f3de2b0eb764fe6bccffd37"
    )

    variant("cuda", default=False, description="Build with CUDA backend")
    variant("rocm", default=False, description="Build with ROCm backend")

    depends_on("cmake@3.20:", type="build")

    depends_on("cuda", when="+cuda")

    depends_on("hip", when="+rocm")
    depends_on("hsa-rocr-dev", when="+rocm")

    root_cmakelists_dir = "llvm"
    build_targets = ["deploy-sycl-toolchain"]

    def cmake_args(self):
        spec = self.spec
        define = self.define

        llvm_external_projects = "sycl;llvm-spirv;opencl;xpti;xptif"

        if spec.platform != "darwin":
            llvm_external_projects += ";libdevice"

        source_path = self.stage.source_path

        sycl_dir = os.path.join(source_path, "sycl")
        spirv_dir = os.path.join(source_path, "llvm-spirv")
        xpti_dir = os.path.join(source_path, "xpti")
        xptifw_dir = os.path.join(source_path, "xptifw")
        libdevice_dir = os.path.join(source_path, "libdevice")
        fusion_dir = os.path.join(source_path, "sycl-fusion")
        llvm_targets_to_build = get_llvm_targets_to_build(spec.target.family)
        llvm_enable_projects = "clang;lld;" + llvm_external_projects
        libclc_targets_to_build = ""
        libclc_gen_remangled_variants = "ON"
        sycl_build_pi_hip_platform = "AMD"
        sycl_clang_extra_flags = ""
        sycl_werror = "OFF"
        llvm_enable_doxygen = "OFF"
        llvm_enable_sphinx = "OFF"
        llvm_build_shared_libs = "OFF"
        llvm_enable_lld = "OFF"
        sycl_enabled_plugins = "opencl;level_zero"
        sycl_preview_lib = "ON"

        sycl_enable_xpti_tracing = "ON"
        xpti_enable_werror = "OFF"
        sycl_enable_fusion = "OFF"

        if spec.satisfies("+cuda") or spec.satisfies("+rocm"):
            llvm_enable_projects += ";libclc"

            libclc_amd_target_names = ";amdgcn--amdhsa"
            libclc_nvidia_target_names = ";nvptx64--nvidiacl"

            if spec.satisfies("+cuda"):
                libclc_targets_to_build += libclc_nvidia_target_names
                sycl_enabled_plugins += ";cuda"
                llvm_targets_to_build += ";NVPTX"

            if spec.satisfies("+rocm"):
                libclc_targets_to_build += libclc_amd_target_names
                sycl_enabled_plugins += ";hip"
                llvm_targets_to_build += ";AMDGPU"

        args = [
            define("LLVM_TARGETS_TO_BUILD", llvm_targets_to_build),
            define("LLVM_EXTERNAL_SYCL_SOURCE_DIR", sycl_dir),
            define("LLVM_EXTERNAL_LLVM_SPIRV_SOURCE_DIR", spirv_dir),
            define("LLVM_EXTERNAL_XPTI_SOURCE_DIR", xpti_dir),
            define("XPTI_SOURCE_DIR", xpti_dir),
            define("LLVM_EXTERNAL_XPTIFW_SOURCE_DIR", xptifw_dir),
            define("LLVM_EXTERNAL_LIBDEVICE_SOURCE_DIR", libdevice_dir),
            define("LLVM_EXTERNAL_SYCL_FUSION_SOURCE_DIR", fusion_dir),
            define("LLVM_ENABLE_PROJECTS", llvm_enable_projects),
            define("SYCL_BUILD_PI_HIP_PLATFORM={}", sycl_build_pi_hip_platform),
            define("LLVM_BUILD_TOOLS", "ON"),
            define("SYCL_ENABLE_WERROR", sycl_werror),
            define("SYCL_INCLUDE_TESTS", "ON"),
            define("LLVM_ENABLE_DOXYGEN", llvm_enable_doxygen),
            define("LLVM_ENABLE_SPHINX", llvm_enable_sphinx),
            define("BUILD_SHARED_LIBS", llvm_build_shared_libs),
            define("SYCL_ENABLE_XPTI_TRACING", sycl_enable_xpti_tracing),
            define("LLVM_ENABLE_LLD", llvm_enable_lld),
            define("DXPTI_ENABLE_WERROR", xpti_enable_werror),
            define("SYCL_CLANG_EXTRA_FLAGS", sycl_clang_extra_flags),
            define("SYCL_ENABLE_PLUGINS={}", ";".join(set(sycl_enabled_plugins))),
            define("SYCL_ENABLE_KERNEL_FUSION", sycl_enable_fusion),
            define("SYCL_ENABLE_MAJOR_RELEASE_PREVIEW_LIB", sycl_preview_lib),
            define("BUG_REPORT_URL", "https://github.com/intel/llvm/issues"),
            define("LIBCLC_TARGETS_TO_BUILD", libclc_targets_to_build),
            define("LIBCLC_GENERATE_REMANGLED_VARIANTS", libclc_gen_remangled_variants),
        ]

        if spec.satisfies("+cuda"):
            args.extend(
                [
                    define("CUDA_TOOLKIT_ROOT_DIR", spec["cuda"].prefix),
                ]
            )

        if spec.satisfies("+rocm"):
            args.extend(
                [
                    define("SYCL_BUILD_PI_HIP_INCLUDE_DIR", spec["hip"].prefix.include),
                    define(
                        "SYCL_BUILD_PI_HIP_HSA_INCLUDE_DIR", spec["hsa-rocr-dev"].prefix.include
                    ),
                    define("SYCL_BUILD_PI_HIP_LIB_DIR", spec["hip"].prefix.lib),
                    define("UR_HIP_INCLUDE_DIR", spec["hip"].prefix.include),
                    define("UR_HIP_HSA_INCLUDE_DIRS", spec["hsa-rocr-dev"].prefix.include),
                    define("UR_HIP_LIB_DIR", spec["hip"].prefix.lib),
                ]
            )

        if self.compiler.name == "gcc":
            args.append(define("GCC_INSTALL_PREFIX", self.compiler.prefix))

        return args

    def setup_build_environment(self, env):
        spec = self.spec

        env.set("CUDA_LIB_PATH", f"{spec['cuda'].prefix}/lib64/stubs")


def get_llvm_targets_to_build(family):
    host_target = ""
    if family in ("x86", "x86_64"):
        host_target = "X86"
    elif family == "arm":
        host_target = "ARM"
    elif family == "aarch64":
        host_target = "AArch64"
    elif family in ("sparc", "sparc64"):
        host_target = "Sparc"
    elif family in ("ppc64", "ppc64le", "ppc", "ppcle"):
        host_target = "PowerPC"
    return host_target
