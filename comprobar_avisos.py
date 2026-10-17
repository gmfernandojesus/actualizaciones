"""Comprueba que los avisos de actualización llevan a cada cliente a SU
programa y a ningún otro.

Se ejecuta solo:
  - antes de cada `git push` desde este ordenador (si falla, no se sube nada),
  - en GitHub en cada publicación, en cada Release y cada mañana (si falla,
    GitHub manda un correo).
A mano: `python comprobar_avisos.py`

No hay ninguna lista de programas que mantener: cada `<programa>.json` debe
descargar `<Programa>.-.Instalador.exe`, y eso se deduce del nombre del
archivo. Es la misma regla con la que los propios programas (Workshop Tool
3.3+, Chassis Program 5.4+) se niegan a ofrecer un instalador que no sea el
suyo.

Existe porque el 2026-10-17 los avisos apuntaban a `releases/latest`, que es
la última Release de cualquier programa: al salir el Chassis 5.3, los
clientes de Workshop Tool que pulsaban Descargar acababan en el Chassis.
"""

import base64
import hashlib
import json
import re
import sys
import urllib.parse
import urllib.request
from pathlib import Path

CLAVE_PUBLICA_HEX = "b77a51734fcbd21f490ca354b8831cf3406400c6f374bf895bade3d8a252d98e"
REPO = "https://github.com/gmfernandojesus/actualizaciones"
DESCARGAS = f"{REPO}/releases/download/"

# Workshop Tool 3.0 lleva grabada otra dirección que no se puede cambiar: ese
# puente tiene que decir siempre lo mismo que workshop-tool.json. Se lee por
# la API y no por raw.githubusercontent, que tarda unos minutos en enterarse
# de los cambios y daría falsas alarmas justo después de publicar.
PUENTES = {
    "taller-toro35/version.json": "workshop-tool.json",
}

MINIMO_BYTES = 1_000_000
CARPETA = Path(__file__).resolve().parent
errores = []


def fallo(texto):
    errores.append(texto)
    print(f"  ERROR: {texto}")


def solo_letras(texto):
    return re.sub(r"[^a-z0-9]", "", texto.lower())


def instalador_esperado(aviso):
    """workshop-tool.json -> Workshop.Tool.-.Instalador.exe"""
    palabras = aviso.stem.replace("_", "-").split("-")
    return ".".join(p.capitalize() for p in palabras) + ".-.Instalador.exe"


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


def firma_valida(producto, datos):
    from cryptography.exceptions import InvalidSignature
    from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey

    firma = str(datos.get("firma", ""))
    try:
        Ed25519PublicKey.from_public_bytes(bytes.fromhex(CLAVE_PUBLICA_HEX)).verify(
            base64.urlsafe_b64decode(firma + "=" * (-len(firma) % 4)),
            texto_firmado(producto, datos),
        )
        return True
    except (InvalidSignature, ValueError, TypeError):
        return False


def descargar_y_medir(url):
    """(tamaño, sha256) de lo que se descarga de verdad, o None."""
    h = hashlib.sha256()
    total = 0
    try:
        with urllib.request.urlopen(url, timeout=120) as r:
            for bloque in iter(lambda: r.read(1 << 20), b""):
                h.update(bloque)
                total += len(bloque)
    except Exception as e:
        print(f"    (no se pudo descargar: {e})")
        return None
    return total, h.hexdigest()


def comprobar_aviso(aviso):
    print(f"\n{aviso.name}")
    instalador = instalador_esperado(aviso)
    try:
        datos = json.loads(aviso.read_text(encoding="utf-8"))
    except (OSError, ValueError) as e:
        fallo(f"{aviso.name} no se puede leer: {e}")
        return

    for campo in ("version", "fecha", "notas", "url"):
        if not str(datos.get(campo, "")).strip():
            fallo(f"{aviso.name}: falta el campo '{campo}'")
    url = str(datos.get("url", ""))
    archivo = urllib.parse.unquote(url.split("?", 1)[0].rsplit("/", 1)[-1])

    if "latest" in url:
        fallo(f"{aviso.name}: el enlace usa 'latest'. Esa es la última Release "
              f"de CUALQUIER programa; tiene que apuntar al instalador de este: "
              f"{DESCARGAS}<tag>/{instalador}")
    elif not url.startswith(DESCARGAS):
        fallo(f"{aviso.name}: el enlace no es una descarga de este repositorio: {url}")
    elif solo_letras(archivo) != solo_letras(instalador):
        fallo(f"{aviso.name}: el enlace descarga '{archivo}', que es OTRO "
              f"programa. Tiene que descargar '{instalador}'")
    else:
        producto = str(datos.get("producto", ""))
        if solo_letras(producto) != solo_letras(aviso.stem):
            fallo(f"{aviso.name}: el campo 'producto' dice {producto!r}, que no es "
                  f"este programa. Publica con publicar.py")
            return
        if not firma_valida(producto, datos):
            fallo(f"{aviso.name}: el aviso no está firmado o la firma no vale. Los "
                  f"programas no se actualizarán solos. Publica con publicar.py")
            return
        medido = descargar_y_medir(url)
        if medido is None:
            fallo(f"{aviso.name}: el instalador no existe o no se puede descargar "
                  f"(¿se borró la Release o el archivo?): {url}")
        elif medido[0] < MINIMO_BYTES:
            fallo(f"{aviso.name}: el instalador pesa {medido[0]} bytes, demasiado poco")
        elif medido != (int(datos.get("tamano") or 0), str(datos.get("sha256", "")).lower()):
            fallo(f"{aviso.name}: el instalador publicado no es el que se firmó "
                  f"(tamaño o huella distintos). Los programas no lo instalarán")
        else:
            print(f"  OK  versión {datos['version']} -> {archivo} "
                  f"({medido[0] / 1048576:.1f} MB, firmado y con huella correcta)")


def comprobar_puente(ruta_puente, nombre):
    repo, archivo = ruta_puente.split("/", 1)
    print(f"\nPuente de Workshop Tool 3.0 ({repo}/{archivo})")
    url = f"https://api.github.com/repos/gmfernandojesus/{repo}/contents/{archivo}?ref=main"
    peticion = urllib.request.Request(url, headers={"Accept": "application/vnd.github.raw"})
    original = json.loads((CARPETA / nombre).read_text(encoding="utf-8"))
    try:
        with urllib.request.urlopen(peticion, timeout=30) as r:
            puente = json.loads(r.read().decode("utf-8"))
    except Exception as e:
        fallo(f"el puente para la 3.0 no responde ({e}): esos clientes no verán "
              f"ninguna actualización")
        return
    antes = len(errores)
    for campo in ("version", "url"):
        if puente.get(campo) != original.get(campo):
            fallo(f"el puente para la 3.0 dice {campo}={puente.get(campo)!r} y "
                  f"{nombre} dice {original.get(campo)!r}. Copia {nombre} encima "
                  f"de {archivo} en el repo {repo} y súbelo ANTES que este")
    if len(errores) == antes:
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
    avisos = sorted(CARPETA.glob("*.json"))
    if not avisos:
        fallo("no hay ningún aviso (*.json) en el repositorio")
    for aviso in avisos:
        comprobar_aviso(aviso)
    for ruta_puente, nombre in PUENTES.items():
        comprobar_puente(ruta_puente, nombre)
    comprobar_revisiones()

    print()
    if errores:
        print(f"HAY {len(errores)} PROBLEMA(S): algún cliente no puede actualizar bien.")
        sys.exit(1)
    print("Todo bien: cada cliente descarga su programa.")


if __name__ == "__main__":
    main()
