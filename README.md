# Typotrix

A typographic display app for Raspberry Pi Zero 2W + HyperPixel 4.0 Square touchscreen. Cycles through Google Fonts displayed as a 2x2 grid of letters from curated 4-letter words. Touch interactive with colormind.io colour circles.

## Hardware

- Raspberry Pi Zero 2W
- Pimoroni HyperPixel 4.0 Square (touch variant)
- MicroSD card (8GB+)

## Controls

| Gesture | Action |
|---|---|
| Tap left half | Previous font |
| Tap right half | Next font |
| Hold anywhere | Place colormind circle (grows while held) |
| Hold centre | Invert display |

## Fresh SD Card Setup

### 1. Flash the OS

Use [Raspberry Pi Imager](https://www.raspberrypi.com/software/) to flash **Raspberry Pi OS Lite (64-bit)** to the SD card. During setup in the imager:
- Set hostname to `typotrix`
- Set username to `milo`
- Enable SSH
- Set your wifi credentials

### 2. SSH in
```bash
ssh milo@typotrix.local
```

### 3. Install HyperPixel display driver
```bash
pip install pimoroni-hyperpixel4-square --break-system-packages
```

Or follow [Pimoroni's setup guide](https://github.com/pimoroni/hyperpixel4).

### 4. Install Python dependencies
```bash
pip install pygame requests --break-system-packages
```

### 5. Download the app
```bash
curl -o ~/typotrix.py https://raw.githubusercontent.com/miloze/Typotrix_1.0/master/typotrix.py
```

### 6. Set up autoboot
```bash
echo 'if [ -z "$DISPLAY" ] && [ "$(tty)" = "/dev/tty1" ]; then startx; fi' >> ~/.bash_profile
echo '/usr/bin/python3 /home/milo/typotrix.py' > ~/.xinitrc
sudo raspi-config nonint do_boot_behaviour B2
```

### 7. Reboot
```bash
sudo reboot
```

The app will boot automatically on every startup. Fonts are downloaded from Google Fonts on first use and cached in `~/fonts/`.

## Web Preview

A browser version is available at:

**[https://miloze.github.io/Typotrix_1.0](https://miloze.github.io/Typotrix_1.0)**

Click left half to go back, right half to go forward, hold to place a circle, arrow keys also work.

## Files

| File | Description |
|---|---|
| `typotrix.py` | Raspberry Pi app (pygame) |
| `index.html` | Browser preview (vanilla JS) |

## Development Notes

- Raspberry Pi Zero 2W has no GPU acceleration — pygame runs on CPU
- HyperPixel 4.0 Square touch coordinates are x-axis mirrored
- FINGERUP x coordinate is unreliable on this display — navigation uses FINGERDOWN position only
- Fonts cached to `~/fonts/` — delete to force re-download
- Colormind API used for circle colours — falls back to random RGB if offline
