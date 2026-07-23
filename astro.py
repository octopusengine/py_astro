import ephem
import matplotlib.pyplot as plt
from datetime import datetime, timedelta, timezone
import json
from pathlib import Path
import sys
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from lib.wrapp_ephem import BRIGHT_STARS, CONSTELLATIONS, PLANETS

if len(sys.argv) > 2:
    raise SystemExit("Použití: python astro.py [konfigurace.json]")

CONFIG_FILE = (
    Path(sys.argv[1])
    if len(sys.argv) == 2
    else Path(__file__).with_name("astro_config.json")
)


def load_location():
    with CONFIG_FILE.open(encoding="utf-8") as location_file:
        location = json.load(location_file)

    for key in ("label", "latitude", "longitude"):
        if key not in location:
            raise ValueError(f"V souboru {CONFIG_FILE.name} chybí položka '{key}'.")

    return location


location = load_location()
main_label = location["label"]
mode = location.get("mode", "dark").lower()
if mode not in {"dark", "light"}:
    raise ValueError("Položka 'mode' v astro_config.json musí být 'dark' nebo 'light'.")

lines = location.get("lines", True)
if not isinstance(lines, bool):
    raise ValueError("Položka 'lines' v astro_config.json musí být true nebo false.")

autosave = location.get("autosave", "off").lower()
if autosave not in {"on", "off"}:
    raise ValueError("Položka 'autosave' v astro_config.json musí být 'on' nebo 'off'.")

img_directory = location.get("img_directory", "images")
if not isinstance(img_directory, str) or not img_directory.strip():
    raise ValueError("Položka 'img_directory' v astro_config.json musí být neprázdný text.")

try:
    step_minutes = int(location.get("step", 60))
except (TypeError, ValueError) as error:
    raise ValueError("Položka 'step' v astro_config.json musí být celé číslo minut.") from error
if step_minutes <= 0:
    raise ValueError("Položka 'step' v astro_config.json musí být větší než nula.")

timezone_name = location.get("timezone", "UTC")
try:
    observation_timezone = ZoneInfo(timezone_name)
except ZoneInfoNotFoundError as error:
    raise ValueError(
        "Položka 'timezone' musí obsahovat platný název časového pásma, "
        "například 'Europe/Madrid'."
    ) from error

plt.style.use("dark_background" if mode == "dark" else "default")
foreground_color = "white" if mode == "dark" else "black"
main_line_color = foreground_color
secondary_line_color = "silver"
planet_colors = {
    planet["name"]: (
        "white" if mode == "dark" and planet["color"] == "black"
        else "goldenrod" if mode == "light" and planet["color"] == "yellow"
        else planet["color"]
    )
    for planet in PLANETS
}

POINT_SIZE = 2
FS = 10
TXT = 3
def anum(a):
    sa = str(a).split(":")
    if len(sa) > 1:
        angle_float = float(sa[0]) + float(sa[1])/60
    else:
        angle_float = float(sa[0])
    return angle_float

o = ephem.Observer()
o.lat = str(location["latitude"])
o.lon = str(location["longitude"])
if "elevation" in location:
    o.elevation = float(location["elevation"])

configured_datetime = location.get("datetime")
if configured_datetime:
    try:
        current_datetime = datetime.fromisoformat(configured_datetime)
    except (TypeError, ValueError) as error:
        raise ValueError(
            "Položka 'datetime' v astro_config.json musí mít formát "
            "YYYY-MM-DDTHH:MM:SS."
        ) from error
else:
    current_datetime = datetime.now(observation_timezone)

if current_datetime.tzinfo is None:
    current_datetime = current_datetime.replace(tzinfo=observation_timezone)
else:
    current_datetime = current_datetime.astimezone(observation_timezone)

formatted_datetime = current_datetime.strftime("%y%m%d-%H%M")


def to_utc_datetime(local_datetime):
    return local_datetime.astimezone(timezone.utc).replace(tzinfo=None)

bodies = {planet["name"]: planet["factory"]() for planet in PLANETS}
sun = bodies["Sun"]
moon = bodies["Moon"]

def star_coordinates(o, stars):
    coordinates = []
    for star in stars:
        try:
            objekt_hvezdy = ephem.star(star)
            objekt_hvezdy.compute(o)
            coordinates.append((anum(ephem.degrees(objekt_hvezdy.az)), anum(ephem.degrees(objekt_hvezdy.alt))))
        except KeyError:
            continue
    return coordinates


def constellation_coordinates(o):
    return {
        name: star_coordinates(o, stars)
        for name, stars in CONSTELLATIONS.items()
    }


def all_star_coordinates(o, constellation_points):
    coordinates = []
    for points in constellation_points.values():
        coordinates.extend(points)
    coordinates.extend(star_coordinates(o, BRIGHT_STARS))
    return coordinates

def day_data(o, local_datetime):
    sun_coordinates = []
    moon_coordinates = []
    for hour in range(1, 23):
        local_time = local_datetime.replace(hour=hour, minute=0, second=0, microsecond=0)
        o.date = to_utc_datetime(local_time)

        sun.compute(o)
        moon.compute(o)

        sun_coordinates.append((anum(sun.az), anum(sun.alt)))
        moon_coordinates.append((anum(moon.az), anum(moon.alt)))
    return sun_coordinates, moon_coordinates

o.date = to_utc_datetime(current_datetime)

planet_coordinates = {}
for planet in PLANETS:
    body = bodies[planet["name"]]
    body.compute(o)
    planet_coordinates[planet["name"]] = (anum(body.az), anum(body.alt))

constellation_points = constellation_coordinates(o)
xyh = all_star_coordinates(o, constellation_points)
xys, xym = day_data(o, current_datetime)
xym.append((anum(180), anum(80)))
o.date = to_utc_datetime(current_datetime)

plt.axvline(x=0, color=main_line_color, linestyle='-', label='N')
plt.axvline(x=180, color=secondary_line_color, linestyle='-', label='N')
plt.axvline(x=90, color=secondary_line_color, linestyle='--', label='N')
plt.axvline(x=270, color=secondary_line_color, linestyle='--', label='N')
plt.axvline(x=360, color=main_line_color, linestyle='-', label='N')
plt.axvline(x=450, color=secondary_line_color, linestyle='--', label='N')
plt.axhline(y=0, color=main_line_color, linestyle='-', label='h')

x, y = zip(*xyh)
star_scatter = plt.scatter(x, y, color='purple', s=POINT_SIZE)

constellation_line_artists = {}
if lines:
    for name, points in constellation_points.items():
        if len(points) < 2:
            continue
        x, y = zip(*points)
        line, = plt.plot(x, y, color='mediumpurple', linewidth=0.7, alpha=0.7)
        constellation_line_artists[name] = line

planet_artists = {}
planet_label_artists = {}
for planet in PLANETS:
    x, y = planet_coordinates[planet["name"]]
    planet_artists[planet["name"]] = plt.scatter(
        x, y, color=planet_colors[planet["name"]], s=POINT_SIZE * planet["size_multiplier"]
    )
    if planet["marker_label"]:
        planet_label_artists[planet["name"]] = plt.text(x + TXT, y, planet["marker_label"], fontsize=FS)

i = 0
bright_star_label_artists = {}
for hvezda in BRIGHT_STARS:
    try:
        obj_star = ephem.star(hvezda)
        obj_star.compute(o)
        xt, yt = anum(ephem.degrees(obj_star.az)), anum(ephem.degrees(obj_star.alt))
        bright_star_label_artists[hvezda] = plt.text(xt + TXT, yt, str(i + 1), color='purple', fontsize=FS)
    except KeyError:
        continue
    i += 1

info_str = f"{main_label}: {o.lat},{o.lon} / {current_datetime:%Y-%m-%d %H:%M %Z}"
info_text = plt.text(5, 80, info_str, color=foreground_color, fontsize=FS)

xtxt, ytxt = 390, 81
for index, planet in enumerate(PLANETS, start=1):
    plt.text(xtxt, ytxt - 8 * index, planet["name"], color=planet_colors[planet["name"]], fontsize=FS)

for index, star in enumerate(BRIGHT_STARS, start=len(PLANETS) + 2):
    plt.text(xtxt, ytxt - 8 * index, f"{index - len(PLANETS) - 1}.{star}", color='purple', fontsize=FS)

plt.xlabel('X')
plt.ylabel('Y')

plt.title(f"Šipky ←/→: posun o {step_minutes} minut")

x, y = zip(*xys)
sun_path_artist = plt.scatter(x, y, color='green', s=POINT_SIZE)

x, y = zip(*xym)
moon_path_artist = plt.scatter(x, y, color='silver', s=POINT_SIZE)


def change_observation_time(event):
    global current_datetime

    if event.key not in {"left", "right"}:
        return

    direction = 1 if event.key == "right" else -1
    current_datetime += timedelta(minutes=direction * step_minutes)
    o.date = to_utc_datetime(current_datetime)

    for planet in PLANETS:
        name = planet["name"]
        body = bodies[name]
        body.compute(o)
        x, y = anum(body.az), anum(body.alt)
        planet_artists[name].set_offsets([[x, y]])
        if name in planet_label_artists:
            planet_label_artists[name].set_position((x + TXT, y))

    constellation_points = constellation_coordinates(o)
    star_scatter.set_offsets(all_star_coordinates(o, constellation_points))
    if lines:
        for name, line in constellation_line_artists.items():
            x, y = zip(*constellation_points[name])
            line.set_data(x, y)
    for star, label_artist in bright_star_label_artists.items():
        try:
            body = ephem.star(star)
            body.compute(o)
            label_artist.set_position((anum(ephem.degrees(body.az)) + TXT, anum(ephem.degrees(body.alt))))
        except KeyError:
            continue

    xys, xym = day_data(o, current_datetime)
    xym.append((anum(180), anum(80)))
    sun_path_artist.set_offsets(xys)
    moon_path_artist.set_offsets(xym)

    o.date = to_utc_datetime(current_datetime)
    info_text.set_text(f"{main_label}: {o.lat},{o.lon} / {current_datetime:%Y-%m-%d %H:%M %Z}")
    event.canvas.draw_idle()


plt.gcf().canvas.mpl_connect("key_press_event", change_observation_time)

if autosave == "on":
    image_directory = Path(img_directory)
    if not image_directory.is_absolute():
        image_directory = CONFIG_FILE.parent / image_directory
    image_directory.mkdir(parents=True, exist_ok=True)
    file_name = image_directory / f"graf{formatted_datetime}.png"
    plt.savefig(file_name)

plt.show()
