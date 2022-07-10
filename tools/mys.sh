#!/bin/sh

BASEDIR=$(dirname "$0")
PYTHONUTF8=1 ${BASEDIR}/mystic/mystic "$@"
