"""Construcción del menú a partir del árbol de documentación."""

from pathlib import Path
import re


IGNORED_DIRECTORIES = {"assets", "imagenes", "images", "__pycache__"}

SPECIAL_TITLES = {
    "practicas": "Prácticas",
    "oracle": "Oracle",
    "postgresql": "PostgreSQL",
    "mysql": "MySQL",
    "mongodb": "MongoDB",
    "cassandra": "Cassandra",
    "redis": "Redis",
    "neo4j": "Neo4j",
    "couchdb": "CouchDB",
    "memcached": "Memcached",
}


def readable_name(name):
    """Elimina el prefijo de orden y transforma el nombre en una etiqueta."""
    name = re.sub(r"^\d+[-_ ]*", "", name)

    if name.lower() in SPECIAL_TITLES:
        return SPECIAL_TITLES[name.lower()]

    return name.replace("-", " ").replace("_", " ").capitalize()


def document_title(path):
    """Obtiene el primer H1, ignorando bloques de código cercados."""
    fence_character = None
    fence_length = 0

    for line in path.read_text(encoding="utf-8-sig").splitlines():
        stripped = line.lstrip()
        fence = re.match(r"(`{3,}|~{3,})", stripped)

        if fence:
            marker = fence.group(1)

            if fence_character is None:
                fence_character = marker[0]
                fence_length = len(marker)
            elif (
                marker[0] == fence_character
                and len(marker) >= fence_length
                and not stripped[len(marker):].strip()
            ):
                fence_character = None
                fence_length = 0

            continue

        if fence_character is not None:
            continue

        heading = re.match(r"^#\s+(.+?)\s*$", line)
        if heading:
            title = re.sub(r"\s+#+\s*$", "", heading.group(1))
            return title.strip()

    return readable_name(path.stem)


def find_index(directory):
    """Encuentra index.md sin depender de las mayúsculas de la extensión."""
    for path in sorted(directory.iterdir(), key=lambda item: item.name.casefold()):
        if path.is_file() and path.name.casefold() == "index.md":
            return path

    return None


def build_navigation(directory, root):
    """Recorre las carpetas sin seguir enlaces simbólicos."""
    items = []
    index = find_index(directory)

    if index is not None and not index.is_symlink():
        label = "Inicio" if directory == root else "Resumen"
        items.append({label: index.relative_to(root).as_posix()})

    for path in sorted(directory.iterdir(), key=lambda item: item.name.casefold()):
        if path.name.startswith(".") or path.is_symlink() or path == index:
            continue

        if path.is_file() and path.suffix.casefold() == ".md":
            items.append({
                document_title(path): path.relative_to(root).as_posix()
            })

        elif path.is_dir() and path.name.lower() not in IGNORED_DIRECTORIES:
            children = build_navigation(path, root)

            if not children:
                continue

            section_index = find_index(path)
            title = readable_name(path.name)

            if section_index is not None and not section_index.is_symlink():
                title = document_title(section_index)

            items.append({title: children})

    return items


def on_config(config):
    """Hook ejecutado por MkDocs antes de construir la navegación."""
    root = Path(config["docs_dir"]).resolve()
    config["nav"] = build_navigation(root, root)
    return config
