"""Shared, bounded subprocess calls. Window titles are never executed."""
import hashlib
import json
import os
from pathlib import Path
import subprocess


def run(args):
    try:
        return subprocess.run(args, capture_output=True, text=True, timeout=1).stdout.strip()
    except (OSError, subprocess.TimeoutExpired):
        return ''


def query(name, default):
    try:
        return json.loads(run(['hyprctl', '-j', name]))
    except (ValueError, TypeError):
        return default


def windows():
    active = query('activewindow', {}).get('address', '')
    clients = [c for c in query('clients', []) if c.get('mapped', True) and not c.get('hidden', False)]
    def key(c):
        age = c.get('focusHistoryID', -1)
        return (c.get('address') != active, age if age >= 0 else 100000, c.get('address', ''))
    return sorted(clients, key=key), active


def runtime():
    base = Path(os.environ.get('XDG_RUNTIME_DIR', str(Path.home() / '.cache')))
    session = hashlib.sha256(os.environ.get('HYPRLAND_INSTANCE_SIGNATURE', 'default').encode()).hexdigest()[:10]
    path = base / ('midnight-ice-' + session)
    path.mkdir(mode=0o700, parents=True, exist_ok=True)
    return path


def glyph(client):
    name = (client.get('class', '') + ' ' + client.get('initialClass', '')).lower()
    for names, icon in [
        (('firefox','zen','librewolf'), ''), (('chrom','brave','vivaldi'), ''),
        (('kitty','alacritty','foot','terminal','wezterm'), ''),
        (('code','codium'), '󰨞'), (('idea','studio','jetbrains'), ''),
        (('discord','vesktop'), ''), (('spotify',), ''),
        (('steam',), ''), (('obsidian',), '󱓧'),
        (('dolphin','thunar','nautilus','nemo'), ''), (('vlc','mpv'), ''),
        (('gimp','krita'), ''), (('telegram',), ''), (('obs',), ''),
        (('pdf','okular','evince'), ''), (('libreoffice',), '')]:
        if any(n in name for n in names):
            return icon
    return ''
