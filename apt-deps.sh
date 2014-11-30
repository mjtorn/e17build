#!/usr/bin/env bash

set -e

for pkgs in $(cat apt-deps.txt); do
        sudo apt-get install -y $pkgs --force-yes
done

