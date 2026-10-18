#!/usr/bin/env python3
"""Prefer CPU package sensors; no unstable hwmon index."""
import json
from pathlib import Path


def read_temperature(root=Path('/sys/class/hwmon')):
    candidates = []
    for device in root.glob('hwmon*'):
        try:
            name = (device / 'name').read_text().strip()
        except OSError:
            continue
        if name not in ('k10temp', 'coretemp', 'zenpower', 'cpu_thermal'):
            continue
        for sensor in device.glob('temp*_input'):
            try:
                value = int(sensor.read_text()) / 1000
                label_file = sensor.with_name(sensor.name.replace('_input', '_label'))
                label = label_file.read_text().strip() if label_file.exists() else sensor.stem
            except (OSError, ValueError):
                continue
            if -20 <= value <= 130:
                rank = 0 if label in ('Tctl', 'Package id 0') else 1
                candidates.append((rank, -value, name, label))
    if not candidates:
        return {'text': '', 'tooltip': 'CPU temperature sensor unavailable'}
    _, negative, name, label = min(candidates)
    value = -negative
    return {'text': f' {value:.0f}°', 'tooltip': f'{name} · {label}: {value:.1f} °C', 'class': 'critical' if value >= 85 else 'normal'}


if __name__ == '__main__':
    print(json.dumps(read_temperature(), ensure_ascii=False))
