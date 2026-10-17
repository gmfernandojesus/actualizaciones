"""Comprueba que los avisos de actualización llevan a cada cliente a SU
programa. Lo ejecuta GitHub solo en cada publicación y cada mañana; si algo
falla, GitHub manda un correo. También se puede lanzar a mano:

    python comprobar_avisos.py

Existe porque el 2026-10-17 los avisos apuntaban a `releases/latest`, que
es la última Release de cualquier programa: al salir el Chassis 5.3, los
clientes de Workshop Tool que pulsaban Descargar acababan en el Chassis.
"""

import base64
import json
import sys
import urllib.request
from pathlib import Path

REPO = "https://github.com/gmfernandojesus/actualizaciones"
DESCARGAS = f"{REPO}/releases/download/"

# Cada aviso y el único instalador al que puede llevar. Para añadir un
# programa nuevo, añadirlo aquí: un aviso que no esté en la lista falla.
PROGRAMAS = {
    "workshop-tool.json": "Workshop.Tool.-.Instalador.exe",
    "chassis-program.json": "Chassis.Program.-.Instalador.exe",
}

# Workshop Tool 3.0 lleva grabada otra dirección y no se puede cambiar:
# este puente tiene que decir siempre lo mismo que workshop-tool.json.
PUENTES = {
    "https://raw.githubusercontent.com/gmfernandojesus/taller-toro35/main/version.json":
        "workshop-tool.json",
}

MINIMO_BYTES = 1_000_000
CARPETA = Path(__file__).resolve().parent
errores = []


def fallo(texto):
    errores.append(texto)
    print(f"  ERROR: {texto}")


def tamano_descarga(url):
    """Tamaño del archivo que se descarga, o None si no se puede bajar."""
    peticion = urllib.request.Request(url, headers={"Range": "bytes=0-0"})
    try:
        with urllib.request.urlopen(peticion, timeout=30) as r:
            rango = r.headers.get("Content-Range", "")
            if "/" in rango:
                return int(rango.rsplit("/", 1)[1])
            return int(r.headers.get("Content-Length") or 0)
    except Exception as e:
        print(f"    (no se pudo descargar: {e})")
        return None


def comprobar_aviso(nombre, instalador):
    print(f"\n{nombre}")
    try:
        datos = json.loads((CARPETA / nombre).read_text(encoding="utf-8"))
    except (OSError, ValueError) as e:
        fallo(f"{nombre} no se puede leer: {e}")
        return None

    for campo in ("version", "fecha", "notas", "url"):
        if not str(datos.get(campo, "")).strip():
            fallo(f"{nombre}: falta el campo '{campo}'")
    url = str(datos.get("url", ""))

    if "latest" in url:
        fallo(f"{nombre}: el enlace usa 'latest'. Esa es la última Release de "
              f"CUALQUIER programa; tiene que apuntar al instalador de este: "
              f"{DESCARGAS}<tag>/{instalador}")
    elif not url.startswith(DESCARGAS):
        fallo(f"{nombre}: el enlace no es una descarga de este repositorio: {url}")
    elif url.rsplit("/", 1)[-1] != instalador:
        fallo(f"{nombre}: el enlace descarga '{url.rsplit('/', 1)[-1]}', "
              f"y tendría que descargar '{instalador}'")
    else:
        tamano = tamano_descarga(url)
        if tamano is None:
            fallo(f"{nombre}: el instalador no existe o no se puede descargar "
                  f"(¿se borró la Release o el archivo?): {url}")
        elif tamano < MINIMO_BYTES:
            fallo(f"{nombre}: el instalador pesa {tamano} bytes, demasiado poco")
        else:
            print(f"  OK  versión {datos['version']} -> {instalador} "
                  f"({tamano / 1048576:.1f} MB)")
    return datos


def comprobar_puente(url_puente, nombre):
    print(f"\nPuente de Workshop Tool 3.0 ({url_puente.split('/')[4]})")
    original = json.loads((CARPETA / nombre).read_text(encoding="utf-8"))
    try:
        with urllib.request.urlopen(url_puente, timeout=30) as r:
            puente = json.loads(r.read().decode("utf-8"))
    except Exception as e:
        fallo(f"el puente para la 3.0 no responde ({e}): esos clientes no verán "
              f"ninguna actualización")
        return
    for campo in ("version", "url"):
        if puente.get(campo) != original.get(campo):
            fallo(f"el puente para la 3.0 dice {campo}={puente.get(campo)!r} y "
                  f"{nombre} dice {original.get(campo)!r}: hay que copiar "
                  f"{nombre} encima de version.json en el repo taller-toro35")
    if not [e for e in errores if "puente" in e]:
        print(f"  OK  igual que {nombre}")


def comprobar_revisiones():
    """Si este archivo desaparece, en 30 días todos los clientes con
    licencias a distancia se quedan en solo lectura."""
    print("\nrevisiones-licencias.txt")
    archivo = CARPETA / "revisiones-licencias.txt"
    if not archivo.exists():
        fallo("FALTA revisiones-licencias.txt. Sin él, en 30 días todos los "
              "clientes pasan a solo lectura. Vuelve a publicarlo desde el "
              "Administrador de licencias.")
        return
    texto = "".join(archivo.read_text(encoding="utf-8").split())
    try:
        cuerpo = texto.rsplit(".", 1)[0]
        datos = json.loads(base64.urlsafe_b64decode(cuerpo + "=" * (-len(cuerpo) % 4)))
        assert datos.get("tipo") == "revisiones" and isinstance(datos.get("version"), int)
    except Exception:
        fallo("revisiones-licencias.txt está estropeado. Vuelve a publicarlo "
              "desde el Administrador de licencias.")
        return
    print(f"  OK  lista de revisiones versión {datos['version']}")


def main():
    for archivo in sorted(CARPETA.glob("*.json")):
        if archivo.name not in PROGRAMAS:
            fallo(f"{archivo.name} no está en PROGRAMAS de comprobar_avisos.py: "
                  f"añade qué instalador le corresponde")
    for nombre, instalador in PROGRAMAS.items():
        comprobar_aviso(nombre, instalador)
    for url_puente, nombre in PUENTES.items():
        comprobar_puente(url_puente, nombre)
    comprobar_revisiones()

    print()
    if errores:
        print(f"HAY {len(errores)} PROBLEMA(S): algún cliente no puede actualizar bien.")
        sys.exit(1)
    print("Todo bien: cada cliente descarga su programa.")


if __name__ == "__main__":
    main()
