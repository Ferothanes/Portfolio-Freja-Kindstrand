import csv
import random
import time
from pathlib import Path

import requests

POKEMON_API_URL = "https://pokeapi.co/api/v2/pokemon/"
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
CSV_PATH = DATA_DIR / "caught_pokemon.csv"
FIELDNAMES = ["id", "name", "height", "weight", "types"]


def get_random_pokemon():
    pokemon_id = random.randint(1, 151)
    response = requests.get(f"{POKEMON_API_URL}{pokemon_id}", timeout=10)
    response.raise_for_status()
    data = response.json()
    return {
        "id": data["id"],
        "name": data["name"],
        "height": data["height"],
        "weight": data["weight"],
        "types": ", ".join(type_info["type"]["name"] for type_info in data["types"]),
    }


def write_to_csv(pokemon_data, filename=CSV_PATH):
    DATA_DIR.mkdir(exist_ok=True)
    file_exists = Path(filename).exists()

    with open(filename, "a", newline="", encoding="utf-8") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=FIELDNAMES)
        if not file_exists:
            writer.writeheader()
        writer.writerow(pokemon_data)


def catch_pokemon(rounds=5, delay=1.5):
    caught_pokemon = []

    for _ in range(rounds):
        try:
            pokemon = get_random_pokemon()
            write_to_csv(pokemon)
            caught_pokemon.append(pokemon)
        except requests.RequestException:
            continue

        if delay:
            time.sleep(delay)

    return caught_pokemon


def play_game(rounds=5):
    print("Welcome to the Pokemon ETL Game!")

    caught_pokemon = catch_pokemon(rounds=rounds)

    for pokemon in caught_pokemon:
        print(f"Caught {pokemon['name'].capitalize()}!")

    if len(caught_pokemon) < rounds:
        print("Some Pokemon escaped because the API could not be reached.")

    print(f"All caught Pokemon saved to '{CSV_PATH.name}'!")


if __name__ == "__main__":
    play_game()
