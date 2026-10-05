from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from hooks.navigation import build_navigation, document_title, readable_name


class NavigationTests(unittest.TestCase):
    def setUp(self):
        self.temp = TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)

    def write(self, relative_path, content):
        path = self.root / relative_path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        return path

    def test_practice_section_document_relationship(self):
        self.write("index.md", "# ABD Lab\n")
        self.write(
            "practicas/01-servidores/index.md",
            "# Práctica 1 - Servidores y Clientes\n",
        )
        self.write(
            "practicas/01-servidores/01-oracle/instalacion.md",
            "# Instalación de Oracle\n",
        )

        result = build_navigation(self.root, self.root)

        self.assertEqual(
            result,
            [
                {"Inicio": "index.md"},
                {
                    "Prácticas": [
                        {
                            "Práctica 1 - Servidores y Clientes": [
                                {"Resumen": "practicas/01-servidores/index.md"},
                                {
                                    "Oracle": [
                                        {
                                            "Instalación de Oracle":
                                            "practicas/01-servidores/"
                                            "01-oracle/instalacion.md"
                                        }
                                    ]
                                },
                            ]
                        }
                    ]
                },
            ],
        )

    def test_assets_and_empty_directories_are_not_in_menu(self):
        self.write("assets/notas.md", "# No debe aparecer\n")
        self.write("imagenes/notas.md", "# Tampoco\n")
        (self.root / "vacio").mkdir()

        self.assertEqual(build_navigation(self.root, self.root), [])

    def test_title_ignores_code_blocks(self):
        path = self.write(
            "documento.md",
            "```bash\n# Comentario de shell\n```\n\n# Título correcto\n",
        )

        self.assertEqual(document_title(path), "Título correcto")

    def test_document_is_not_modified(self):
        path = self.write(
            "oracle.md",
            "# Oracle\n\n```bash\nsudo example\n```\n",
        )
        original = path.read_bytes()

        build_navigation(self.root, self.root)

        self.assertEqual(path.read_bytes(), original)

    def test_new_documents_are_discovered_in_order(self):
        self.write("02-segundo.md", "# Segundo\n")
        self.write("01-primero.md", "# Primero\n")

        self.assertEqual(
            build_navigation(self.root, self.root),
            [
                {"Primero": "01-primero.md"},
                {"Segundo": "02-segundo.md"},
            ],
        )

        self.write("03-tercero.md", "# Tercero\n")

        self.assertEqual(
            build_navigation(self.root, self.root)[-1],
            {"Tercero": "03-tercero.md"},
        )

    def test_fallback_title(self):
        path = self.write("01-pruebas-remotas.md", "Documento sin H1.\n")

        self.assertEqual(document_title(path), "Pruebas remotas")
        self.assertEqual(readable_name("03-mongodb"), "MongoDB")


if __name__ == "__main__":
    unittest.main()
