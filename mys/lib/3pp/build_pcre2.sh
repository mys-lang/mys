#!/bin/sh

install=${1}
[ -e ${install}/include/pcre2.h ] && exit 0

version=10.36

build=$(mktemp -d)
cd $build

wget https://ftp.pcre.org/pub/pcre/pcre2-${version}.tar.gz
tar -xzf pcre2-${version}.tar.gz
cd pcre2-${version}
./configure --disable-pcre2-8 --enable-pcre2-32 --disable-shared
make -j4
make install prefix=${install}

cd $build/..
rm -rf $build
