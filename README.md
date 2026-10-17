# Actualizaciones

Avisos de versión de los programas de **FJGM Racing**. Este repositorio es
público a propósito: los programas instalados leen de aquí si hay una versión
nueva, y aquí se descargan los instaladores.

**Aquí no hay código fuente**, solo el número de versión de cada programa y sus
instaladores publicados en *Releases*.

| Programa | Aviso de versión |
|---|---|
| Chassis Program | [`chassis-program.json`](chassis-program.json) |
| Workshop Tool | [`workshop-tool.json`](workshop-tool.json) |

## Descargar la última versión

Están en la pestaña **[Releases](../../releases)** de este repositorio.

## Publicar una versión nueva

1. Subir la versión en el programa (`VERSION_PROGRAMA` en `routes.py` y
   `VersionApp` en `instalador.iss`) y compilar el instalador.
2. Editar aquí el `.json` de ese programa con la versión, la fecha y las notas.
3. Crear la Release con el instalador adjunto.

A los clientes les aparece el aviso solos la próxima vez que abran el programa.

## Reglas al publicar (las vigila el sistema solo)

Hay tres protecciones para que un cliente que actualiza un programa nunca
reciba otro:

1. **Dentro de cada programa** (Workshop Tool 3.3+, Chassis Program 5.4+):
   solo ofrece descargar un archivo si es su propio instalador. Si el aviso
   estuviera mal, el botón no aparece y le dice que te escriba.
2. **Antes de cada `git push` desde este ordenador**: `comprobar_avisos.py`
   se ejecuta solo y, si algo está mal, la subida se cancela.
3. **En GitHub**, en cada cambio, en cada Release y cada mañana: si algo está
   mal, te llega un correo.

Las reglas que se comprueban:

- **Cada `<programa>.json` descarga `<Programa>.-.Instalador.exe`**, el de su
  propio programa, con la dirección directa de la Release
  (`.../releases/download/<tag>/Workshop.Tool.-.Instalador.exe`). **Nunca
  `releases/latest`**: este repositorio es de varios programas y "latest" es
  la última Release de cualquiera de ellos.
- **Al publicar Workshop Tool, primero el puente** de la 3.0 (`version.json`
  del repo `taller-toro35`, copia exacta de `workshop-tool.json`) y después
  este repositorio.
- **`revisiones-licencias.txt` no se borra nunca**: sin él, en 30 días todos
  los clientes pasan a solo lectura.

**Programa nuevo:** no hay que apuntarlo en ningún sitio de aquí. Basta con
que su aviso se llame como el programa (`mi-programa.json`) y su instalador
`Mi Programa - Instalador.exe`; el comprobador lo deduce del nombre.

**En un ordenador nuevo**, después de clonar este repositorio, activa la
comprobación antes de subir con: `git config core.hooksPath .githooks`

Para comprobarlo a mano: `python comprobar_avisos.py`
