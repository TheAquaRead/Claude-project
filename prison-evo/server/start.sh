#!/bin/sh
set -eu
cd "$(dirname "$0")"
printf '\nHYLOR | Prison Evo — local demo\n'
if ! grep -q '^eula=true' eula.txt; then
  printf 'Minecraft EULA: https://aka.ms/MinecraftEULA\nHave you read and accepted it? (y/N) '
  read -r answer
  case "$answer" in y|Y) printf 'eula=true\n' > eula.txt;; *) echo 'EULA was not accepted.'; exit 0;; esac
fi
JAVA_BIN=$(find .runtime -type f -path '*/bin/java' -print -quit 2>/dev/null || true)
if [ -z "$JAVA_BIN" ]; then
  [ "$(uname -s)" = Linux ] && [ "$(uname -m)" = x86_64 ] || { echo 'Install Java 25 and run: java -Xmx2G -jar paper.jar --nogui'; exit 1; }
  command -v curl >/dev/null || { echo 'curl is required'; exit 1; }
  echo 'Downloading Java 25 (first start only)...'
  mkdir -p .runtime
  curl -fL -o .runtime/java.tar.gz 'https://api.adoptium.net/v3/binary/latest/25/ga/linux/x64/jre/hotspot/normal/eclipse'
  tar -xzf .runtime/java.tar.gz -C .runtime
  rm .runtime/java.tar.gz
  JAVA_BIN=$(find .runtime -type f -path '*/bin/java' -print -quit)
fi
printf 'Connect in Minecraft Java 26.3 to localhost.\n'
exec "$JAVA_BIN" -Xms1G -Xmx2G -jar paper.jar --nogui
