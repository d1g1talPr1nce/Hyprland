#!/usr/bin/env bash
# Opens the real application launcher using this folder, without installing.
set -euo pipefail
root="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
exec bash "$root/launch.sh" "$@"
