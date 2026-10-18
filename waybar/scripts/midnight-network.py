#!/usr/bin/env python3
"""Small NetworkManager drawer; connection changes only on an explicit click."""
import os
from pathlib import Path
import socket
import subprocess
import sys
import threading
import fcntl
from midnight_common import runtime


def nm(args):
    try:
        r=subprocess.run(['nmcli', '--wait', '10']+args,capture_output=True,text=True,timeout=12,env={**os.environ,'LC_ALL':'C'})
        return r.returncode, r.stdout.strip() if r.returncode==0 else r.stderr.strip()
    except (OSError,subprocess.TimeoutExpired) as exc: return 1,str(exc)


def profiles(text):
    result=[]
    for row in text.splitlines():
        # UUID contains no colon; preserve colons in a profile name.
        uuid, sep, name=row.partition(':')
        if sep and uuid: result.append((uuid,name))
    return result


def serve():
    import gi
    gi.require_version('Gtk','3.0');gi.require_version('GtkLayerShell','0.1')
    from gi.repository import Gtk,Gdk,GLib,GtkLayerShell
    lock=(runtime()/'network.lock').open('w')
    try: fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
    except BlockingIOError:return
    path=runtime()/'network.sock';path.unlink(missing_ok=True)
    sock=socket.socket(socket.AF_UNIX,socket.SOCK_DGRAM);sock.bind(str(path));sock.setblocking(False)
    win=Gtk.Window(title='Midnight Network');win.set_name('midnight-panel');win.set_decorated(False)
    win.set_app_paintable(True)
    visual=win.get_screen().get_rgba_visual()
    if visual:win.set_visual(visual)
    GtkLayerShell.init_for_window(win);GtkLayerShell.set_namespace(win,'midnight-network')
    GtkLayerShell.set_layer(win,GtkLayerShell.Layer.OVERLAY)
    for edge in [GtkLayerShell.Edge.TOP,GtkLayerShell.Edge.RIGHT]:GtkLayerShell.set_anchor(win,edge,True)
    GtkLayerShell.set_margin(win,GtkLayerShell.Edge.TOP,78);GtkLayerShell.set_margin(win,GtkLayerShell.Edge.RIGHT,18)
    GtkLayerShell.set_keyboard_mode(win,GtkLayerShell.KeyboardMode.ON_DEMAND)
    css=Gtk.CssProvider();css.load_from_path(str(Path(__file__).resolve().parent.parent/'panel.css'))
    Gtk.StyleContext.add_provider_for_screen(Gdk.Screen.get_default(),css,Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)
    body=Gtk.Box(orientation=Gtk.Orientation.VERTICAL,spacing=12);body.set_name('panel-body');body.set_size_request(390,-1);win.add(body)
    head=Gtk.Box(spacing=12);body.pack_start(head,False,False,0)
    title=Gtk.Label(label='󰈀  NETWORK MANAGER',xalign=0);title.get_style_context().add_class('heading');head.pack_start(title,True,True,0)
    close=Gtk.Button(label='×');close.connect('clicked',lambda *_:Gtk.main_quit());head.pack_end(close,False,False,0)
    status=Gtk.Label(label='Načítám síť…',xalign=0);status.set_line_wrap(True);status.set_max_width_chars(42);body.pack_start(status,False,False,0)
    scroll=Gtk.ScrolledWindow();scroll.set_policy(Gtk.PolicyType.NEVER,Gtk.PolicyType.AUTOMATIC);scroll.set_min_content_height(180);scroll.set_max_content_height(340);scroll.set_propagate_natural_height(True);body.pack_start(scroll,True,True,0)
    listing=Gtk.Box(orientation=Gtk.Orientation.VERTICAL,spacing=7);scroll.add(listing)
    footer=Gtk.Box(spacing=8);body.pack_start(footer,False,False,0)
    def spawn(args):
        try:subprocess.Popen(args,start_new_session=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
        except OSError as exc:status.set_text(str(exc))
    editor=Gtk.Button(label='Upravit připojení');editor.connect('clicked',lambda *_:spawn(['nm-connection-editor']));footer.pack_start(editor,True,True,0)
    wifi=Gtk.Button(label='Wi-Fi / nová síť');wifi.connect('clicked',lambda *_:spawn(['kitty','-e','nmtui','connect']));footer.pack_start(wifi,True,True,0)
    busy=[False]
    def apply_data(state, saved, active):
        if busy[0]:return False
        status.set_text(state or 'NetworkManager není dostupný.')
        for child in listing.get_children():child.destroy()
        for uuid,name in saved:
            b=Gtk.Button(label=('●  ' if uuid in active else '○  ')+name)
            if uuid in active:b.get_style_context().add_class('active-window')
            b.connect('clicked',lambda _,u=uuid:activate(u));listing.pack_start(b,False,False,0)
        if not saved:listing.pack_start(Gtk.Label(label='Žádné uložené profily.'),False,False,0)
        listing.show_all();return False
    def load_worker():
        _,state=nm(['-t','-f','DEVICE,STATE,CONNECTION','device','status'])
        _,saved=nm(['-t','--escape','no','-f','UUID,NAME','connection','show'])
        _,active=nm(['-t','-f','UUID','connection','show','--active'])
        GLib.idle_add(apply_data,state,profiles(saved),set(active.splitlines()))
    def refresh():threading.Thread(target=load_worker,daemon=True).start()
    def finish(code,message):
        busy[0]=False;listing.set_sensitive(True)
        if code:status.set_text('Připojení selhalo: '+message[:250])
        else:refresh()
        return False
    def activate(uuid):
        if busy[0]:return
        busy[0]=True;listing.set_sensitive(False);status.set_text('Připojuji uložený profil…')
        def worker():
            code,message=nm(['connection','up','uuid',uuid]);GLib.idle_add(finish,code,message)
        threading.Thread(target=worker,daemon=True).start()
    refresh_button=Gtk.Button(label='Obnovit');refresh_button.connect('clicked',lambda *_:refresh());body.pack_start(refresh_button,False,False,0)
    def receive(*_):
        try:sock.recv(32)
        except BlockingIOError:return True
        Gtk.main_quit();return False
    GLib.io_add_watch(sock.fileno(),GLib.IO_IN,receive)
    win.connect('key-press-event',lambda _,e:(Gtk.main_quit() or True) if e.keyval==Gdk.KEY_Escape else False)
    win.connect('destroy',lambda *_:Gtk.main_quit())
    win.show_all();refresh()
    try:Gtk.main()
    finally:sock.close();path.unlink(missing_ok=True)


def main():
    if '--serve' in sys.argv:serve();return
    sock=socket.socket(socket.AF_UNIX,socket.SOCK_DGRAM)
    try:sock.sendto(b'close',str(runtime()/'network.sock'));return
    except (FileNotFoundError,ConnectionRefusedError):pass
    finally:sock.close()
    if '--quit' in sys.argv:return
    with (runtime()/'network.log').open('a') as log:
        subprocess.Popen([sys.executable,str(Path(__file__).resolve()),'--serve'],start_new_session=True,stdout=log,stderr=log)


if __name__=='__main__':main()
