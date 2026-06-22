#!/usr/bin/env bash

grep -rc "" -I *.py | cut -d':' -f2 | paste -sd+ | bc
