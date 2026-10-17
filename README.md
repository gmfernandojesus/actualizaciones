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
