"""Jednostkowe i integracyjne testy silnika z laboratoriów 2–3 oraz obsługi błędów."""

import csv
import json
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from konwertery import (
    BladKonwersji, Zlecenie, dostepne_formaty, wykonaj, wolna_nazwa,
    znajdz_libreoffice,
)
from usluga import wykonaj_z_logowaniem

KATALOG = Path(__file__).resolve().parents[1]
PRZYKLADY = KATALOG / "przyklady"


def libreoffice_dostepny() -> bool:
    try:
        znajdz_libreoffice()
    except BladKonwersji:
        return False
    return True
TEKST = [
    "Praca projektu konwerter",
    "Wyniki są dobre",
    "Wyniki dla znaków specjalnych ąęóśćń",
]


class TestKonwertery(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="konwerter_test_")
        self.addCleanup(self.temp.cleanup)
        self.wyniki = Path(self.temp.name)

    def convert(self, filename, target):
        return wykonaj(Zlecenie(PRZYKLADY / filename, target, self.wyniki))

    def test_registry_targets_depend_on_extension(self):
        self.assertEqual(dostepne_formaty(Path("dane.csv")), [".json"])
        self.assertEqual(dostepne_formaty(Path("dane.json")), [".csv"])
        self.assertEqual(dostepne_formaty(Path("dokument.docx")), [".pdf", ".txt"])
        self.assertEqual(dostepne_formaty(Path("dane.exe")), [])

    def test_missing_source(self):
        with self.assertRaisesRegex(BladKonwersji, "Nie znaleziono pliku"):
            wykonaj(Zlecenie(self.wyniki / "nie_ma.csv", ".json", self.wyniki))

    def test_missing_output_dir(self):
        with self.assertRaisesRegex(BladKonwersji, "Nie znaleziono katalogu"):
            wykonaj(Zlecenie(PRZYKLADY / "osoby.csv", ".json", self.wyniki / "nie_ma"))

    def test_unsupported_pair(self):
        with self.assertRaisesRegex(BladKonwersji, "Nieobsługiwana konwersja"):
            self.convert("osoby.csv", ".pdf")

    def test_csv_to_json_preserves_polish_and_order(self):
        p = self.convert("osoby.csv", ".json")
        value = json.loads(p.read_text(encoding="utf-8"))
        self.assertEqual(value["columns"], ["Akapit", "Treść"])
        self.assertEqual([r["Treść"] for r in value["rows"]], TEKST)
        self.assertIn("ąęóśćń", p.read_text(encoding="utf-8"))

    def test_json_to_csv_preserves_polish_and_order(self):
        p = self.convert("osoby.json", ".csv")
        with p.open(encoding="utf-8-sig", newline="") as f:
            reader = csv.DictReader(f)
            self.assertEqual(reader.fieldnames, ["Akapit", "Treść"])
            self.assertEqual([r["Treść"] for r in reader], TEKST)

    def test_empty_and_leading_zeros_preserved(self):
        source = self.wyniki / "zera.csv"
        source.write_text('Kod,Opis\n0012,""\n0023,"Łódź, Polska"\n', encoding="utf-8")
        intermediate = wykonaj(Zlecenie(source, ".json", self.wyniki))
        result = wykonaj(Zlecenie(intermediate, ".csv", self.wyniki))
        with result.open(encoding="utf-8-sig", newline="") as f:
            reader = list(csv.DictReader(f))
        self.assertEqual(reader[0]["Kod"], "0012")
        self.assertEqual(reader[0]["Opis"], "")
        self.assertEqual(reader[1]["Opis"], "Łódź, Polska")

    def test_bad_json_controlled_error(self):
        with self.assertRaisesRegex(BladKonwersji, "Niepoprawny JSON"):
            self.convert("bledny.json", ".csv")

    def test_bad_json_structure_controlled_error(self):
        bad = self.wyniki / "zly.json"
        bad.write_text('{"zly": "schemat"}', encoding="utf-8")
        with self.assertRaisesRegex(BladKonwersji, "columns"):
            wykonaj(Zlecenie(bad, ".csv", self.wyniki))

    def test_wrong_csv_column_count(self):
        bad = self.wyniki / "zly.csv"
        bad.write_text('A,B\n1\n', encoding="utf-8")
        with self.assertRaisesRegex(BladKonwersji, "wiersz 2"):
            wykonaj(Zlecenie(bad, ".json", self.wyniki))

    def test_duplicate_csv_columns(self):
        bad = self.wyniki / "duplikat.csv"
        bad.write_text('A,A\n1,2\n', encoding="utf-8")
        with self.assertRaisesRegex(BladKonwersji, "powtarzające"):
            wykonaj(Zlecenie(bad, ".json", self.wyniki))

    def test_existing_output_safe_suffix(self):
        first = self.convert("osoby.csv", ".json")
        second = self.convert("osoby.csv", ".json")
        self.assertEqual(first.name, "osoby.json")
        self.assertEqual(second.name, "osoby_1.json")
        self.assertTrue(first.exists() and second.exists())
        self.assertEqual(wolna_nazwa(PRZYKLADY / "osoby.csv", self.wyniki, ".json").name, "osoby_2.json")

    def test_txt_to_docx(self):
        from docx import Document
        created = self.convert("notatka.txt", ".docx")
        doc = Document(created)
        content = [p.text for p in doc.paragraphs if p.text]
        self.assertEqual(content, TEKST)

    def test_docx_to_txt(self):
        created = self.convert("dokument.docx", ".txt")
        self.assertEqual(created.read_text(encoding="utf-8").splitlines(), TEKST)

    def test_invalid_docx(self):
        bad = self.wyniki / "zepsuty.docx"
        bad.write_text("To nie jest archiwum DOCX", encoding="utf-8")
        with self.assertRaisesRegex(BladKonwersji, "Nie można odczytać DOCX"):
            wykonaj(Zlecenie(bad, ".txt", self.wyniki))

    @unittest.skipUnless(libreoffice_dostepny(), "Brak LibreOffice")
    def test_docx_to_pdf_integration(self):
        created = self.convert("dokument.docx", ".pdf")
        self.assertGreater(created.stat().st_size, 1000)
        self.assertEqual(created.read_bytes()[:4], b"%PDF")

    @unittest.skipUnless(libreoffice_dostepny(), "Brak LibreOffice")
    def test_odt_to_pdf_integration(self):
        created = self.convert("dokument.odt", ".pdf")
        self.assertGreater(created.stat().st_size, 1000)
        self.assertEqual(created.read_bytes()[:4], b"%PDF")

    @patch("konwertery.znajdz_libreoffice", side_effect=BladKonwersji("Brak LibreOffice"))
    def test_missing_libreoffice(self, _mock):
        with self.assertRaisesRegex(BladKonwersji, "Brak LibreOffice"):
            self.convert("dokument.docx", ".pdf")

    @patch("konwertery.znajdz_libreoffice", return_value="/example/soffice")
    @patch("konwertery.subprocess.run", return_value=SimpleNamespace(returncode=13, stderr="awaria", stdout=""))
    def test_external_program_exit_code_and_safe_shell(self, mocked_run, _mock_find):
        with self.assertRaisesRegex(BladKonwersji, "kodem 13"):
            self.convert("dokument.docx", ".pdf")
        args, kwargs = mocked_run.call_args
        self.assertIn("--headless", args[0])
        self.assertFalse(kwargs["shell"])
        self.assertEqual(kwargs["timeout"], 90)

    @patch("konwertery.znajdz_libreoffice", return_value="/example/soffice")
    @patch("konwertery.subprocess.run", return_value=SimpleNamespace(returncode=0, stderr="", stdout=""))
    def test_external_success_exit_but_missing_pdf(self, mocked_run, _mock_find):
        with self.assertRaisesRegex(BladKonwersji, "nie utworzył oczekiwanego"):
            self.convert("dokument.odt", ".pdf")

    def test_logging_success_and_error(self):
        with self.assertLogs("konwerter", level="INFO") as logs:
            result = wykonaj_z_logowaniem(Zlecenie(PRZYKLADY / "osoby.csv", ".json", self.wyniki))
            self.assertTrue(result.is_file())
            with self.assertRaises(BladKonwersji):
                wykonaj_z_logowaniem(Zlecenie(PRZYKLADY / "bledny.json", ".csv", self.wyniki))
        self.assertTrue(any("SUKCES" in line for line in logs.output))
        self.assertTrue(any("BŁĄD" in line for line in logs.output))


if __name__ == "__main__":
    unittest.main()
