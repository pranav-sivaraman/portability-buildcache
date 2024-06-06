#!/bin/bash

# Setup Spack
export SPACK_PYTHON=/opt/python/cp312-cp312/bin/python
git clone -c feature.manyFiles=true https://github.com/spack/spack.git
export SPACK_ROOT=spack
. spack/share/spack/setup-env.sh

# Trust buildcache
spack mirror add develop-2024-06-02 https://binaries.spack.io/develop-2024-06-02
spack buildcache keys --install --trust

# Find compilers
spack compiler find --mixed-toolchain

# Install newer gmake
spack install gmake && spack load gmake

# Concretize
spack -e . -v concretize

# Install
spack -e . env depfile -o Makefile
make -Orecurse -j $(($(nproc) + 1)) SPACK_INSTALL_FLAGS=--no-check-signature

# Push packages and update index
spack -e . mirror set --push --oci-username "${OCI_USERNAME}" --oci-password "${OCI_PASSWORD}" local-buildcache
spack -e . buildcache push -j $(($(nproc) + 1)) --base-image ${CONTAINER} --update-index --force local-buildcache
