#!/usr/bin/env bash
#
# Reformat all python files
# Requires yapf, which can be installed through pip
yapf --style google -i -r .
