"""Graficzny konwerter plików – laboratoria 4 i 5.

Uruchomienie: py gui.py (Windows) lub python gui.py.
Przepływ: Tkinter -> Zlecenie -> usluga -> konwertery (lab. 2 i 3).
Tkinter działa wyłącznie w głównym wątku, konwersja w osobnym wątku.
"""

import os
import queue
import subprocess
import sys
import threading
import time
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

from konwertery import BladKonwersji, Zlecenie, dostepne_formaty
from usluga import LOGGER, skonfiguruj_logi, wykonaj_z_logowaniem

KATALOG_PROJEKTU = Path(__file__).resolve().parent


class OknoKonwertera(tk.Tk):
    """Interfejs bez logiki formatów: źródłem prawdy jest rejestr konwerterów."""

    def __init__(self):
        super().__init__()
        self.title("Uniwersalny konwerter plików | Python")
        self.geometry("800x690")
        self.minsize(680, 640)
        self.configure(background="#F4F7FB")

        self.plik_var = tk.StringVar()
        self.katalog_var = tk.StringVar(value=str(KATALOG_PROJEKTU / "wyniki"))
        self.format_var = tk.StringVar()
        self.status_var = tk.StringVar(value="Gotowy do pracy — wybierz plik źródłowy.")
        self.formaty_info_var = tk.StringVar(value="Najpierw wybierz plik źródłowy.")
        self.wynik_var = tk.StringVar(value="")

        self._w_trakcie = False
        self._wyniki = queue.Queue()
        self._identyfikator_after = None
        self._skonfiguruj_styl()
        self._zbuduj_interfejs()

        (KATALOG_PROJEKTU / "wyniki").mkdir(parents=True, exist_ok=True)
        self.plik_var.trace_add("write", self._aktualizuj_formaty)
        self.protocol("WM_DELETE_WINDOW", self._zamknij)
        self._aktualizuj_formaty()

    def _skonfiguruj_styl(self):
        styl = ttk.Style(self)
        if "clam" in styl.theme_names():
            styl.theme_use("clam")
        styl.configure("TFrame", background="#F4F7FB")
        styl.configure("Karta.TFrame", background="#FFFFFF")
        styl.configure("TLabel", background="#F4F7FB", foreground="#22304B", font=("Segoe UI", 10))
        styl.configure("Karta.TLabel", background="#FFFFFF", foreground="#24334C", font=("Segoe UI", 10))
        styl.configure("Pole.TLabel", background="#FFFFFF", foreground="#24334C", font=("Segoe UI", 10, "bold"))
        styl.configure("Wskazowka.TLabel", background="#FFFFFF", foreground="#64748B", font=("Segoe UI", 9))
        styl.configure("TEntry", padding=8)
        styl.configure("TCombobox", padding=7)
        styl.configure("TButton", padding=(14, 9), font=("Segoe UI", 10))
        styl.configure("Glowny.TButton", padding=(20, 12), background="#1769D2", foreground="#FFFFFF", font=("Segoe UI", 10, "bold"))
        styl.map(
            "Glowny.TButton",
            background=[("disabled", "#C3CDDB"), ("active", "#0952A5")],
            foreground=[("disabled", "#4B5563")],
        )
        styl.configure("Pasek.Horizontal.TProgressbar", thickness=7)

    def _zbuduj_interfejs(self):
        naglowek = tk.Frame(self, background="#102A51", height=108)
        naglowek.pack(fill="x")
        naglowek.pack_propagate(False)
        tk.Label(
            naglowek, text="UNIWERSALNY KONWERTER PLIKÓW",
            background="#102A51", foreground="#FFFFFF",
            font=("Segoe UI", 18, "bold"), anchor="w",
        ).pack(fill="x", padx=30, pady=(22, 2))
        tk.Label(
            naglowek, text="Projekt 1  •  Programowanie V  •  laboratoria 2–5",
            background="#102A51", foreground="#BDCAE0",
            font=("Segoe UI", 10), anchor="w",
        ).pack(fill="x", padx=30)

        glowna = ttk.Frame(self)
        glowna.pack(fill="both", expand=True, padx=26, pady=(21, 12))
        karta = ttk.Frame(glowna, style="Karta.TFrame", padding=22)
        karta.pack(fill="x")
        karta.columnconfigure(0, weight=1)

        ttk.Label(karta, text="1. Plik wejściowy", style="Pole.TLabel").grid(row=0, column=0, columnspan=2, sticky="w")
        self.wejscie_pliku = ttk.Entry(karta, textvariable=self.plik_var)
        self.wejscie_pliku.grid(row=1, column=0, sticky="ew", pady=(6, 16), padx=(0, 9))
        self.przycisk_pliku = ttk.Button(karta, text="Wybierz plik…", command=self._wybierz_plik)
        self.przycisk_pliku.grid(row=1, column=1, sticky="ew", pady=(6, 16))

        ttk.Label(karta, text="2. Katalog wynikowy", style="Pole.TLabel").grid(row=2, column=0, columnspan=2, sticky="w")
        self.wejscie_katalogu = ttk.Entry(karta, textvariable=self.katalog_var)
        self.wejscie_katalogu.grid(row=3, column=0, sticky="ew", pady=(6, 16), padx=(0, 9))
        self.przycisk_katalogu = ttk.Button(karta, text="Wybierz katalog…", command=self._wybierz_katalog)
        self.przycisk_katalogu.grid(row=3, column=1, sticky="ew", pady=(6, 16))

        ttk.Label(karta, text="3. Format docelowy", style="Pole.TLabel").grid(row=4, column=0, columnspan=2, sticky="w")
        self.lista_formatow = ttk.Combobox(karta, textvariable=self.format_var, state="disabled", width=18)
        self.lista_formatow.grid(row=5, column=0, sticky="w", pady=(6, 5))
        self.info_formatow = ttk.Label(karta, textvariable=self.formaty_info_var, style="Wskazowka.TLabel", wraplength=580)
        self.info_formatow.grid(row=6, column=0, columnspan=2, sticky="w", pady=(0, 2))

        przyciski = ttk.Frame(glowna)
        przyciski.pack(fill="x", pady=(18, 13))
        self.przycisk_konwertuj = ttk.Button(
            przyciski, text="Konwertuj plik", style="Glowny.TButton", command=self._uruchom_konwersje
        )
        self.przycisk_konwertuj.pack(side="left")
        self.przycisk_otworz = ttk.Button(przyciski, text="Otwórz folder wyników", command=self._otworz_katalog)
        self.przycisk_otworz.pack(side="right")

        panel_statusu = ttk.Frame(glowna)
        panel_statusu.pack(fill="x")
        ttk.Label(panel_statusu, text="STATUS", font=("Segoe UI", 9, "bold")).pack(anchor="w", pady=(0, 5))
        self.etykieta_statusu = ttk.Label(panel_statusu, textvariable=self.status_var, wraplength=690)
        self.etykieta_statusu.pack(fill="x")
        self.pasek = ttk.Progressbar(panel_statusu, mode="indeterminate", style="Pasek.Horizontal.TProgressbar")
        self.pasek.pack(fill="x", pady=(10, 6))
        self.etykieta_wyniku = ttk.Label(panel_statusu, textvariable=self.wynik_var, wraplength=690)
        self.etykieta_wyniku.pack(fill="x")

        ttk.Label(
            self, text="Obsługiwane: CSV ↔ JSON  |  TXT ↔ DOCX  |  DOCX/ODT → PDF",
            font=("Segoe UI", 9), foreground="#64748B",
        ).pack(side="bottom", pady=(0, 12))

    def _wybierz_plik(self):
        nazwa = filedialog.askopenfilename(
            parent=self, title="Wybierz plik do konwersji",
            initialdir=str(KATALOG_PROJEKTU / "przyklady"),
            filetypes=[("Obsługiwane pliki", "*.csv *.json *.txt *.docx *.odt"), ("Wszystkie pliki", "*.*")],
        )
        if nazwa:
            self.plik_var.set(nazwa)

    def _wybierz_katalog(self):
        aktualny = Path(self.katalog_var.get().strip())
        start = aktualny if aktualny.is_dir() else KATALOG_PROJEKTU
        nazwa = filedialog.askdirectory(parent=self, title="Wybierz katalog wynikowy", initialdir=str(start))
        if nazwa:
            self.katalog_var.set(nazwa)

    def _aktualizuj_formaty(self, *_):
        if self._w_trakcie:
            return
        plik = Path(self.plik_var.get().strip())
        mozliwe = [x.lstrip(".").upper() for x in dostepne_formaty(plik)]
        poprzedni = self.format_var.get()
        self.lista_formatow.configure(values=mozliwe, state="readonly" if mozliwe else "disabled")
        if poprzedni not in mozliwe:
            self.format_var.set("")
        if mozliwe:
            self.formaty_info_var.set("Dostępne formaty: " + ", ".join(mozliwe) + ".")
        elif self.plik_var.get().strip():
            self.formaty_info_var.set("Ten typ pliku nie jest obsługiwany.")
        else:
            self.formaty_info_var.set("Najpierw wybierz plik źródłowy.")

    def _przygotuj_zlecenie(self) -> Zlecenie:
        nazwa = self.plik_var.get().strip()
        katalog = self.katalog_var.get().strip()
        format_docelowy = self.format_var.get().strip().lower()
        if not nazwa:
            raise BladKonwersji("Wybierz plik wejściowy.")
        if not katalog:
            raise BladKonwersji("Wybierz katalog docelowy.")
        if not format_docelowy:
            raise BladKonwersji("Wybierz format docelowy z listy.")
        zlecenie = Zlecenie(Path(nazwa), "." + format_docelowy, Path(katalog))
        # Niezależna walidacja blokuje ręcznie wpisane niedozwolone pary.
        zlecenie.sprawdz()
        return zlecenie

    def _ustaw_zajety(self, zajety: bool):
        self._w_trakcie = zajety
        for widget in (self.wejscie_pliku, self.wejscie_katalogu,
                       self.przycisk_pliku, self.przycisk_katalogu,
                       self.przycisk_konwertuj, self.przycisk_otworz):
            widget.configure(state="disabled" if zajety else "normal")
        if zajety:
            self.lista_formatow.configure(state="disabled")
            self.pasek.start(12)
        else:
            self.pasek.stop()
            self._aktualizuj_formaty()

    def _uruchom_konwersje(self):
        if self._w_trakcie:
            return
        try:
            zlecenie = self._przygotuj_zlecenie()
        except BladKonwersji as blad:
            LOGGER.warning("ODRZUCONO ZLECENIE | %s", blad)
            self.status_var.set("Błąd: " + str(blad))
            messagebox.showerror("Nie można rozpocząć konwersji", str(blad), parent=self)
            return

        self.wynik_var.set("")
        self.status_var.set(f"Konwersja w toku: {zlecenie.plik.name} → {zlecenie.format_docelowy.upper()}")
        self._ustaw_zajety(True)
        threading.Thread(target=self._zadanie_w_tle, args=(zlecenie,), daemon=True).start()
        self._identyfikator_after = self.after(90, self._sprawdz_kolejke)

    def _zadanie_w_tle(self, zlecenie: Zlecenie):
        """Wyłącznie praca na plikach; nie dotyka widgetów Tkinter."""
        poczatek = time.perf_counter()
        try:
            wynik = wykonaj_z_logowaniem(zlecenie)
            self._wyniki.put((True, wynik, time.perf_counter() - poczatek))
        except Exception as blad:
            # Wyjątek jest już zarejestrowany przez wykonaj_z_logowaniem().
            self._wyniki.put((False, str(blad), time.perf_counter() - poczatek))

    def _sprawdz_kolejke(self):
        self._identyfikator_after = None
        try:
            powodzenie, odpowiedz, czas = self._wyniki.get_nowait()
        except queue.Empty:
            self._identyfikator_after = self.after(90, self._sprawdz_kolejke)
            return

        self._ustaw_zajety(False)
        if powodzenie:
            self.status_var.set(f"Sukces! Konwersja zakończona w {czas:.2f} s.")
            self.wynik_var.set("Zapisano: " + str(odpowiedz))
            messagebox.showinfo("Konwersja zakończona", f"Utworzono plik:\n{odpowiedz}", parent=self)
        else:
            self.status_var.set("Nie udało się wykonać konwersji.")
            self.wynik_var.set("Błąd: " + str(odpowiedz))
            messagebox.showerror("Błąd konwersji", str(odpowiedz), parent=self)

    def _otworz_katalog(self):
        katalog = Path(self.katalog_var.get().strip())
        if not katalog.is_dir():
            messagebox.showerror("Niepoprawny katalog", "Wskazany katalog nie istnieje.", parent=self)
            return
        try:
            if sys.platform == "win32":
                os.startfile(str(katalog))
            elif sys.platform == "darwin":
                subprocess.Popen(["open", str(katalog)], shell=False)
            else:
                subprocess.Popen(["xdg-open", str(katalog)], shell=False)
        except OSError as blad:
            messagebox.showerror("Nie można otworzyć katalogu", str(blad), parent=self)

    def _zamknij(self):
        if self._w_trakcie:
            messagebox.showwarning("Konwersja w toku", "Zakończ konwersję przed zamknięciem okna.", parent=self)
            return
        if self._identyfikator_after is not None:
            self.after_cancel(self._identyfikator_after)
        self.destroy()


def main():
    try:
        skonfiguruj_logi()
    except OSError as blad:
        # Brak uprawnień do pliku dziennika nie powinien uniemożliwić konwersji.
        print(f"Uwaga: nie można utworzyć dziennika: {blad}", file=sys.stderr)
    app = OknoKonwertera()
    app.mainloop()


if __name__ == "__main__":
    main()
