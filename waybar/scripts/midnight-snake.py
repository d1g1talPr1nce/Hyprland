#!/usr/bin/env python3
import fcntl
import html
import json
import sys
from midnight_common import runtime, windows, glyph, run


def render(clients, active, expanded):
    if not clients:
        return {'text': '', 'tooltip': 'Žádná otevřená okna', 'class': 'empty'}
    shown = clients if expanded else clients[:1]
    parts = []
    count = len(shown)
    for i, c in enumerate(shown):
        # Bright head; remaining icons smoothly descend to a readable slate blue.
        t = i / max(1, count - 1)
        rgb = tuple(round(a + (b-a)*t) for a,b in zip((188,238,255),(69,92,122)))
        color = '#%02x%02x%02x' % rgb
        parts.append(f'<span foreground="{color}">{glyph(c)}</span>')
    marker = '‹' if expanded else ('›' if len(clients)>1 else '')
    text = '   '.join(parts) + ('  ' + marker if marker else '')
    tip = ['Klik: sbalit / rozbalit', 'Pravý klik: panel s výběrem oken', 'Kolečko: předchozí / další okno', '']
    tip += [f"{'●' if c.get('address') == active else '○'} {c.get('class','')} · {c.get('title','')}" for c in clients]
    return {'text':text, 'tooltip':html.escape('\n'.join(tip)), 'class':'expanded' if expanded else 'collapsed'}


def main():
    state = runtime() / 'snake-expanded'
    action = sys.argv[1] if len(sys.argv)>1 else 'show'
    if action == 'toggle':
        with (runtime()/'snake.lock').open('w') as lock:
            fcntl.flock(lock, fcntl.LOCK_EX)
            if state.exists(): state.unlink()
            else: state.touch(mode=0o600)
        return
    clients, active = windows()
    if action in ('next','prev'):
        stable = sorted(clients, key=lambda c:c.get('address',''))
        if stable:
            current = next((i for i,c in enumerate(stable) if c.get('address')==active), 0)
            c = stable[(current+(1 if action=='next' else -1))%len(stable)]
            run(['hyprctl','dispatch','focuswindow','address:'+c['address']])
        return
    print(json.dumps(render(clients, active, state.exists()), ensure_ascii=False))


if __name__=='__main__': main()
