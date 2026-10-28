"""Testy interfejsu Tkinter; wymagają środowiska z graficznym wyświetlaczem."""

import tempfile
import time
import tkinter as tk
import unittest
from pathlib import Path
from unittest.mock import patch

from gui import OknoKonwertera

PRZYKLADY = Path(__file__).resolve().parents[1] / "przyklady"


class TestGUI(unittest.TestCase):
    def setUp(self):
        try:
            self.app = OknoKonwertera()
        except tk.TclError as blad:
            self.skipTest(f"Brak aktywnego wyświetlacza dla Tkinter: {blad}")
        self.app.withdraw()
        self.addCleanup(self.app.destroy)
        self.temp = tempfile.TemporaryDirectory(prefix="gui_test_")
        self.addCleanup(self.temp.cleanup)
        self.app.katalog_var.set(self.temp.name)
        self.app.update_idletasks()

    def test_file_formats_dynamic(self):
        self.app.plik_var.set(str(PRZYKLADY / "osoby.csv"))
        self.assertEqual(self.app.lista_formatow["values"], ("JSON",))
        self.assertEqual(str(self.app.lista_formatow.cget("state")), "readonly")
        self.app.plik_var.set(str(PRZYKLADY / "dokument.docx"))
        self.assertEqual(self.app.lista_formatow["values"], ("PDF", "TXT"))

    def test_changing_input_resets_invalid_selected_target(self):
        self.app.plik_var.set(str(PRZYKLADY / "dokument.docx"))
        self.app.format_var.set("PDF")
        self.app.plik_var.set(str(PRZYKLADY / "osoby.csv"))
        self.assertEqual(self.app.format_var.get(), "")
        self.assertEqual(self.app.lista_formatow["values"], ("JSON",))

    def test_unknown_extension_disabled(self):
        self.app.plik_var.set(str(PRZYKLADY / "dane.xyz"))
        self.assertEqual(str(self.app.lista_formatow.cget("state")), "disabled")

    def test_missing_choice_and_bad_manual_pair(self):
        with self.assertRaisesRegex(Exception, "Wybierz plik"):
            self.app._przygotuj_zlecenie()
        self.app.plik_var.set(str(PRZYKLADY / "osoby.csv"))
        self.app.format_var.set("PDF")  # próba obejścia wyboru przez ręczną zmianę StringVar
        with self.assertRaisesRegex(Exception, "Nieobsługiwana"):
            self.app._przygotuj_zlecenie()

    def test_invalid_ui_submission_does_not_start_worker(self):
        self.app.plik_var.set(str(PRZYKLADY / "osoby.csv"))
        with patch("gui.messagebox.showerror") as bad, patch("gui.threading.Thread") as worker:
            self.app._uruchom_konwersje()
        bad.assert_called_once()
        worker.assert_not_called()
        self.assertFalse(self.app._w_trakcie)
        self.assertIn("Wybierz format", self.app.status_var.get())

    def test_conversion_runs_in_background_and_finishes(self):
        self.app.plik_var.set(str(PRZYKLADY / "osoby.csv"))
        self.app.format_var.set("JSON")
        with patch("gui.messagebox.showinfo") as message_ok, patch("gui.messagebox.showerror") as message_bad:
            self.app._uruchom_konwersje()
            self.assertTrue(self.app._w_trakcie)
            self.assertEqual(str(self.app.przycisk_konwertuj.cget("state")), "disabled")
            deadline = time.monotonic() + 8
            while self.app._w_trakcie and time.monotonic() < deadline:
                self.app.update()
                time.sleep(0.03)
            self.assertFalse(self.app._w_trakcie, "Interfejs nie odebrał zakończenia wątku")
            self.assertTrue(message_ok.called)
            self.assertFalse(message_bad.called)
            self.assertTrue((Path(self.temp.name) / "osoby.json").is_file())
            self.assertIn("Sukces", self.app.status_var.get())

    def test_conversion_error_shows_dialog_and_recovers(self):
        self.app.plik_var.set(str(PRZYKLADY / "bledny.json"))
        self.app.format_var.set("CSV")
        with patch("gui.messagebox.showerror") as message_bad:
            self.app._uruchom_konwersje()
            deadline = time.monotonic() + 8
            while self.app._w_trakcie and time.monotonic() < deadline:
                self.app.update()
                time.sleep(0.03)
            self.assertFalse(self.app._w_trakcie)
            self.assertTrue(message_bad.called)
            self.assertIn("Niepoprawny JSON", self.app.wynik_var.get())
            self.assertEqual(str(self.app.przycisk_konwertuj.cget("state")), "normal")


if __name__ == "__main__":
    unittest.main()
