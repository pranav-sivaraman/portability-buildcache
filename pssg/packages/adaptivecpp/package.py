# Copyright 2013-2023 Lawrence Livermore National Security, LLC and other
# Spack Project Developers. See the top-level COPYRIGHT file for details.
#
# SPDX-License-Identifier: (Apache-2.0 OR MIT)
from spack.package import *


class Adaptivecpp(CMakePackage):
    """AdaptiveCpp is the independent, community-driven modern platform for
    C++-based heterogeneous programming models targeting CPUs and GPUs
    from all major vendors."""

    homepage = "https://adaptivecpp.github.io/"
    url = "https://github.com/AdaptiveCpp/AdaptiveCpp/archive/refs/tags/v23.10.0.tar.gz"
    git = "https://github.com/AdaptiveCpp/AdaptiveCpp.git"

    license("BSD-2-Clause")

    version("develop", branch="develop")
    version("24.02.0", sha256="180bdcbf40db9907ba5b3da06a57e779e1527c62528211f72e9d36a5e46b0956")
    version("23.10.0", sha256="9ac3567c048a848f4e6eadb15b09750357ae399896e802b2f1dcaecf8a090064")
    version("0.9.4", sha256="d9269c814f5e07b54a58bcef177950f222e22127c8399edc2e627d6b9e250763")
    version("0.9.3", sha256="6a2e2d81bd21209ad0726d5aa377321e177fecb775ad93078259835be0931f51")
    version("0.9.2", sha256="4b2308eb19b978a8528d55fe8c9fbb18d5be51aa0dd1a18a068946d8ddedebb1")
    version("0.9.1", sha256="f4adbe283d21272d5b5a1431650971c29360453c167b8c3f6ed32611322aa4b1")
    version("0.9.0", sha256="a7c565055fcb88dbca73693d3497fc8118e4f65b435e9bf136098a06b19dd8fc")
    version("0.8.0", sha256="18e1a14d2f5f86a9bb4b799818c086d017a7e397a5f58bb92463a90355951f44")

    variant("cuda", default=False, description="Build with CUDA backend")
    variant("rocm", default=False, description="Build with ROCm backend")

    depends_on("boost +filesystem +fiber +context cxxstd=17")

    depends_on("libllvm")
    depends_on("llvm +clang", when="^llvm")

    depends_on("cuda", when="+cuda")
    depends_on("hip", when="+rocm")

    def cmake_args(self):
        spec = self.spec
        define = self.define
        from_variant = self.define_from_variant

        args = [
            define("LLVM_DIR", spec["libllvm"].prefix + "/lib/cmake/llvm"),
            define("ACPP_VERSION_SUFFIX", "-"),
        ]

        if spec.satisfies("+cuda"):
            args.extend(
                [
                    from_variant("WITH_CUDA_BACKEND", "cuda"),
                    define("CUDA_TOOLKIT_ROOT_DIR", spec["cuda"].prefix),
                ]
            )

        if spec.satisfies("+rocm"):
            args.extend(
                [
                    from_variant("WITH_ROCM_BACKEND", "rocm"),
                    define("ROCM_PATH", spec["hip"].prefix),
                ]
            )

        return args
