#!/bin/bash

# --- KONFIGURACE ---
# Cesta ke složce s tapetami (uprav podle sebe)
WALLPAPER_DIR="/home/jerry/Obrazky/Wallpapers/"

# Soubor pro uložení aktuálního indexu (aby si pamatoval pořadí)
INDEX_FILE="/tmp/wallpaper_index"

# Přechodový efekt (volitelné: grow, outer, wave, simple, any...)
TRANSITION="grow"
# -------------------

# Zkontroluje, zda běží swww daemon, pokud ne, spustí ho
if ! pgrep -x "swww-daemon" > /dev/null; then
    swww-daemon &
    sleep 1
fi

# Načte všechny obrázky do pole
PICS=("$WALLPAPER_DIR"/*)
NUM_PICS=${#PICS[@]}

# Pokud složka neobsahuje obrázky, skončí
if [ $NUM_PICS -eq 0 ]; then
    notify-send "Chyba" "Žádné tapety ve složce $WALLPAPER_DIR"
    exit 1
fi

# Přečte aktuální index, pokud soubor neexistuje, začne od 0
if [ -f "$INDEX_FILE" ]; then
    CURRENT_INDEX=$(cat "$INDEX_FILE")
else
    CURRENT_INDEX=0
fi

# Vypočítá další index (cyklicky: pokud dojde na konec, začne od 0)
NEXT_INDEX=$(( (CURRENT_INDEX + 1) % NUM_PICS ))

# Uloží nový index
echo "$NEXT_INDEX" > "$INDEX_FILE"

# Nastaví tapetu pomocí swww
NEXT_WALLPAPER="${PICS[$NEXT_INDEX]}"
swww img "$NEXT_WALLPAPER" --transition-type "$TRANSITION" --transition-fps 60

# (Volitelné) Pošle notifikaci o změně
# notify-send "Wallpaper změněn" "$(basename "$NEXT_WALLPAPER")"
