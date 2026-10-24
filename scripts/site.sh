#!/usr/bin/env bash
set -euo pipefail
portfolio_root="$(cd "$(dirname "$0")/.." && pwd)"
cd "$portfolio_root"
if [ -f "$portfolio_root/.tools/gems/bin/bundle" ]; then
  export GEM_HOME="$portfolio_root/.tools/gems"
  export GEM_PATH="$portfolio_root/.tools/gems"
  export BUNDLE_USER_HOME="$portfolio_root/.tools/bundle-user"
  export BUNDLE_APP_CONFIG="$portfolio_root/.bundle"
  export TMPDIR="$portfolio_root/.tools/tmp"
  exec ruby "$portfolio_root/.tools/gems/bin/bundle" exec jekyll "$@"
fi
exec bundle exec jekyll "$@"
