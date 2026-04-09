import base64
import sqlite3
import time
from pathlib import Path

import altair as alt
import pandas as pd
import requests
import streamlit as st

from pokemon_ETL_game import CSV_PATH, catch_pokemon

PAGE_TITLE = "Pokemon ETL Dashboard"
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
POKEMON_IMAGE = DATA_DIR / "pikachuu.png"
POKEDEX_HEADER_IMAGE = Path(r"c:\Users\Freja\Downloads\ChatGPT Image Apr 9, 2026, 04_52_48 PM.png")
POKEDEX_IMAGE_DIR = DATA_DIR / "pokedex_images"
POKEDEX_CACHE_PATH = DATA_DIR / "pokedex_cache.csv"
POKEDEX_CACHE_MAX_AGE_SECONDS = 60 * 60 * 24 * 7
POKEAPI_POKEMON_LIST_URL = "https://pokeapi.co/api/v2/pokemon?limit=151"
POKEAPI_POKEMON_URL = "https://pokeapi.co/api/v2/pokemon/{pokemon_id}"
POKEAPI_SPECIES_URL = "https://pokeapi.co/api/v2/pokemon-species/{pokemon_id}"

TYPE_QUERY = """
WITH RECURSIVE split_types (pokemon_name, type_name, remaining) AS (
    SELECT
        name,
        TRIM(SUBSTR(types, 1, INSTR(types || ',', ',') - 1)),
        LTRIM(SUBSTR(types || ',', INSTR(types || ',', ',') + 1))
    FROM pokemon
    UNION ALL
    SELECT
        pokemon_name,
        TRIM(SUBSTR(remaining, 1, INSTR(remaining, ',') - 1)),
        LTRIM(SUBSTR(remaining, INSTR(remaining, ',') + 1))
    FROM split_types
    WHERE remaining <> ''
)
SELECT type_name, COUNT(*) AS catches
FROM split_types
WHERE type_name <> ''
GROUP BY type_name
ORDER BY catches DESC, type_name ASC
"""

HEAVIEST_QUERY = """
SELECT name, weight, height, types
FROM pokemon
ORDER BY weight DESC
LIMIT 5
"""

TALLEST_QUERY = """
SELECT name, height, weight, types
FROM pokemon
ORDER BY height DESC
LIMIT 5
"""

DUPLICATE_QUERY = """
SELECT name, COUNT(*) AS catches
FROM pokemon
GROUP BY name
HAVING COUNT(*) > 1
ORDER BY catches DESC, name ASC
LIMIT 10
"""

TYPE_COLORS = {
    "bug": "#92BC2C",
    "dark": "#595761",
    "dragon": "#0C69C8",
    "electric": "#F2D94E",
    "fairy": "#EE90E6",
    "fighting": "#D3425F",
    "fire": "#FBA54C",
    "flying": "#A1BBEC",
    "ghost": "#5F6DBC",
    "grass": "#5FBD58",
    "ground": "#DA7C4D",
    "ice": "#75D0C1",
    "normal": "#A0A29F",
    "poison": "#B763CF",
    "psychic": "#FA8581",
    "rock": "#C9BB8A",
    "steel": "#5695A3",
    "water": "#539DDF",
}

STAT_LABELS = {
    "hp": "HP",
    "attack": "Attack",
    "defense": "Defense",
    "speed": "Speed",
}


st.set_page_config(page_title=PAGE_TITLE, page_icon="⚡", layout="wide")


@st.cache_data(show_spinner=False)
def load_pokemon_data():
    if not CSV_PATH.exists():
        return pd.DataFrame(columns=["id", "name", "height", "weight", "types"])

    dataframe = pd.read_csv(CSV_PATH)
    if dataframe.empty:
        return dataframe

    dataframe["name"] = dataframe["name"].str.title()
    return dataframe


def extract_flavor_text(entries):
    for entry in entries:
        if entry["language"]["name"] == "en":
            return entry["flavor_text"].replace("\n", " ").replace("\f", " ").strip()
    return "No Pokedex description available."


def parse_evolution_chain(chain_node):
    stages = []

    def walk(node):
        species_name = node["species"]["name"].title()
        stages.append(species_name)
        for evolution in node["evolves_to"]:
            walk(evolution)

    walk(chain_node)
    deduped_stages = []
    for stage in stages:
        if stage not in deduped_stages:
            deduped_stages.append(stage)
    return deduped_stages


def cache_is_fresh(cache_path, max_age_seconds):
    if not cache_path.exists():
        return False
    return (time.time() - cache_path.stat().st_mtime) < max_age_seconds


@st.cache_data(show_spinner=False)
def read_cached_pokedex_dataframe(cache_path_str):
    cache_path = Path(cache_path_str)
    dataframe = pd.read_csv(cache_path)
    fill_columns = ["type_1", "type_2", "abilities", "color", "habitat", "flavor_text", "evolution_chain", "sprite_url"]
    for column in fill_columns:
        if column in dataframe.columns:
            dataframe[column] = dataframe[column].fillna("")
    return dataframe


def fetch_and_cache_pokedex_data(limit=151, cache_path=POKEDEX_CACHE_PATH):
    session = requests.Session()
    response = session.get(POKEAPI_POKEMON_LIST_URL, timeout=20)
    response.raise_for_status()
    pokemon_entries = response.json()["results"][:limit]

    pokedex_rows = []
    for index, _ in enumerate(pokemon_entries, start=1):
        pokemon = session.get(POKEAPI_POKEMON_URL.format(pokemon_id=index), timeout=20).json()
        species = session.get(POKEAPI_SPECIES_URL.format(pokemon_id=index), timeout=20).json()
        evolution_chain = session.get(species["evolution_chain"]["url"], timeout=20).json()

        stats = {entry["stat"]["name"]: entry["base_stat"] for entry in pokemon["stats"]}
        types = [entry["type"]["name"] for entry in pokemon["types"]]
        abilities = [entry["ability"]["name"].replace("-", " ").title() for entry in pokemon["abilities"]]

        pokedex_rows.append(
            {
                "id": pokemon["id"],
                "name": pokemon["name"].title(),
                "type_1": types[0].title(),
                "type_2": types[1].title() if len(types) > 1 else "",
                "height": pokemon["height"],
                "weight": pokemon["weight"],
                "hp": stats.get("hp"),
                "attack": stats.get("attack"),
                "defense": stats.get("defense"),
                "speed": stats.get("speed"),
                "abilities": ", ".join(abilities),
                "color": species["color"]["name"].title(),
                "habitat": species["habitat"]["name"].title() if species["habitat"] else "Unknown",
                "flavor_text": extract_flavor_text(species["flavor_text_entries"]),
                "evolution_chain": " -> ".join(parse_evolution_chain(evolution_chain["chain"])),
                "sprite_url": pokemon["sprites"]["other"]["official-artwork"]["front_default"]
                or pokemon["sprites"]["front_default"],
            }
        )

    dataframe = pd.DataFrame(pokedex_rows)
    cache_path.parent.mkdir(parents=True, exist_ok=True)
    dataframe.to_csv(cache_path, index=False)
    read_cached_pokedex_dataframe.clear()
    return dataframe


def load_pokedex_data(limit=151, force_refresh=False):
    if not force_refresh and cache_is_fresh(POKEDEX_CACHE_PATH, POKEDEX_CACHE_MAX_AGE_SECONDS):
        return read_cached_pokedex_dataframe(str(POKEDEX_CACHE_PATH))

    if not force_refresh and POKEDEX_CACHE_PATH.exists():
        return read_cached_pokedex_dataframe(str(POKEDEX_CACHE_PATH))

    return fetch_and_cache_pokedex_data(limit=limit, cache_path=POKEDEX_CACHE_PATH)


def build_connection(dataframe):
    connection = sqlite3.connect(":memory:")
    dataframe.to_sql("pokemon", connection, index=False, if_exists="replace")
    return connection


def run_query(connection, query):
    return pd.read_sql_query(query, connection)


def refresh_collection(rounds):
    return catch_pokemon(rounds=rounds, delay=0.2)


def format_catch_summary(caught_pokemon):
    if not caught_pokemon:
        return "No Pokemon were caught this round."

    summary_lines = []
    for pokemon in caught_pokemon:
        type_text = pokemon["types"].title()
        summary_lines.append(
            f"#{int(pokemon['id']):03d} {pokemon['name'].title()} - {type_text}"
        )
    return "\n".join(summary_lines)


def count_local_pokedex_images():
    if not POKEDEX_IMAGE_DIR.exists():
        return 0

    return sum(
        1
        for file_path in POKEDEX_IMAGE_DIR.rglob("*")
        if file_path.suffix.lower() in {".png", ".jpg", ".jpeg", ".webp"}
    )


@st.cache_data(show_spinner=False)
def build_local_image_index(image_dir_str):
    image_dir = Path(image_dir_str)
    if not image_dir.exists():
        return {}

    image_index = {}
    for file_path in image_dir.rglob("*"):
        if file_path.suffix.lower() not in {".png", ".jpg", ".jpeg", ".webp"}:
            continue
        stem = file_path.stem.lower()
        image_index[stem] = str(file_path)
    return image_index


def find_local_pokemon_image(pokemon_id, pokemon_name, image_index):
    normalized_name = pokemon_name.lower().replace(".", "").replace("'", "").replace("♀", "f").replace("♂", "m")
    candidate_patterns = [
        f"{pokemon_id}",
        f"{pokemon_id:03d}",
        normalized_name,
        normalized_name.replace("-", ""),
        normalized_name.replace("-", "_"),
    ]

    for stem, file_path in image_index.items():
        if any(pattern in stem for pattern in candidate_patterns):
            return file_path

    return None


def render_type_badges(type_names):
    badge_markup = []
    for type_name in type_names:
        if pd.isna(type_name):
            continue
        type_name = str(type_name).strip()
        if not type_name:
            continue
        color = TYPE_COLORS.get(type_name.lower(), "#2A4B9B")
        badge_markup.append(
            f"<span style='background:{color};color:#10203f;padding:0.28rem 0.7rem;border-radius:999px;"
            f"font-weight:700;font-size:0.82rem;margin-right:0.35rem;display:inline-block'>{type_name}</span>"
        )
    return "".join(badge_markup)


def render_stat_bars(pokemon):
    stat_rows = []
    for stat_key, label in STAT_LABELS.items():
        stat_value = int(pokemon[stat_key])
        bar_width = min(int((stat_value / 180) * 100), 100)
        stat_rows.append(
            "<div style='margin:0.55rem 0;'>"
            f"<div style='display:flex;justify-content:space-between;font-size:0.9rem;color:#24324d;font-weight:700;'>"
            f"<span>{label}</span><strong>{stat_value}</strong></div>"
            "<div style='background:rgba(27,42,82,0.14);border-radius:999px;height:10px;overflow:hidden;'>"
            f"<div style='width:{bar_width}%;height:10px;background:linear-gradient(90deg,#ffd34d,#ff8a3d);'></div>"
            "</div></div>"
        )
    return "".join(stat_rows)


def render_pokedex_buttons():
    return """
    <div class='hardware-bottom'>
        <div class='speaker-grid'>
            <span></span><span></span><span></span>
            <span></span><span></span><span></span>
        </div>
        <div class='button-row'>
            <div class='joypad'></div>
            <div class='action-buttons'>
                <div class='action-button teal'></div>
                <div class='action-button yellow'></div>
            </div>
        </div>
    </div>
    """


def render_responsive_header_image(image_path):
    if not image_path.exists():
        return ""

    encoded_image = base64.b64encode(image_path.read_bytes()).decode("ascii")
    return (
        "<div class='pokedex-header-art'>"
        f"<img src='data:image/png;base64,{encoded_image}' alt='Pokedex header artwork' />"
        "</div>"
    )


st.markdown(
    """
    <style>
    :root {
        --ink: #24324d;
        --ink-strong: #1b2a52;
        --pokedex-red: #d93b33;
        --pokedex-red-deep: #a8211b;
        --pokedex-yellow: #ffd34d;
        --pokedex-blue: #8fd3ff;
        --panel-cream: #fffaf0;
        --panel-sky: #eef7ff;
    }
    .stApp {
        background:
            radial-gradient(circle at top left, rgba(255, 214, 10, 0.20), transparent 28%),
            radial-gradient(circle at top right, rgba(59, 76, 202, 0.14), transparent 30%),
            linear-gradient(180deg, #fff8e8 0%, #fffdf7 45%, #f4f8ff 100%);
        color: var(--ink);
    }
    .stApp, .stApp p, .stApp li, .stApp label, .stApp span, .stApp div {
        color: var(--ink);
    }
    .stApp h1, .stApp h2, .stApp h3, .stApp h4, .stApp h5, .stApp h6 {
        color: var(--ink-strong);
    }
    section[data-testid="stSidebar"] {
        background:
            radial-gradient(circle at top, rgba(255, 211, 77, 0.18), transparent 26%),
            linear-gradient(180deg, #d93b33 0%, #bd2d27 34%, #274b9f 100%);
    }
    section[data-testid="stSidebar"] * {
        color: #f4f7ff !important;
    }
    section[data-testid="stSidebar"] .stButton button {
        color: #f4f7ff !important;
        border-color: rgba(244, 247, 255, 0.32) !important;
        background: rgba(255, 255, 255, 0.08) !important;
    }
    section[data-testid="stSidebar"] code {
        color: #8ff7bf !important;
        background: rgba(0, 0, 0, 0.22) !important;
    }
    .hero-card {
        background: rgba(255, 255, 255, 0.88);
        border: 3px solid #2a4b9b;
        border-radius: 24px;
        padding: 1.4rem;
        box-shadow: 0 14px 30px rgba(42, 75, 155, 0.14);
        position: relative;
        overflow: hidden;
        margin-bottom: 1.35rem;
    }
    .sidebar-pikachu {
        display: flex;
        justify-content: center;
        margin: 0.2rem 0 0.75rem 0;
    }
    .sidebar-pikachu img {
        max-height: 140px !important;
        width: auto !important;
        object-fit: contain;
    }
    .hero-card::after {
        content: "";
        position: absolute;
        inset: auto -10% -30% auto;
        width: 220px;
        height: 220px;
        border-radius: 50%;
        background: radial-gradient(circle, rgba(255,203,5,0.28) 0%, rgba(255,203,5,0) 70%);
    }
    .summary-console {
        background: linear-gradient(180deg, #fff8eb 0%, #fffdf6 100%);
        border: 2px solid rgba(42, 75, 155, 0.16);
        border-radius: 20px;
        padding: 1rem;
        margin-bottom: 1rem;
        box-shadow: 0 12px 24px rgba(42, 75, 155, 0.08);
        color: var(--ink);
    }
    .summary-console strong {
        color: var(--ink-strong);
    }
    .overview-note {
        background: linear-gradient(135deg, rgba(255, 244, 204, 0.98) 0%, rgba(255, 233, 164, 0.94) 100%);
        border: 1px solid rgba(217, 59, 51, 0.18);
        border-radius: 20px;
        padding: 1rem 1.1rem;
        margin-bottom: 1rem;
        box-shadow: 0 10px 20px rgba(217, 59, 51, 0.08);
    }
    .overview-note-title {
        color: var(--ink-strong);
        font-size: 0.82rem;
        font-weight: 800;
        letter-spacing: 0.08em;
        text-transform: uppercase;
        margin-bottom: 0.35rem;
    }
    .overview-note-copy {
        color: var(--ink);
        font-size: 1rem;
        line-height: 1.5;
    }
    .chart-card {
        background: linear-gradient(180deg, rgba(255, 250, 240, 0.98), rgba(255, 255, 255, 0.98));
        border: 1px solid rgba(42, 75, 155, 0.14);
        border-radius: 24px;
        padding: 0.9rem 1rem 0.4rem 1rem;
        box-shadow: 0 16px 28px rgba(42, 75, 155, 0.10);
        margin-bottom: 1.2rem;
    }
    .chart-card-title {
        color: var(--ink-strong);
        font-size: 1.05rem;
        font-weight: 800;
        margin-bottom: 0.35rem;
    }
    .chart-card-copy {
        color: var(--ink);
        font-size: 0.9rem;
        margin-bottom: 0.35rem;
    }
    .pokedex-shell {
        background: transparent;
        border-radius: 34px;
        padding: 0;
        box-shadow: none;
        border: none;
        position: relative;
        overflow: visible;
    }
    .pokedex-screen {
        background: transparent;
        border-radius: 0;
        padding: 0;
        min-height: 100%;
        border: none;
        box-shadow: none;
    }
    .pokedex-header-art {
        display: block;
        margin: 0 0 0.9rem 0;
    }
    .pokedex-header-art img {
        display: block;
        width: 100%;
        max-width: calc(100% - 4.8rem);
        min-width: 280px;
        height: auto;
    }
    @media (max-width: 900px) {
        .pokedex-header-art img {
            max-width: calc(100% - 1.5rem);
            min-width: 0;
        }
    }
    .screen-label, .hero-kicker {
        color: #d14b15;
        font-size: 0.9rem;
        font-weight: 700;
        letter-spacing: 0.08em;
        text-transform: uppercase;
    }
    .device-meta {
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 1rem;
        margin-bottom: 0.85rem;
    }
    .device-meta-text {
        color: #d9ecff;
        font-size: 0.82rem;
        font-weight: 700;
        letter-spacing: 0.03em;
    }
    .device-meta-pill {
        background: rgba(255,255,255,0.14);
        color: #f4f7ff;
        border: 1px solid rgba(255,255,255,0.18);
        border-radius: 999px;
        padding: 0.28rem 0.7rem;
        font-size: 0.74rem;
        font-weight: 800;
        white-space: nowrap;
    }
    .hero-title {
        color: var(--ink-strong);
        font-size: 2.5rem;
        font-weight: 800;
        line-height: 1.1;
        margin-bottom: 0.6rem;
    }
    .hero-copy { color: var(--ink); font-size: 1.05rem; }
    .code-chip, .dex-pill {
        background: #1b2a52;
        border-radius: 999px;
        color: #fff8e8 !important;
        display: inline-block;
        font-size: 0.9rem;
        margin-top: 0.8rem;
        padding: 0.45rem 0.8rem;
    }
    .dex-pill {
        background: #ffd34d;
        color: #6e2400;
        margin-top: 0;
        margin-bottom: 0.75rem;
        font-weight: 800;
        font-size: 0.78rem;
    }
    .dex-title {
        color: var(--ink-strong);
        font-size: 2rem;
        font-weight: 800;
        line-height: 1.05;
        margin-bottom: 0.3rem;
    }
    .dex-copy {
        color: var(--ink);
        font-size: 0.98rem;
        line-height: 1.55;
    }
    .mini-card {
        background: linear-gradient(180deg, rgba(255, 250, 240, 0.98), rgba(255, 255, 255, 0.96));
        border: 1px solid rgba(42, 75, 155, 0.14);
        border-radius: 18px;
        padding: 0.9rem;
        margin-bottom: 0.8rem;
    }
    .caught-gallery-card {
        background: linear-gradient(180deg, rgba(255, 250, 240, 0.98), rgba(239, 247, 255, 0.94));
        border: 1px solid rgba(42, 75, 155, 0.14);
        border-radius: 18px;
        padding: 0.85rem;
        text-align: center;
        min-height: 100%;
        box-shadow: 0 10px 20px rgba(42, 75, 155, 0.08);
    }
    .caught-gallery-card img {
        max-height: 140px !important;
        width: auto !important;
        object-fit: contain;
        margin: 0 auto 0.35rem auto;
    }
    .caught-gallery-name {
        color: var(--ink-strong);
        font-weight: 800;
        font-size: 1rem;
        margin-top: 0.25rem;
    }
    .caught-gallery-meta {
        color: var(--ink);
        font-size: 0.86rem;
        margin-top: 0.15rem;
    }
    .caught-gallery-stat {
        color: var(--ink);
        font-size: 0.84rem;
        margin-top: 0.1rem;
    }
    .mini-label {
        color: #d14b15;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        font-size: 0.75rem;
        font-weight: 800;
    }
    .mini-value {
        color: var(--ink-strong);
        font-size: 1.05rem;
        font-weight: 700;
        margin-top: 0.2rem;
    }
    .screen-divider {
        height: 1px;
        background: linear-gradient(90deg, rgba(255,255,255,0.08), rgba(255,255,255,0.38), rgba(255,255,255,0.08));
        margin: 0.9rem 0 1rem 0;
    }
    .status-strip {
        display: flex;
        align-items: center;
        gap: 0.5rem;
        color: var(--ink);
        font-size: 0.86rem;
        margin-top: 0.5rem;
        font-weight: 700;
    }
    .status-dot {
        width: 10px;
        height: 10px;
        border-radius: 50%;
        background: #7df08f;
        box-shadow: 0 0 10px rgba(125,240,143,0.8);
    }
    .status-dot.offline {
        background: #ff9f9f;
        box-shadow: 0 0 10px rgba(255,159,159,0.8);
    }
    .caught-badge, .missing-badge {
        padding: 0.35rem 0.75rem;
        border-radius: 999px;
        display: inline-block;
        font-size: 0.84rem;
        font-weight: 800;
        margin-top: 0.6rem;
    }
    .caught-badge { background: #c7f2c8; color: #165b23; }
    .missing-badge { background: #f6d5d5; color: #8b2222; }
    .hardware-bottom {
        margin-top: 1rem;
        display: flex;
        align-items: flex-end;
        justify-content: space-between;
        gap: 1rem;
    }
    .button-row { display: flex; align-items: center; gap: 1rem; }
    .joypad {
        width: 62px;
        height: 62px;
        border-radius: 16px;
        background: linear-gradient(180deg, #2a4254 0%, #172733 100%);
        box-shadow: inset 0 0 0 2px rgba(255,255,255,0.08);
        position: relative;
    }
    .joypad::before, .joypad::after {
        content: "";
        position: absolute;
        background: #90a9bb;
        border-radius: 999px;
    }
    .joypad::before { width: 38px; height: 10px; top: 26px; left: 12px; }
    .joypad::after { width: 10px; height: 38px; top: 12px; left: 26px; }
    .action-buttons { display: flex; gap: 0.7rem; }
    .action-button {
        width: 22px;
        height: 54px;
        border-radius: 999px;
        transform: rotate(32deg);
        box-shadow: inset 0 0 0 2px rgba(255,255,255,0.18);
    }
    .action-button.teal { background: linear-gradient(180deg, #64dfdf 0%, #1d8f96 100%); }
    .action-button.yellow { background: linear-gradient(180deg, #ffe27a 0%, #d5a600 100%); }
    .speaker-grid {
        display: grid;
        grid-template-columns: repeat(3, 10px);
        gap: 0.38rem;
        align-self: center;
    }
    .speaker-grid span {
        width: 10px;
        height: 10px;
        border-radius: 50%;
        background: rgba(75, 8, 8, 0.45);
        box-shadow: inset 0 1px 2px rgba(255,255,255,0.14);
    }
    div[data-testid="stMetric"] {
        background: linear-gradient(180deg, rgba(255, 250, 240, 0.96), rgba(255, 255, 255, 0.96));
        border: 1px solid rgba(42, 75, 155, 0.16);
        border-radius: 18px;
        padding: 0.4rem;
        box-shadow: 0 10px 18px rgba(42, 75, 155, 0.06);
    }
    div[data-testid="stAlert"][kind="success"] {
        background: linear-gradient(135deg, rgba(255, 244, 204, 0.98) 0%, rgba(255, 233, 164, 0.94) 100%) !important;
        border: 1px solid rgba(255, 211, 77, 0.35) !important;
        color: var(--ink-strong) !important;
    }
    div[data-testid="stMetric"] * {
        color: var(--ink-strong) !important;
    }
    div[data-testid="stMetric"] label {
        color: var(--ink) !important;
    }
    div[data-testid="stMetric"] [data-testid="stMetricValue"] {
        color: var(--ink-strong) !important;
    }
    .stTabs [role="tab"], .stSegmentedControl label, .stSelectbox label, .stTextInput label {
        color: var(--ink-strong) !important;
    }
    .stDataFrame, .stTable {
        color: var(--ink-strong) !important;
    }
    .stCodeBlock, .stCode {
        background: #111111 !important;
        border: 1px solid rgba(255, 255, 255, 0.08) !important;
        border-radius: 18px !important;
    }
    .stCodeBlock pre, .stCode pre {
        color: #f4f7ff !important;
        background: #111111 !important;
    }
    .stCodeBlock code, .stCode code {
        color: #f4f7ff !important;
        text-shadow: none !important;
    }
    .stDataFrame [data-testid="stDataFrameResizable"],
    .stDataFrame [role="grid"],
    .stDataFrame [role="table"] {
        background: linear-gradient(180deg, #fffaf0 0%, #eef7ff 100%) !important;
        color: var(--ink-strong) !important;
    }
    .stDataFrame [role="columnheader"],
    .stDataFrame [role="rowheader"],
    .stDataFrame [role="gridcell"] {
        background: transparent !important;
        color: var(--ink-strong) !important;
        border-color: rgba(42, 75, 155, 0.12) !important;
    }
    .stDataFrame [role="columnheader"] {
        background: rgba(217, 59, 51, 0.08) !important;
        font-weight: 700 !important;
    }
    .stSegmentedControl [data-baseweb="button-group"] button,
    .stSegmentedControl [data-baseweb="button-group"] button *,
    .stSegmentedControl [data-baseweb="button-group"] button span,
    .stSegmentedControl [data-baseweb="button-group"] button div {
        color: #f4f7ff !important;
        fill: #f4f7ff !important;
        -webkit-text-fill-color: #f4f7ff !important;
        opacity: 1 !important;
    }
    .stSegmentedControl [data-baseweb="button-group"] button[aria-pressed="false"],
    .stSegmentedControl [data-baseweb="button-group"] button[aria-pressed="false"] *,
    .stSegmentedControl [data-baseweb="button-group"] button[aria-pressed="false"] span,
    .stSegmentedControl [data-baseweb="button-group"] button[aria-pressed="false"] div {
        color: #f4f7ff !important;
        fill: #f4f7ff !important;
        -webkit-text-fill-color: #f4f7ff !important;
        text-shadow: none !important;
        opacity: 1 !important;
    }
    .stSegmentedControl [data-baseweb="button-group"] {
        background: linear-gradient(180deg, #274b9f 0%, #1b2a52 100%) !important;
        border-radius: 14px !important;
        padding: 3px !important;
    }
    .stSegmentedControl [data-baseweb="button-group"] button[aria-pressed="true"],
    .stSegmentedControl [data-baseweb="button-group"] button[aria-pressed="true"] *,
    .stSegmentedControl [data-baseweb="button-group"] button[aria-pressed="true"] span,
    .stSegmentedControl [data-baseweb="button-group"] button[aria-pressed="true"] div {
        color: var(--ink-strong) !important;
        fill: var(--ink-strong) !important;
        -webkit-text-fill-color: var(--ink-strong) !important;
        background: linear-gradient(180deg, #fff7d6 0%, #ffe18b 100%) !important;
        opacity: 1 !important;
    }
    .stTextInput input,
    .stTextInput input *,
    .stTextInput [data-baseweb="input"] *,
    .stSelectbox div[data-baseweb="select"] > div,
    .stSelectbox div[data-baseweb="select"] span,
    .stSelectbox div[data-baseweb="select"] * ,
    .stSelectbox svg {
        color: #f4f7ff !important;
        fill: #f4f7ff !important;
        opacity: 1 !important;
    }
    .stTextInput [data-baseweb="input"],
    .stSelectbox div[data-baseweb="select"] > div {
        background: linear-gradient(180deg, #274b9f 0%, #1b2a52 100%) !important;
        border-color: rgba(255, 211, 77, 0.22) !important;
    }
    .stTextInput input::placeholder {
        color: rgba(244, 247, 255, 0.72) !important;
    }
    .stSelectbox div[data-baseweb="select"] input {
        -webkit-text-fill-color: #f4f7ff !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

if POKEMON_IMAGE.exists():
    st.sidebar.markdown("<div class='sidebar-pikachu'>", unsafe_allow_html=True)
    st.sidebar.image(str(POKEMON_IMAGE), width=160)
    st.sidebar.markdown("</div>", unsafe_allow_html=True)

st.sidebar.title("Trainer Controls")
st.sidebar.write("Catch a few more Pokemon and immediately watch the SQL views update.")

if "catch_results" not in st.session_state:
    st.session_state.catch_results = None

if st.sidebar.button("Catch 1 Pokemon", use_container_width=True):
    caught_now = refresh_collection(rounds=1)
    if caught_now:
        st.session_state.catch_results = {
            "title": "Catch Result",
            "message": format_catch_summary(caught_now),
        }
        st.sidebar.success(f"Caught {caught_now[0]['name'].title()}!")
    else:
        st.session_state.catch_results = {
            "title": "Catch Result",
            "message": "No Pokemon were caught. The API may be unavailable.",
        }
        st.sidebar.warning("No Pokemon was caught. The API may be unavailable.")
    st.cache_data.clear()
    st.rerun()

if st.sidebar.button("Catch 5 Pokemon", use_container_width=True):
    caught_batch = refresh_collection(rounds=5)
    if caught_batch:
        st.session_state.catch_results = {
            "title": "Catch Results",
            "message": format_catch_summary(caught_batch),
        }
        st.sidebar.success(f"Caught {len(caught_batch)} Pokemon and updated the CSV.")
    else:
        st.session_state.catch_results = {
            "title": "Catch Results",
            "message": "No Pokemon were caught. The API may be unavailable.",
        }
        st.sidebar.warning("No Pokemon were caught. The API may be unavailable.")
    st.cache_data.clear()
    st.rerun()

if st.sidebar.button("Refresh Pokedex Cache", use_container_width=True):
    try:
        fetch_and_cache_pokedex_data()
    except requests.RequestException:
        st.sidebar.error("Could not refresh the Pokedex cache right now.")
    else:
        st.sidebar.success("Pokedex cache refreshed.")
        st.rerun()

st.sidebar.markdown("Data source: `data/caught_pokemon.csv`")
st.sidebar.markdown("Analytics engine: `SQLite`")
st.sidebar.markdown("Pokedex cache: `data/pokedex_cache.csv`")

local_image_count = count_local_pokedex_images()
image_index = build_local_image_index(str(POKEDEX_IMAGE_DIR))
dataframe = load_pokemon_data()

st.markdown(
    """
    <div class="hero-card">
        <div class="hero-kicker">Python + SQL Portfolio Project</div>
        <div class="hero-title">Pokemon ETL Dashboard</div>
        <div class="hero-copy">
            A playful data project that fetches Pokemon with Python, stores them in CSV,
            explores them with SQLite, and includes a full Pokedex with artwork, evolution paths, and catch tracking.
        </div>
        <div class="code-chip">Extract -> Transform -> Load -> Query -> Visualize</div>
    </div>
    """,
    unsafe_allow_html=True,
)

if local_image_count == 0:
    st.warning(
        "Kaggle Pokedex images are not installed yet, so the app is using online artwork only. "
        "Run `python download_pokedex_assets.py` to populate `data/pokedex_images`."
    )

if dataframe.empty:
    st.warning("No Pokemon data found yet. Run the ETL game or use the sidebar buttons to catch some Pokemon.")
    st.stop()

if st.session_state.catch_results:
    catch_box = st.session_state.catch_results
    with st.container():
        st.markdown(
            "<div class='summary-console' style='margin-top:0.5rem;'>"
            f"<strong>{catch_box['title']}:</strong><br><pre style='margin:0.65rem 0 0 0;white-space:pre-wrap;"
            f"font-family:inherit;color:var(--ink);background:transparent;border:none;'>{catch_box['message']}</pre>"
            "</div>",
            unsafe_allow_html=True,
        )
    st.session_state.catch_results = None

connection = build_connection(dataframe)
type_counts = run_query(connection, TYPE_QUERY)
heaviest = run_query(connection, HEAVIEST_QUERY)
tallest = run_query(connection, TALLEST_QUERY)
duplicates = run_query(connection, DUPLICATE_QUERY)

metric_1, metric_2, metric_3, metric_4 = st.columns(4)
metric_1.metric("Total catches", int(len(dataframe)))
metric_2.metric("Unique Pokemon", int(dataframe["name"].nunique()))
metric_3.metric("Average weight", f"{dataframe['weight'].mean():.1f}")
metric_4.metric("Top type", type_counts.iloc[0]["type_name"].title() if not type_counts.empty else "Unknown")

page = st.segmented_control(
    "Dashboard View",
    options=["Pokedex Device", "Overview", "SQL Insights", "Raw Data"],
    default="Pokedex Device",
)

if page == "Pokedex Device":
    st.subheader("Kanto Pokedex")
    st.write("Search the original 151, inspect a single Pokemon, and see whether your ETL pipeline has already caught it.")

    try:
        pokedex_df = load_pokedex_data()
    except requests.RequestException:
        st.error("The Pokedex could not be loaded from PokéAPI right now. Try again when the API is available.")
    else:
        caught_ids = set(dataframe["id"].astype(int).tolist())
        caught_names = set(dataframe["name"].str.title())
        pokedex_df["caught"] = pokedex_df["id"].isin(caught_ids) | pokedex_df["name"].isin(caught_names)

        filter_col, type_col, select_col = st.columns([1.3, 1, 1.7], gap="large")
        with filter_col:
            search_term = st.text_input("Search by name", placeholder="Pikachu, Eevee, Charizard...")
        with type_col:
            available_types = sorted(
                {
                    type_name
                    for type_name in pd.concat([pokedex_df["type_1"], pokedex_df["type_2"]]).dropna().unique()
                    if type_name
                }
            )
            selected_type = st.selectbox("Type", options=["All"] + available_types)
        with select_col:
            dex_options = [f"#{int(row.id):03d} {row.name}" for row in pokedex_df.itertuples()]
            default_index = dex_options.index("#025 Pikachu") if "#025 Pikachu" in dex_options else 0
            selected_label = st.selectbox("Inspect Pokemon", options=dex_options, index=default_index)

        filtered_pokedex = pokedex_df.copy()
        if search_term:
            filtered_pokedex = filtered_pokedex[
                filtered_pokedex["name"].str.contains(search_term, case=False, na=False)
            ]
        if selected_type != "All":
            filtered_pokedex = filtered_pokedex[
                (filtered_pokedex["type_1"] == selected_type) | (filtered_pokedex["type_2"] == selected_type)
            ]

        selected_id = int(selected_label.split()[0].replace("#", ""))
        selected_pokemon = pokedex_df[pokedex_df["id"] == selected_id].iloc[0]
        local_image = find_local_pokemon_image(int(selected_pokemon["id"]), selected_pokemon["name"], image_index)
        image_source = local_image or selected_pokemon["sprite_url"]

        st.markdown(
            "<div class='summary-console'>"
            f"<strong>Console feed:</strong> {len(filtered_pokedex)} Pokemon match your filters. "
            f"{int(filtered_pokedex['caught'].sum()) if len(filtered_pokedex) else 0} already appear in your ETL dataset, "
            f"and the selected entry is <strong>{selected_pokemon['name']}</strong>."
            "</div>",
            unsafe_allow_html=True,
        )
        shell_col, side_col = st.columns([2.2, 1], gap="large")

        with shell_col:
            st.markdown("<div class='pokedex-shell'>", unsafe_allow_html=True)
            if POKEDEX_HEADER_IMAGE.exists():
                st.markdown(render_responsive_header_image(POKEDEX_HEADER_IMAGE), unsafe_allow_html=True)
            st.markdown("<div class='pokedex-screen'>", unsafe_allow_html=True)
            st.markdown(
                "<div class='device-meta'>"
                f"<div class='device-meta-text'>Artwork source: {'Local Kaggle image' if local_image else 'Online PokéAPI fallback'}</div>"
                "<div class='device-meta-pill'>Kanto Scanner</div>"
                "</div>",
                unsafe_allow_html=True,
            )
            top_left, top_right = st.columns([1.05, 1.2], gap="large")

            with top_left:
                st.markdown("<div class='screen-label'>Visual Scanner</div>", unsafe_allow_html=True)
                st.image(image_source, use_container_width=True)
                st.markdown("<div class='screen-divider'></div>", unsafe_allow_html=True)
                st.markdown(
                    f"<div class='status-strip'><span class='status-dot'></span>ARTWORK {'LOCAL' if local_image else 'ONLINE'}</div>",
                    unsafe_allow_html=True,
                )

            with top_right:
                st.markdown("<div class='dex-pill'>Live Pokedex Entry</div>", unsafe_allow_html=True)
                st.markdown(
                    f"<div class='dex-title'>#{int(selected_pokemon['id']):03d} {selected_pokemon['name']}</div>",
                    unsafe_allow_html=True,
                )
                st.markdown(render_type_badges([selected_pokemon["type_1"], selected_pokemon["type_2"]]), unsafe_allow_html=True)
                st.markdown(f"<div class='dex-copy'>{selected_pokemon['flavor_text']}</div>", unsafe_allow_html=True)
                status_class = "caught-badge" if bool(selected_pokemon["caught"]) else "missing-badge"
                status_text = "Caught in your CSV dataset" if bool(selected_pokemon["caught"]) else "Not caught yet"
                st.markdown(f"<div class='{status_class}'>{status_text}</div>", unsafe_allow_html=True)
                st.markdown(
                    f"<div class='status-strip'><span class='status-dot {'offline' if not bool(selected_pokemon['caught']) else ''}'></span>"
                    f"TRAINER LOG {'SYNCED' if bool(selected_pokemon['caught']) else 'WAITING FOR CAPTURE'}</div>",
                    unsafe_allow_html=True,
                )
                st.markdown("<div style='margin-top:1rem;'>" + render_stat_bars(selected_pokemon) + "</div>", unsafe_allow_html=True)

            info_a, info_b, info_c = st.columns(3, gap="medium")
            with info_a:
                st.markdown(
                    "<div class='mini-card'><div class='mini-label'>Measurements</div>"
                    f"<div class='mini-value'>Height {selected_pokemon['height']} | Weight {selected_pokemon['weight']}</div></div>",
                    unsafe_allow_html=True,
                )
            with info_b:
                st.markdown(
                    "<div class='mini-card'><div class='mini-label'>Abilities</div>"
                    f"<div class='mini-value'>{selected_pokemon['abilities']}</div></div>",
                    unsafe_allow_html=True,
                )
            with info_c:
                st.markdown(
                    "<div class='mini-card'><div class='mini-label'>World Data</div>"
                    f"<div class='mini-value'>{selected_pokemon['color']} | {selected_pokemon['habitat']}</div></div>",
                    unsafe_allow_html=True,
                )

            st.markdown(
                "<div class='mini-card'><div class='mini-label'>Evolution Chain</div>"
                f"<div class='mini-value'>{selected_pokemon['evolution_chain']}</div></div>",
                unsafe_allow_html=True,
            )
            st.markdown("</div>", unsafe_allow_html=True)
            st.markdown(render_pokedex_buttons(), unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)

        with side_col:
            st.markdown("### Trainer Progress")
            st.metric("Caught in Pokedex", int(pokedex_df["caught"].sum()))
            st.metric("Still missing", int((~pokedex_df["caught"]).sum()))
            st.metric("Completion", f"{(pokedex_df['caught'].mean() * 100):.1f}%")

            st.markdown("### Matching Pokemon")
            preview_df = filtered_pokedex[["id", "name", "type_1", "type_2", "caught"]].copy()
            preview_df["status"] = preview_df["caught"].map({True: "Caught", False: "Missing"})
            preview_df["dex_no"] = preview_df["id"].map(lambda value: f"#{int(value):03d}")
            st.dataframe(
                preview_df[["dex_no", "name", "type_1", "type_2", "status"]],
                use_container_width=True,
                hide_index=True,
                height=480,
            )

elif page == "Overview":
    st.markdown(
        """
        <div class="overview-note">
            <div class="overview-note-title">Overview Mode</div>
            <div class="overview-note-copy">
                This lighter view skips the heavy Pokédex loading path unless you actually open <code>Pokedex Device</code>.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    type_counts_sorted = type_counts.sort_values(["catches", "type_name"], ascending=[False, True]).copy()
    type_chart = (
        alt.Chart(type_counts_sorted)
        .mark_bar(cornerRadiusEnd=8, color="#ffbd12")
        .encode(
            y=alt.Y(
                "type_name:N",
                sort="-x",
                title=None,
                axis=alt.Axis(labelColor="#24324d", labelPadding=8),
            ),
            x=alt.X(
                "catches:Q",
                title="Number of catches",
                axis=alt.Axis(labelColor="#24324d", titleColor="#24324d", gridColor="rgba(36,50,77,0.10)"),
            ),
            tooltip=["type_name", "catches"],
        )
        .properties(height=320)
    )
    type_labels = (
        alt.Chart(type_counts_sorted)
        .mark_text(align="left", dx=8, color="#24324d", fontSize=12, fontWeight="bold")
        .encode(
            y=alt.Y("type_name:N", sort="-x"),
            x=alt.X("catches:Q"),
            text=alt.Text("catches:Q"),
        )
    )
    st.markdown("<div class='chart-card'>", unsafe_allow_html=True)
    st.markdown("<div class='chart-card-title'>Caught Pokemon by Type</div>", unsafe_allow_html=True)
    st.markdown("<div class='chart-card-copy'>Most common types in your current caught dataset.</div>", unsafe_allow_html=True)
    st.altair_chart(
        (type_chart + type_labels).configure_view(strokeOpacity=0).configure(background="transparent"),
        use_container_width=True,
    )
    st.markdown("</div>", unsafe_allow_html=True)

    compact_a, compact_b = st.columns(2, gap="medium")

    heaviest_chart = (
        alt.Chart(heaviest)
        .mark_bar(cornerRadiusEnd=8, color="#d93b33")
        .encode(
            y=alt.Y("name:N", sort="-x", title=None, axis=alt.Axis(labelColor="#24324d", labelPadding=8)),
            x=alt.X("weight:Q", title="Weight", axis=alt.Axis(labelColor="#24324d", titleColor="#24324d", gridColor="rgba(36,50,77,0.10)")),
            tooltip=["name", "weight", "height", "types"],
        )
        .properties(height=240)
    )
    heaviest_labels = (
        alt.Chart(heaviest)
        .mark_text(align="left", dx=8, color="#24324d", fontSize=12, fontWeight="bold")
        .encode(y=alt.Y("name:N", sort="-x"), x=alt.X("weight:Q"), text=alt.Text("weight:Q"))
    )

    tallest_chart = (
        alt.Chart(tallest)
        .mark_bar(cornerRadiusEnd=8, color="#5dade2")
        .encode(
            y=alt.Y("name:N", sort="-x", title=None, axis=alt.Axis(labelColor="#24324d", labelPadding=8)),
            x=alt.X("height:Q", title="Height", axis=alt.Axis(labelColor="#24324d", titleColor="#24324d", gridColor="rgba(36,50,77,0.10)")),
            tooltip=["name", "height", "weight", "types"],
        )
        .properties(height=240)
    )
    tallest_labels = (
        alt.Chart(tallest)
        .mark_text(align="left", dx=8, color="#24324d", fontSize=12, fontWeight="bold")
        .encode(y=alt.Y("name:N", sort="-x"), x=alt.X("height:Q"), text=alt.Text("height:Q"))
    )

    with compact_a:
        st.markdown("<div class='chart-card'>", unsafe_allow_html=True)
        st.markdown("<div class='chart-card-title'>Heaviest Pokemon</div>", unsafe_allow_html=True)
        st.markdown("<div class='chart-card-copy'>Top catches by recorded weight.</div>", unsafe_allow_html=True)
        st.altair_chart(
            (heaviest_chart + heaviest_labels).configure_view(strokeOpacity=0).configure(background="transparent"),
            use_container_width=True,
        )
        st.markdown("</div>", unsafe_allow_html=True)
    with compact_b:
        st.markdown("<div class='chart-card'>", unsafe_allow_html=True)
        st.markdown("<div class='chart-card-title'>Tallest Pokemon</div>", unsafe_allow_html=True)
        st.markdown("<div class='chart-card-copy'>Top catches by recorded height.</div>", unsafe_allow_html=True)
        st.altair_chart(
            (tallest_chart + tallest_labels).configure_view(strokeOpacity=0).configure(background="transparent"),
            use_container_width=True,
        )
        st.markdown("</div>", unsafe_allow_html=True)

elif page == "SQL Insights":
    st.subheader("SQLite Query Examples")
    st.code(TYPE_QUERY.strip(), language="sql")
    st.dataframe(type_counts, use_container_width=True, hide_index=True)

    st.code(HEAVIEST_QUERY.strip(), language="sql")
    st.dataframe(heaviest, use_container_width=True, hide_index=True)

    st.code(DUPLICATE_QUERY.strip(), language="sql")
    if duplicates.empty:
        st.info("No duplicate catches yet. Every Pokemon in the CSV is unique so far.")
    else:
        st.dataframe(duplicates, use_container_width=True, hide_index=True)

else:
    st.subheader("Collected Pokemon")
    st.write("A visual gallery of the Pokemon currently stored in your caught dataset.")

    try:
        pokedex_df = load_pokedex_data()
    except requests.RequestException:
        st.info("Could not load Pokédex artwork for the gallery right now.")
    else:
        caught_gallery = (
            dataframe[["id", "name", "types", "height"]]
            .drop_duplicates(subset=["id", "name"])
            .sort_values(["id", "name"])
            .copy()
        )
        caught_gallery["name"] = caught_gallery["name"].str.title()
        gallery_with_art = caught_gallery.merge(
            pokedex_df[["id", "name", "sprite_url"]],
            on=["id", "name"],
            how="left",
        )

        for row_start in range(0, len(gallery_with_art), 5):
            row = gallery_with_art.iloc[row_start : row_start + 5]
            columns = st.columns(5, gap="medium")

            for column, (_, pokemon) in zip(columns, row.iterrows()):
                with column:
                    local_image = find_local_pokemon_image(int(pokemon["id"]), pokemon["name"], image_index)
                    image_source = local_image or pokemon["sprite_url"]

                    st.markdown("<div class='caught-gallery-card'>", unsafe_allow_html=True)
                    if image_source:
                        st.image(image_source, width=160)
                    st.markdown(
                        f"<div class='caught-gallery-name'>#{int(pokemon['id']):03d} {pokemon['name']}</div>",
                        unsafe_allow_html=True,
                    )
                    st.markdown(
                        f"<div class='caught-gallery-meta'>{str(pokemon['types']).title()}</div>",
                        unsafe_allow_html=True,
                    )
                    st.markdown(
                        f"<div class='caught-gallery-stat'>Height: {int(pokemon['height'])}</div>",
                        unsafe_allow_html=True,
                    )
                    st.markdown("</div>", unsafe_allow_html=True)
