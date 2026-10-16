#!/bin/bash

# Krok animace (0, 1, nebo 2)
i=0
# Tři "noty", které budeme střídat
notes=("♪" "♫" "♬")

while true; do
    is_playing=false

    # Hledáme přehrávač (včetně "zen")
    for player in $(playerctl -l 2>/dev/null); do
        if [[ $player == *"firefox"* || $player == *"chrome"* || $player == *"chromium"* || $player == *"zen"* ]]; then
            url=$(playerctl --player=$player metadata xesam:url 2>/dev/null)
            status=$(playerctl --player=$player status 2>/dev/null)

            # Pokud hraje A ZÁROVEŇ je to z YouTube...
            if [[ $status == "Playing" && $url == *"youtube.com"* ]]; then
                is_playing=true
                break
            fi
        fi
    done

    if [ "$is_playing" = true ]; then
        # HRAJE: Zobraz ikonu a přidej k ní jednu z not podle kroku animace
        current_note=${notes[$i]}
        echo '{"text": " '"$current_note"'", "class": "youtube", "tooltip": "Hraje YouTube"}'

        # Posuň se na další "snímek" animace
        i=$(((i + 1) % ${#notes[@]}))
    else
        # NEHRAJE: Nevypisuj nic (modul se schová)
        echo ''

        # Vynuluj animaci na začátek
        i=0
    fi

    sleep 1 # Rychlost animace (1 "snímek" za sekundu)
done
