import subprocess
from pathlib import Path

def main():
    project_root = Path(__file__).resolve().parent.parent
    out_dir = project_root / "data_raw" / "kaggle" / "sumitrodatta"
    out_dir.mkdir(parents=True, exist_ok=True)

    slug = "sumitrodatta/nba-aba-baa-stats"

    print(f"Downloading dataset: {slug}")
    subprocess.check_call([
        "kaggle", "datasets", "download",
        "-d", slug,
        "-p", str(out_dir),
        "--unzip"
    ])

    print("Download complete.")
    print(f"Files saved in: {out_dir}")

if __name__ == "__main__":
    main()
