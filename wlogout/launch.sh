#!/usr/bin/env bash
set -euo pipefail
root="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
exec wlogout -l "$root/layout" -C "$root/style.css" -b 3 "$@"
