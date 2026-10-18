#!/usr/bin/env python3
"""One CAVA process per bar, no sed process per frame; private temp config."""
import os
import shutil
import signal
import subprocess
import tempfile


def main():
    if not shutil.which('cava'):
        print('▁' * 22, flush=True)
        return
    signal.signal(signal.SIGTERM, lambda *_: (_ for _ in ()).throw(SystemExit(0)))
    with tempfile.TemporaryDirectory(prefix='midnight-cava-') as folder:
        config = os.path.join(folder, 'config')
        with open(config, 'w') as f:
            f.write('[general]\nbars = 22\nframerate = 24\n[output]\nmethod = raw\nraw_target = /dev/stdout\ndata_format = ascii\nascii_max_range = 7\n')
        proc = subprocess.Popen(['cava', '-p', config], stdout=subprocess.PIPE, text=True)
        try:
            for line in proc.stdout:
                values = line.strip().strip(';').split(';')
                try:
                    text = ''.join('▁▂▃▄▅▆▇█'[max(0, min(7, int(v)))] for v in values)
                except ValueError:
                    continue
                print(text, flush=True)
        except (BrokenPipeError, KeyboardInterrupt):
            pass
        finally:
            proc.terminate()
            try:
                proc.wait(timeout=2)
            except subprocess.TimeoutExpired:
                proc.kill()
                proc.wait()


if __name__ == '__main__':
    main()
