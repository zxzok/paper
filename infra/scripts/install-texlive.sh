#!/usr/bin/env bash
set -euo pipefail

PROFILE=${TEXLIVE_PROFILE:-/tmp/texlive.profile}

if [ ! -f "$PROFILE" ]; then
  cat <<'PROFILEEOF' > "$PROFILE"
selected_scheme scheme-medium
tlpdbopt_install_docfiles 0
tlpdbopt_install_srcfiles 0
option_autobackup 0
option_desktop_integration 0
option_file_assocs 0
option_fmt 1
option_letter 0
option_sys_bin /usr/local/bin
option_sys_man /usr/local/share/man
option_sys_info /usr/local/share/info
option_w32_multi_user 0
PROFILEEOF
fi

wget -qO- http://mirror.ctan.org/systems/texlive/tlnet/install-tl-unx.tar.gz | tar -xz -C /tmp
/tmp/install-tl-*/install-tl --profile="$PROFILE"
