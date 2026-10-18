#!/usr/bin/env python3
"""Toggle a session-local GTK layer-shell drawer without a compositor config edit."""
import fcntl
import os
from pathlib import Path
import shutil
import socket
import subprocess
import sys
from midnight_common import runtime, query, windows, run, glyph

BASE = Path(__file__).resolve().parent.parent


def serve():
    import gi
    gi.require_version('Gtk', '3.0')
    gi.require_version('GtkLayerShell', '0.1')
    from gi.repository import Gtk, Gdk, GLib, Gio, GtkLayerShell
    lock = (runtime()/'panel.lock').open('w')
    try: fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except BlockingIOError: return
    address = runtime()/'panel.sock'
    address.unlink(missing_ok=True)
    channel = socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM)
    channel.bind(str(address)); channel.setblocking(False)
    os.chmod(address, 0o600)
    provider = Gtk.CssProvider()
    provider.load_from_path(str(BASE/'panel.css'))
    Gtk.StyleContext.add_provider_for_screen(Gdk.Screen.get_default(), provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)
    win = Gtk.Window(title='Midnight Control')
    win.set_name('midnight-panel'); win.set_decorated(False)
    win.set_app_paintable(True)
    visual = win.get_screen().get_rgba_visual()
    if visual: win.set_visual(visual)
    GtkLayerShell.init_for_window(win)
    GtkLayerShell.set_namespace(win, 'midnight-control')
    GtkLayerShell.set_layer(win, GtkLayerShell.Layer.OVERLAY)
    for edge in (GtkLayerShell.Edge.RIGHT, GtkLayerShell.Edge.TOP, GtkLayerShell.Edge.BOTTOM):
        GtkLayerShell.set_anchor(win, edge, True)
    GtkLayerShell.set_margin(win, GtkLayerShell.Edge.TOP, 76)
    GtkLayerShell.set_margin(win, GtkLayerShell.Edge.BOTTOM, 14)
    GtkLayerShell.set_margin(win, GtkLayerShell.Edge.RIGHT, 14)
    GtkLayerShell.set_exclusive_zone(win, 0)
    GtkLayerShell.set_keyboard_mode(win, GtkLayerShell.KeyboardMode.ON_DEMAND)
    win.set_size_request(1, 1)
    revealer = Gtk.Revealer()
    revealer.set_transition_type(Gtk.RevealerTransitionType.SLIDE_LEFT)
    revealer.set_transition_duration(260)
    win.add(revealer)
    body = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=14)
    body.set_name('panel-body');body.set_size_request(360, -1)
    revealer.add(body)
    opened = [False]
    def label(text, style=None):
        obj=Gtk.Label(label=text, xalign=0)
        if style: obj.get_style_context().add_class(style)
        return obj
    def action(args):
        try: subprocess.Popen(args, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, start_new_session=True)
        except OSError: pass
    def button(text, callback):
        b=Gtk.Button(label=text);b.connect('clicked',lambda *_:callback());return b
    def close():
        opened[0]=False;revealer.set_reveal_child(False)
        GLib.timeout_add(280, lambda: (win.hide() if not opened[0] else None) or False)
    header=Gtk.Box(spacing=12);body.pack_start(header,False,False,0)
    header.pack_start(label('MIDNIGHT / CONTROL','heading'),True,True,0)
    header.pack_end(button('×',close),False,False,0)
    status=label('','muted');body.pack_start(status,False,False,0)
    metrics=label('','metrics');body.pack_start(metrics,False,False,0)
    media=label('','muted');media.set_max_width_chars(34);media.set_line_wrap(True)
    body.pack_start(media,False,False,0)
    playback=Gtk.Box(spacing=8);body.pack_start(playback,False,False,0)
    for text, op in [('󰒮','previous'),('󰐎','play-pause'),('󰒭','next')]:
        b=button(text,lambda op=op:action(['playerctl',op]));b.set_sensitive(bool(shutil.which('playerctl')));playback.pack_start(b,True,True,0)
    body.pack_start(label('HLASITOST','section'),False,False,0)
    volume=Gtk.Scale.new_with_range(Gtk.Orientation.HORIZONTAL,0,100,1)
    volume.set_draw_value(True);volume.set_sensitive(bool(shutil.which('pactl')))
    syncing=[False];pending=[None]
    def set_volume():
        pending[0]=None;action(['pactl','set-sink-volume','@DEFAULT_SINK@',f'{int(volume.get_value())}%']);return False
    def volume_changed(*_):
        if syncing[0]: return
        if pending[0]: GLib.source_remove(pending[0])
        pending[0]=GLib.timeout_add(90,set_volume)
    volume.connect('value-changed',volume_changed);body.pack_start(volume,False,False,0)
    controls=Gtk.Box(spacing=8);body.pack_start(controls,False,False,0)
    for text,args in [('󰝟',['pactl','set-sink-mute','@DEFAULT_SINK@','toggle']),('󰤨',['nm-connection-editor']),('󰌾',['hyprlock']),('',['wlogout'])]:
        b=button(text,lambda args=args:action(args));b.set_sensitive(bool(shutil.which(args[0])));controls.pack_start(b,True,True,0)
    body.pack_start(label('OTEVŘENÁ OKNA','section'),False,False,0)
    scroll=Gtk.ScrolledWindow();scroll.set_policy(Gtk.PolicyType.NEVER,Gtk.PolicyType.AUTOMATIC)
    body.pack_start(scroll,True,True,0)
    listing=Gtk.Box(orientation=Gtk.Orientation.VERTICAL,spacing=6);scroll.add(listing)
    desktops={}
    for app in Gio.AppInfo.get_all():
        keys=[(app.get_id() or '').removesuffix('.desktop'), app.get_name()]
        if hasattr(app,'get_startup_wm_class'): keys.append(app.get_startup_wm_class())
        for key in keys:
            if key: desktops[key.lower()]=app
    snapshot=[None];cpu_previous=[None]
    def focus(address):
        action(['hyprctl','dispatch','focuswindow','address:'+address]);close()
    def refresh():
        if not opened[0]: return True
        from datetime import datetime
        try:
            uptime=int(float(Path('/proc/uptime').read_text().split()[0]))
            status.set_text(datetime.now().strftime('%A · %d.%m. · %H:%M') + f'\nUptime {uptime//3600} h {(uptime//60)%60} min')
            mem={line.split(':')[0]:int(line.split()[1]) for line in Path('/proc/meminfo').read_text().splitlines()}
            used=(mem['MemTotal']-mem['MemAvailable'])/1048576
            data=list(map(int,Path('/proc/stat').read_text().splitlines()[0].split()[1:9]));total=sum(data);idle=data[3]+data[4]
            old=cpu_previous[0];cpu_previous[0]=(total,idle)
            cpu=100*(1-(idle-old[1])/max(1,total-old[0])) if old else 0
            disk=shutil.disk_usage(Path.home());dp=100*disk.used/disk.total
            metrics.set_text(f'CPU  {cpu:3.0f}%     RAM  {used:.1f} GiB\nDISK {dp:3.0f}%     FREE {disk.free/1073741824:.0f} GiB')
        except (OSError,ValueError,KeyError): pass
        media.set_text(run(['playerctl','metadata','--format','{{artist}} — {{title}}']) or 'Žádné aktivní médium')
        import re
        v=re.search(r'(\d+)%',run(['pactl','get-sink-volume','@DEFAULT_SINK@']))
        if v and pending[0] is None:
            syncing[0]=True;volume.set_value(int(v[1]));syncing[0]=False
        clients, active=windows()
        current=[(c.get('address'),c.get('title'),c.get('class'),c.get('workspace',{}).get('id')) for c in clients],active
        if current!=snapshot[0]:
            snapshot[0]=current
            for child in listing.get_children(): child.destroy()
            for i,c in enumerate(clients):
                b=Gtk.Button();row=Gtk.Box(spacing=12);b.add(row)
                app=desktops.get(c.get('class','').lower()) or desktops.get(c.get('initialClass','').lower())
                if app and app.get_icon(): icon=Gtk.Image.new_from_gicon(app.get_icon(),Gtk.IconSize.LARGE_TOOLBAR)
                else: icon=label(glyph(c))
                row.pack_start(icon,False,False,0)
                text=label(c.get('title') or c.get('class') or 'Okno');text.set_max_width_chars(29)
                from gi.repository import Pango
                text.set_ellipsize(Pango.EllipsizeMode.END);row.pack_start(text,True,True,0)
                b.set_tooltip_text(c.get('title',''));b.set_opacity(max(.45,1-i*.06))
                if c.get('address')==active: b.get_style_context().add_class('active-window')
                b.connect('clicked',lambda _,a=c['address']:focus(a));listing.pack_start(b,False,False,0)
            if not clients: listing.pack_start(label('Žádná otevřená okna','muted'),False,False,0)
            listing.show_all()
        return True
    def toggle():
        if opened[0]: close();return
        opened[0]=True
        # Open on the currently focused Hyprland monitor, matching GDK by geometry.
        focused=next((m for m in query('monitors',[]) if m.get('focused')),None)
        display=Gdk.Display.get_default()
        if focused:
            for i in range(display.get_n_monitors()):
                monitor=display.get_monitor(i);geo=monitor.get_geometry()
                if geo.x==focused.get('x') and geo.y==focused.get('y'):
                    GtkLayerShell.set_monitor(win,monitor);break
        refresh();win.show_all()
        GLib.idle_add(lambda: revealer.set_reveal_child(True) or False)
    def receive(*_):
        try: message=channel.recv(32)
        except BlockingIOError: return True
        if message==b'quit': Gtk.main_quit();return False
        toggle();return True
    win.connect('key-press-event',lambda _,e:(close() or True) if e.keyval==Gdk.KEY_Escape else False)
    GLib.io_add_watch(channel.fileno(),GLib.IO_IN,receive)
    GLib.timeout_add_seconds(2,refresh)
    toggle()
    try: Gtk.main()
    finally: channel.close();address.unlink(missing_ok=True)


def main():
    if '--serve' in sys.argv:
        serve();return
    message=b'quit' if '--quit' in sys.argv else b'toggle'
    channel=socket.socket(socket.AF_UNIX,socket.SOCK_DGRAM)
    try:
        channel.sendto(message,str(runtime()/'panel.sock'));return
    except (FileNotFoundError,ConnectionRefusedError): pass
    finally: channel.close()
    if message==b'quit': return
    # Fail visibly when dependencies are missing; do not silently install packages.
    try:
        import gi
        gi.require_version('Gtk','3.0');gi.require_version('GtkLayerShell','0.1')
    except (ImportError,ValueError):
        text='Chybí python-gobject / gtk3 / gtk-layer-shell. Viz README.'
        print(text,file=sys.stderr)
        run(['notify-send','Midnight Control',text]);return
    with (runtime()/'panel.log').open('a') as log:
        subprocess.Popen([sys.executable,str(Path(__file__).resolve()),'--serve'],stdout=log,stderr=log,start_new_session=True)


if __name__=='__main__': main()
