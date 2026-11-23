#!/bin/sh
# User-facing macOS launcher. No package installs or remote calls.
set -eu
cd "$(dirname "$0")/projects/reliability-lab"
exec python3 -m reliability_lab serve
