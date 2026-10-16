#!/bin/bash

WALLPAPER_DIR="/home/jerry/Obrazky/Wallpapers"
INDEX_FILE="/tmp/hyprpaper_index"

# Načte pouze obrázky (ignoruje případná videa ve složce)
shopt -s nullglob
FILES=("$WALLPAPER_DIR"/*.{jpg,jpeg,png,webp})
NUM_FILES=${#FILES[@]}

if [ $NUM_FILES -eq 0 ]; then
    notify-send "Chyba" "Žádné obrázky ve složce $WALLPAPER_DIR"
    exit 1
fi

# Zjištění aktuální pozice
if [ -f "$INDEX_FILE" ]; then
    CURRENT_INDEX=$(cat "$INDEX_FILE")
else
    CURRENT_INDEX=0
fi

# Posun na další index
NEXT_INDEX=$(( (CURRENT_INDEX + 1) % NUM_FILES ))
echo "$NEXT_INDEX" > "$INDEX_FILE"

NEXT_WALLPAPER="${FILES[$NEXT_INDEX]}"
NAME=$(basename "$NEXT_WALLPAPER")

# --- HYPRPAPER LOGIKA ---

# 1. Nejdřív se musí tapeta nahrát do paměti (preload)
hyprctl hyprpaper preload "$NEXT_WALLPAPER"

# 2. Aplikování tapety na všechny připojené monitory
for monitor in $(hyprctl monitors | grep "Monitor" | awk '{print $2}'); do
    hyprctl hyprpaper wallpaper "$monitor,$NEXT_WALLPAPER"
done

# 3. Uvolnění starých tapet z paměti (aby hyprpaper nežral zbytečně RAM)
hyprctl hyprpaper unload unused

# Volitelné upozornění
notify-send "Tapeta změněna" "$NAME"
