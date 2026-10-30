#!/bin/sh
cd "$(dirname "$0")" || exit 1
java -Xms1G -Xmx2G -jar paper.jar --nogui
