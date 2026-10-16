-- Hyprland 0.56.2 | migrated from hyprland.conf
-- Original file preserved in the accompanying archive.

local terminal = "kitty"
local fileManager = "dolphin"
local menu = "wofi --show drun"
local mainMod = "SUPER"

-- Physical monitor topology: Samsung | Alienware | Philips
hl.monitor({ output = "HDMI-A-2", mode = "1920x1080@74.97", position = "0x0", scale = 1 })
hl.monitor({ output = "DP-1", mode = "2560x1440@239.97", position = "1920x0", scale = 1 })
hl.monitor({ output = "HDMI-A-1", mode = "1920x1080@74.97", position = "4480x0", scale = 1 })

local workspaceMonitors = {
    "HDMI-A-2", "DP-1", "HDMI-A-1", "DP-1", "DP-1",
    "DP-1", "DP-1", "DP-1", "DP-1", "DP-1",
}
for i, monitor in ipairs(workspaceMonitors) do
    hl.workspace_rule({ workspace = tostring(i), monitor = monitor })
end

hl.on("hyprland.start", function()
    hl.exec_cmd("hyprpaper")
    hl.exec_cmd("waybar")
    hl.exec_cmd("blueman-applet")
end)

hl.env("XCURSOR_SIZE", "24")
hl.env("HYPRCURSOR_SIZE", "24")

hl.config({
    general = {
        gaps_in = 5,
        gaps_out = 20,
        border_size = 2,
        col = {
            active_border = { colors = { "rgba(33ccffee)", "rgba(00ff99ee)" }, angle = 45 },
            inactive_border = "rgba(595959aa)",
        },
        resize_on_border = false,
        allow_tearing = false,
        layout = "dwindle",
    },
    decoration = {
        rounding = 10,
        rounding_power = 2,
        active_opacity = 1.0,
        inactive_opacity = 1.0,
        shadow = { enabled = true, range = 4, render_power = 3, color = "rgba(1a1a1aee)" },
        blur = { enabled = true, size = 3, passes = 1, vibrancy = 0.1696 },
    },
    animations = { enabled = true },
    master = { new_status = "master" },
    misc = { force_default_wallpaper = -1, disable_hyprland_logo = false },
    input = {
        kb_layout = "cz",
        kb_variant = "",
        kb_model = "",
        kb_options = "",
        kb_rules = "",
        follow_mouse = 1,
        scroll_factor = 1.0,
        sensitivity = 0,
        touchpad = { natural_scroll = false },
    },
})

local curves = {
    { "easeOutQuint", { { 0.23, 1 }, { 0.32, 1 } } },
    { "easeInOutCubic", { { 0.65, 0.05 }, { 0.36, 1 } } },
    { "linear", { { 0, 0 }, { 1, 1 } } },
    { "almostLinear", { { 0.5, 0.5 }, { 0.75, 1 } } },
    { "quick", { { 0.15, 0 }, { 0.1, 1 } } },
}
for _, curve in ipairs(curves) do
    hl.curve(curve[1], { type = "bezier", points = curve[2] })
end

local animations = {
    { "global", 10, "default" },
    { "border", 5.39, "easeOutQuint" },
    { "windows", 4.79, "easeOutQuint" },
    { "windowsIn", 4.1, "easeOutQuint", "popin 87%" },
    { "windowsOut", 1.49, "linear", "popin 87%" },
    { "fadeIn", 1.73, "almostLinear" },
    { "fadeOut", 1.46, "almostLinear" },
    { "fade", 3.03, "quick" },
    { "layers", 3.81, "easeOutQuint" },
    { "layersIn", 4, "easeOutQuint", "fade" },
    { "layersOut", 1.5, "linear", "fade" },
    { "fadeLayersIn", 1.79, "almostLinear" },
    { "fadeLayersOut", 1.39, "almostLinear" },
    { "workspaces", 1.94, "almostLinear", "fade" },
    { "workspacesIn", 1.21, "almostLinear", "fade" },
    { "workspacesOut", 1.94, "almostLinear", "fade" },
    { "zoomFactor", 7, "quick" },
}
for _, a in ipairs(animations) do
    local options = { leaf = a[1], enabled = true, speed = a[2], bezier = a[3] }
    if a[4] then options.style = a[4] end
    hl.animation(options)
end

hl.gesture({ fingers = 3, direction = "horizontal", action = "workspace" })
-- Preserved original per-device rule (only effective when such a device exists).
hl.device({ name = "epic-mouse-v1", sensitivity = 1.0 })

hl.bind(mainMod .. " + Q", hl.dsp.exec_cmd(terminal))
hl.bind(mainMod .. " + C", hl.dsp.window.close())
hl.bind(mainMod .. " + M", hl.dsp.exit())
hl.bind(mainMod .. " + E", hl.dsp.exec_cmd(fileManager))
hl.bind(mainMod .. " + J", hl.dsp.window.float({ action = "toggle" }))
hl.bind(mainMod .. " + R", hl.dsp.exec_cmd(menu))
hl.bind(mainMod .. " + P", hl.dsp.window.pseudo())
hl.bind(mainMod .. " + H", hl.dsp.layout("orientationleft"))
hl.bind(mainMod .. " + V", hl.dsp.layout("orientationtop"))
hl.bind(mainMod .. " + X", hl.dsp.exec_cmd("wlogout"))
hl.bind(mainMod .. " + L", hl.dsp.exec_cmd("hyprlock"))
hl.bind(mainMod .. " + left", hl.dsp.focus({ direction = "left" }))
hl.bind(mainMod .. " + right", hl.dsp.focus({ direction = "right" }))
hl.bind(mainMod .. " + up", hl.dsp.focus({ direction = "up" }))
hl.bind(mainMod .. " + down", hl.dsp.focus({ direction = "down" }))
hl.bind(mainMod .. " + Z", hl.dsp.exec_cmd("/home/jerry/.config/hypr/scripts/next_wallpaper.sh"))

for i = 1, 10 do
    local key = i == 10 and "0" or ("F" .. i)
    hl.bind(mainMod .. " + " .. key, hl.dsp.focus({ workspace = i }))
    hl.bind(mainMod .. " + SHIFT + " .. key, hl.dsp.window.move({ workspace = i }))
end
hl.bind(mainMod .. " + S", hl.dsp.workspace.toggle_special("magic"))
hl.bind(mainMod .. " + SHIFT + S", hl.dsp.window.move({ workspace = "special:magic" }))
hl.bind(mainMod .. " + mouse_down", hl.dsp.focus({ workspace = "e+1" }))
hl.bind(mainMod .. " + mouse_up", hl.dsp.focus({ workspace = "e-1" }))
hl.bind(mainMod .. " + mouse:272", hl.dsp.window.drag(), { mouse = true })
hl.bind(mainMod .. " + mouse:273", hl.dsp.window.resize(), { mouse = true })

-- Original config has duplicate volume binds: preserve volume notification sound,
-- while retaining the locked/repeating behavior and the original upper limit of 1.
hl.bind("XF86AudioRaiseVolume", hl.dsp.exec_cmd("wpctl set-volume -l 1 @DEFAULT_AUDIO_SINK@ 5%+ && paplay /usr/share/sounds/freedesktop/stereo/audio-volume-change.oga"), { locked = true, repeating = true })
hl.bind("XF86AudioLowerVolume", hl.dsp.exec_cmd("wpctl set-volume @DEFAULT_AUDIO_SINK@ 5%- && paplay /usr/share/sounds/freedesktop/stereo/audio-volume-change.oga"), { locked = true, repeating = true })
hl.bind("XF86AudioMute", hl.dsp.exec_cmd("wpctl set-mute @DEFAULT_AUDIO_SINK@ toggle"), { locked = true, repeating = true })
hl.bind("XF86AudioMicMute", hl.dsp.exec_cmd("wpctl set-mute @DEFAULT_AUDIO_SOURCE@ toggle"), { locked = true, repeating = true })
hl.bind("XF86MonBrightnessUp", hl.dsp.exec_cmd("brightnessctl -e4 -n2 set 5%+"), { locked = true, repeating = true })
hl.bind("XF86MonBrightnessDown", hl.dsp.exec_cmd("brightnessctl -e4 -n2 set 5%-"), { locked = true, repeating = true })
hl.bind("XF86AudioNext", hl.dsp.exec_cmd("playerctl next"), { locked = true })
hl.bind("XF86AudioPause", hl.dsp.exec_cmd("playerctl play-pause"), { locked = true })
hl.bind("XF86AudioPlay", hl.dsp.exec_cmd("playerctl play-pause"), { locked = true })
hl.bind("XF86AudioPrev", hl.dsp.exec_cmd("playerctl previous"), { locked = true })

local screenshotDir = "~/Obrazky/Screenshots/"
local screenshotName = "screenshot_$(date +'%Y-%m-%d_%H-%M-%S').png"
hl.bind(mainMod .. " + F11", hl.dsp.exec_cmd("grimblast copysave output " .. screenshotDir .. screenshotName))
hl.bind(mainMod .. " + SHIFT + F11", hl.dsp.exec_cmd("grimblast copysave area " .. screenshotDir .. screenshotName))

-- Original virt-manager window rules were disabled, so they remain disabled.
