import requests
import csv
import random
import time
from pathlib import Path

POKEMON_API_URL = "https://pokeapi.co/api/v2/pokemon/"
FIELDNAMES = ["id", "name", "height", "weight", "types"]  # ✅ Reused in CSV writing

def get_random_pokemon():
    pokemon_id = random.randint(1, 151)  # First gen nostalgia!
    response = requests.get(f"{POKEMON_API_URL}{pokemon_id}")
    if response.status_code == 200:
        data = response.json()
        return {
            "id": data["id"],
            "name": data["name"],
            "height": data["height"],
            "weight": data["weight"],
            "types": ", ".join(t['type']['name'] for t in data['types'])
        }
    else:
        return None

DATA_DIR = Path("Python_&_SQL\data")
DATA_DIR.mkdir(exist_ok=True)  # Makes sure the folder exists

def write_to_csv(pokemon_data, filename=DATA_DIR / "caught_pokemon.csv"):
    file_exists = Path(filename).exists()
    with open(filename, "a", newline="") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=FIELDNAMES)
        if not file_exists:
            writer.writeheader()
        writer.writerow(pokemon_data)

def play_game(rounds=5):
    print("🎮 Welcome to the Pokémon ETL Game!")
    for i in range(rounds):
        print(f"\n🔍 Searching for Pokémon #{i + 1}...")
        pokemon = get_random_pokemon()
        if pokemon:
            print(f"✅ Caught {pokemon['name'].capitalize()}!")
            write_to_csv(pokemon)
        else:
            print("❌ Failed to catch Pokémon.")
        time.sleep(1.5)
    print("\n📦 All caught Pokémon saved to 'caught_pokemon.csv'!")

if __name__ == "__main__":
    play_game()
