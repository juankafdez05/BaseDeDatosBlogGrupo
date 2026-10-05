# ABD Lab · Blog de Base de Datos

Blog técnico de Rube, Alfredo y Juan Carlos.

**Centro:** IES Gonzalo Nazareno  
**Curso:** 2.º ASIR · 2026/27  
**Asignatura:** Base de Datos

## Objetivo

Documentar las prácticas realizadas durante el curso, conservando una
estructura clara, ampliable y fácil de mantener.

El contenido se organiza mediante esta relación:

Práctica → Apartado → Documento

Los apartados pueden contener subapartados para separar autores, servidores,
clientes, aplicaciones y evidencias.

## Equipo

- Rube.
- Alfredo.
- Juan Carlos.

La correspondencia con Alumno 1, Alumno 2 y Alumno 3 y los roles de cada
práctica se registran en su página de seguimiento.

## Tecnologías

- Python 3.12.
- MkDocs.
- Material for MkDocs.
- Markdown.
- GitHub Actions y GitHub Pages.

## Puesta en marcha local

Desde la raíz del repositorio:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt

python -m unittest discover -s tests -v
python -m mkdocs build --strict
python -m mkdocs serve
```

Abrir la dirección local que muestre el último comando.

En Windows, la activación del entorno desde PowerShell es:

```powershell
.venv\Scripts\Activate.ps1
```

## Publicación en GitHub Pages

1. Subir estos archivos a la rama `main`.
2. Entrar en Settings → Pages.
3. En Build and deployment, seleccionar GitHub Actions.
4. Revisar la ejecución del workflow "Validar y publicar blog".
5. Abrir la dirección mostrada por el despliegue.

Si la rama principal no se llama `main`, cambiar ese nombre en
`.github/workflows/pages.yml`.

Las pull requests ejecutan pruebas y construyen la web, pero no la publican.

## Cómo añadir un documento

Crear un archivo `.md` dentro del apartado correspondiente.

Ejemplo:

```text
docs/practicas/01-servidores-clientes/03-postgresql/instalacion.md
```

No hace falta editar el menú ni añadir front matter.

El título se obtiene del primer encabezado de nivel 1:

```markdown
# Instalación de PostgreSQL
```

Si no existe, se utiliza el nombre del archivo.

Los prefijos numéricos ordenan carpetas y documentos, pero se eliminan de
las etiquetas del menú.

## Cómo añadir un apartado

Crear una carpeta y añadir documentos:

```text
docs/practicas/01-servidores-clientes/04-mysql/
├── index.md
├── rube.md
├── alfredo.md
└── juan-carlos.md
```

El archivo `index.md` es opcional. Si existe:

- Actúa como resumen del apartado.
- Su primer encabezado define el nombre de la sección.
- Aparece como "Resumen" dentro de esa sección.

Las carpetas vacías no aparecen en el menú.

## Cómo añadir una práctica

Crear otra carpeta dentro de `docs/practicas/`:

```text
docs/practicas/02-nombre-de-la-practica/
├── index.md
├── 01-primer-apartado/
│   └── desarrollo.md
└── 02-segundo-apartado/
    └── pruebas.md
```

En su `index.md`, incluir el título, objetivos, enunciado resumido,
responsabilidades y criterios de entrega.

La práctica aparecerá automáticamente en la navegación.

## Documento original de Oracle

Subir el documento sin modificar su contenido a:

```text
docs/practicas/01-servidores-clientes/01-oracle/instalacion.md
```

La publicación no equivale a una revisión técnica de los comandos ni
demuestra que la práctica esté terminada.

No marcar como validado hasta añadir las evidencias reales y completar
la revisión correspondiente.

## Imágenes y evidencias

Guardar las imágenes cerca del documento:

```text
01-oracle/
├── instalacion.md
└── imagenes/
    └── listener.png
```

Referenciarlas con rutas relativas:

```markdown
![Estado del Listener](imagenes/listener.png)
```

No utilizar rutas locales del ordenador ni rutas que empiecen por `/`.

Para enlazar otro documento:

```markdown
[Pruebas remotas](pruebas-remotas.md)
```

Los vídeos pueden enlazarse desde el documento. Guardar los vídeos grandes
fuera del repositorio.

## Código de las aplicaciones

Guardar el código fuente fuera de `docs/`, por ejemplo:

```text
aplicaciones/
└── practica-01/
    ├── mongodb/
    ├── mysql/
    └── postgresql/
```

En cada documento, añadir el enlace al directorio correspondiente de GitHub
y las instrucciones de ejecución.

Cada aplicación debe disponer de sus propias dependencias e instrucciones.
Las dependencias del blog no son las de las aplicaciones.

## Estados de trabajo

Usar estados explícitos en la página de seguimiento:

- Pendiente.
- En desarrollo.
- En revisión.
- Validado.

La existencia de un documento no implica que la tarea esté terminada.
No se calcula un porcentaje automático a partir del número de archivos.

## Trabajo colaborativo

1. Crear una rama de trabajo.
2. Añadir o actualizar documentación.
3. Ejecutar las pruebas y la compilación.
4. Abrir una pull request.
5. Solicitar revisión a otro miembro.
6. Fusionar en `main` cuando las comprobaciones sean correctas.

Los cambios en `mkdocs.yml`, `hooks/` y `.github/` requieren especial revisión.

## Seguridad editorial

- No subir contraseñas, claves privadas, tokens ni archivos `.env`.
- Revisar capturas y salidas antes de publicarlas.
- Usar credenciales ficticias en los ejemplos.
- Mantener fuera de `docs/` cualquier información privada.
- Realizar las demostraciones de inyección únicamente en el laboratorio
  autorizado, con datos y credenciales de prueba.
- Revisar también los archivos no Markdown: pueden formar parte del sitio.

## Validación

```bash
python -m unittest discover -s tests -v
python -m mkdocs build --strict
```

Además, comprobar manualmente:

- Navegación en escritorio y móvil.
- Búsqueda de un término presente en Oracle.
- Tema claro y oscuro.
- Tablas, bloques de código e imágenes.
- Enlaces entre documentos.
- Aparición de un nuevo apartado después de añadir un `.md`.

Al añadir archivos o cambiar títulos durante la previsualización local,
reiniciar `mkdocs serve` para regenerar el menú.

## Archivos generados

`site/` contiene la web compilada y no debe subirse al repositorio.

## Licencia

Pendiente de acordar por el grupo. No se asigna automáticamente una
licencia al contenido, a las imágenes o al código de las prácticas.
