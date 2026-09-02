#!/usr/bin/env bash
set -euo pipefail
mkdir -p backups
tar --exclude=backups --exclude=.git -czf "backups/historianos-$(date +%Y%m%d_%H%M%S).tar.gz" .
