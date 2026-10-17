"""Publica una versión nueva de un programa para que se actualice sola en
todos los clientes. Uso (con el python del venv, que tiene `cryptography`):

    python publicar.py "Workshop Tool" 3.4 "ruta\\Workshop Tool - Instalador.exe" "Notas para el taller"

Hace, en este orden:
  1. Calcula tamaño y huella SHA-256 del instalador.
  2. Crea la Release `<programa>-<version>` con el instalador (una Release por
     programa: nada de mezclar programas ni de depender de "latest").
  3. Firma el aviso con la clave privada del Administrador de licencias: el
     programa instalado solo se actualiza con avisos firmados para él.
  4. Workshop Tool: publica primero el puente para las instalaciones 3.0.
  5. Escribe `<programa>.json` y lo sube (el hook pre-push lo comprueba todo
     antes de dejarlo salir).

La clave privada nunca sale de `Desktop\\IA\\Administrador de licencias\\`.
"""

import base64
import hashlib
import json
import subprocess
import sys
from datetime import date
from pathlib import Path

from cryptography.hazmat.primitives import serialization

REPO = "gmfernandojesus/actualizaciones"
DESCARGAS = f"https://github.com/{REPO}/releases/download/"
CARPETA = Path(__file__).resolve().parent
CLAVE_PRIVADA = Path.home() / "Desktop" / "IA" / "Administrador de licencias" / "clave_privada.pem"
# Workshop Tool 3.0 lee de otra dirección grabada en su .exe.
PUENTES = {"Workshop Tool": CARPETA.parent / "puente-30" / "version.json"}


def texto_firmado(producto, datos):
    """Idéntico a actualizador.texto_firmado en los programas."""
    return json.dumps(
        {
            "tipo": "actualizacion",
            "producto": producto,
            "version": str(datos.get("version", "")),
            "url": str(datos.get("url", "")),
            "sha256": str(datos.get("sha256", "")).lower(),
            "tamano": int(datos.get("tamano") or 0),
        },
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode("utf-8")


def ejecutar(*orden, cwd=CARPETA):
    print("  $", " ".join(orden))
    subprocess.run(orden, cwd=cwd, check=True)


def main():
    if len(sys.argv) != 5:
        raise SystemExit(__doc__)
    programa, version, instalador, notas = sys.argv[1:]
    instalador = Path(instalador)
    slug = programa.lower().replace(" ", "-")
    tag = f"{slug}-{version}"
    nombre_en_github = f"{programa} - Instalador.exe".replace(" ", ".")

    datos_bin = instalador.read_bytes()
    datos = {
        "producto": programa,
        "version": version,
        "fecha": date.today().isoformat(),
        "notas": notas,
        "url": f"{DESCARGAS}{tag}/{nombre_en_github}",
        "sha256": hashlib.sha256(datos_bin).hexdigest(),
        "tamano": len(datos_bin),
    }
    clave = serialization.load_pem_private_key(CLAVE_PRIVADA.read_bytes(), password=None)
    datos["firma"] = base64.urlsafe_b64encode(
        clave.sign(texto_firmado(programa, datos))).decode().rstrip("=")
    print(f"{programa} {version}: {datos['tamano']} bytes, sha256 {datos['sha256'][:16]}…")

    print("\n1) Release con el instalador")
    ejecutar("gh", "release", "create", tag, "--repo", REPO,
             "--title", f"{programa} {version}", "--notes", notas, str(instalador))

    texto = json.dumps(datos, ensure_ascii=False, indent=2) + "\n"
    autor = ["-c", "user.name=gmfernandojesus", "-c", "user.email=gm.fernandojesus@gmail.com"]
    mensaje = f"{programa} {version}\n\nCo-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
    if programa in PUENTES:
        print("\n2) Puente para las instalaciones antiguas")
        puente = PUENTES[programa]
        ejecutar("git", "pull", "-q", "--ff-only", cwd=puente.parent)
        puente.write_text(texto, encoding="utf-8")
        ejecutar("git", "add", puente.name, cwd=puente.parent)
        ejecutar("git", *autor, "commit", "-q", "-m", mensaje, cwd=puente.parent)
        ejecutar("git", "push", "-q", "origin", "main", cwd=puente.parent)

    print("\n3) Aviso de versión (pasa por la comprobación antes de subirse)")
    ejecutar("git", "pull", "-q", "--ff-only")
    (CARPETA / f"{slug}.json").write_text(texto, encoding="utf-8")
    ejecutar("git", "add", f"{slug}.json")
    ejecutar("git", *autor, "commit", "-q", "-m", mensaje)
    ejecutar("git", "push", "origin", "main")
    print(f"\nPublicado: {programa} {version} se instalará solo en todos los clientes.")


if __name__ == "__main__":
    main()
