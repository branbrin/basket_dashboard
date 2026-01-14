import os
import sys
import zipfile
import subprocess
from pathlib import Path


def run(cmd: list[str]) -> None:
    """Run a command and raise a nice error if it fails."""
    print(">", " ".join(cmd))
    p = subprocess.run(cmd, capture_output=True, text=True)
    if p.returncode != 0:
        print(p.stdout)
        print(p.stderr, file=sys.stderr)
        raise RuntimeError(f"Command failed with exit code {p.returncode}")


def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def list_files(root: Path) -> list[Path]:
    if not root.exists():
        return []
    return sorted([p for p in root.rglob("*") if p.is_file()])


def unzip_all(zip_path: Path, out_dir: Path) -> None:
    with zipfile.ZipFile(zip_path, "r") as zf:
        zf.extractall(out_dir)


def main():
    # --- CONFIG ---
    # Usage:
    #   python scripts/download_kaggle_dataset.py viniciusrabello/nba-past-drafts-ncaa-stats data_raw/ncaa
    slug = sys.argv[1] if len(sys.argv) > 1 else "viniciusrabello/nba-past-drafts-ncaa-stats"
    out_dir = Path(sys.argv[2]) if len(sys.argv) > 2 else Path("data_raw/ncaa")

    ensure_dir(out_dir)

    # We store the zip in a temp folder inside out_dir to keep things tidy
    tmp_dir = out_dir / "_tmp"
    ensure_dir(tmp_dir)
    zip_path = tmp_dir / f"{slug.replace('/', '__')}.zip"

    print(f"Dataset slug: {slug}")
    print(f"Output dir:   {out_dir.resolve()}")

    # --- Sanity checks ---
    # 1) Kaggle CLI installed?
    try:
        run(["kaggle", "--version"])
    except Exception as e:
        raise RuntimeError(
            "No encuentro el comando 'kaggle'.\n"
            "Instálalo en tu venv:  pip install kaggle\n"
            "Y asegúrate de que el venv está activo cuando lo ejecutes."
        ) from e

    # 2) Kaggle credentials exist?
    kaggle_json = Path.home() / ".kaggle" / "kaggle.json"
    if not kaggle_json.exists():
        raise RuntimeError(
            "No encuentro tus credenciales de Kaggle en:\n"
            f"  {kaggle_json}\n\n"
            "Solución rápida:\n"
            "1) En Kaggle -> Account -> Create New Token\n"
            "2) Copia kaggle.json a C:\\Users\\TU_USUARIO\\.kaggle\\kaggle.json\n"
            "3) Vuelve a ejecutar el script"
        )

    before = set(map(str, list_files(out_dir)))

    # --- Download ---
    # -p sets output folder, -f sets file name, --force overwrites
    run([
        "kaggle", "datasets", "download",
        "-d", slug,
        "-p", str(tmp_dir),
        "-f", zip_path.name,
        "--force"
    ])

    if not zip_path.exists():
        raise RuntimeError(f"Descarga completada pero no veo el zip aquí: {zip_path}")

    # --- Extract ---
    unzip_all(zip_path, out_dir)

    after = set(map(str, list_files(out_dir)))
    new_files = sorted(list(after - before))

    print("\n✅ Descarga y extracción completadas.")
    print("📄 Archivos nuevos detectados:")
    if not new_files:
        print("  (No detecté archivos nuevos; quizás ya existían o el dataset no trae ficheros adicionales.)")
    else:
        for f in new_files:
            # Show paths relative to repo
            try:
                rel = str(Path(f).resolve().relative_to(Path.cwd().resolve()))
            except Exception:
                rel = f
            print("  -", rel)

    print("\nℹ️ Nota: dejo el zip en:", zip_path)
    print("   (Puedes borrarlo cuando quieras.)")


if __name__ == "__main__":
    main()
