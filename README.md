# Astro Sky Viewer

A small Python program that plots the visible sky for a configured Earth-based observing location. It shows the Sun, Moon, selected planets, bright stars, and a few constellations.

## Requirements

- Python 3.10 or newer
- `pip`

The required Python packages are listed in `requirements.txt`. The `tzdata` package provides IANA time zones such as `Europe/Prague` and is especially required on Windows.

## Installation

### Windows (PowerShell)

```powershell
cd path\to\py_astro
py -m venv venv
.\venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

If PowerShell prevents activation, use the virtual-environment Python directly instead:

```powershell
.\venv\Scripts\python.exe -m pip install -r requirements.txt
.\venv\Scripts\python.exe astro.py
```

### Linux

```bash
cd /path/to/py_astro
python3 -m venv venv
source venv/bin/activate
python -m pip install -r requirements.txt
```

On Debian or Ubuntu, install the `python3-venv` system package first if the `venv` command is unavailable.

## Running the program

Run with the default configuration:

```bash
python astro.py
```

The default file is `astro_config.json`.

To use another configuration, pass its filename as a positional argument:

```bash
python astro.py astro_conf_menorca.json
```

Only one optional configuration filename is accepted.

## Configuration

Each configuration is a JSON file. `label`, `latitude`, and `longitude` are required. The following example uses Menorca:

```json
{
  "label": "Menorca",
  "latitude": 39.9496,
  "longitude": 4.1103,
  "elevation": 100,
  "datetime": "2026-08-12T20:30:00",
  "timezone": "Europe/Madrid",
  "mode": "dark",
  "lines": true,
  "autosave": "off",
  "img_directory": "images",
  "step": 60
}
```

| Setting | Description |
| --- | --- |
| `label` | Location name displayed in the chart. |
| `latitude` | Latitude in decimal degrees; north is positive. |
| `longitude` | Longitude in decimal degrees; east is positive. |
| `elevation` | Optional elevation in metres. |
| `datetime` | Optional local observation time in ISO format, for example `2026-08-12T20:30:00`. Omit it or set it to an empty string to use the current time. |
| `timezone` | IANA time-zone name, for example `Europe/Prague` or `Europe/Madrid`. Local configuration time is converted to UTC automatically for PyEphem. If omitted, the legacy default is `UTC`. |
| `mode` | `dark` or `light`; defaults to `dark`. |
| `lines` | `true` connects stars in each configured constellation with lines; `false` shows the stars without connecting lines. Defaults to `true`. |
| `autosave` | `on` saves the generated PNG automatically; `off` does not. Defaults to `off`. |
| `img_directory` | Output directory for automatically saved images. Relative paths are resolved relative to the configuration file. Defaults to `images`. |
| `step` | Number of minutes to move through time with the arrow keys. Must be a positive integer; defaults to `60`. |

## Interactive controls

With the plot window focused:

- Left arrow: move the observation time backward by `step` minutes.
- Right arrow: move the observation time forward by `step` minutes.

The Back and Forward buttons in the standard Matplotlib toolbar control plot-view history (pan and zoom); they do not change the observation time.

## Notes

PyEphem `Observer` represents a location on Earth. This program therefore supports Earth-based locations only; Mars and other planetary surface locations require a different astronomy library with planetary-observer support.
