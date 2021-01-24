#!/bin/sh

install=${1}
[ -e ${install}/include/uv.h ] && exit 0

version=v1.40.0

build=$(mktemp -d)
cd $build

wget https://dist.libuv.org/dist/${version}/libuv-${version}.tar.gz
tar -xzf libuv-${version}.tar.gz
cd libuv-${version}
sh autogen.sh
./configure --disable-shared
make -j4
make install prefix=${install}

cd $build/..
rm -rf $build
