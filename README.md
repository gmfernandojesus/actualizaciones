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

## Reglas al publicar (las vigila GitHub solo)

Cada vez que se publica algo aquí, y cada mañana, GitHub ejecuta
`comprobar_avisos.py`. Si algo está mal, **te llega un correo** y la
publicación sale con una ❌ roja en la pestaña *Actions*.

1. **El `url` de cada aviso apunta al instalador de SU programa**, nunca a
   `releases/latest`: este repositorio es de varios programas y "latest" es
   la última Release de cualquiera de ellos.
   Bien: `.../releases/download/v2026.10.17/Workshop.Tool.-.Instalador.exe`
2. **Al publicar Workshop Tool, actualizar también el puente** de la 3.0
   (`version.json` del repo `taller-toro35`) con el mismo contenido que
   `workshop-tool.json`.
3. **`revisiones-licencias.txt` no se borra nunca**: sin él, en 30 días todos
   los clientes pasan a solo lectura.
4. **Programa nuevo**: añadirlo a `PROGRAMAS` en `comprobar_avisos.py`.

Para comprobarlo a mano antes de publicar: `python comprobar_avisos.py`
