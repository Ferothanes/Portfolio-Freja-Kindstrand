from pathlib import Path
import shutil

try:
    import kagglehub
except ModuleNotFoundError as exc:
    raise SystemExit(
        "Missing dependency: kagglehub.\n"
        "Install project dependencies with `python -m pip install -r requirements.txt`.\n"
        "If that still fails, try `python -m pip install kagglehub --index-url https://pypi.org/simple`.\n"
        "After install, rerun `python download_pokedex_assets.py`."
    ) from exc


DATASET_NAME = "arenagrenade/the-complete-pokemon-images-data-set"
BASE_DIR = Path(__file__).resolve().parent
TARGET_DIR = BASE_DIR / "data" / "pokedex_images"


def main():
    dataset_path = Path(kagglehub.dataset_download(DATASET_NAME))
    TARGET_DIR.mkdir(parents=True, exist_ok=True)

    copied_files = 0
    for file_path in dataset_path.rglob("*"):
        if file_path.suffix.lower() not in {".png", ".jpg", ".jpeg", ".webp"}:
            continue
        destination = TARGET_DIR / file_path.name
        shutil.copy2(file_path, destination)
        copied_files += 1

    print(f"Copied {copied_files} image files into {TARGET_DIR}")


if __name__ == "__main__":
    main()
