# Dziennik etapów — Projekt 1

Ten plik jest **dziennikiem zmian do projektu**. Nie zastępuje autentycznych commitów w Twoim repozytorium Git i nie przypisuje nikomu nieistniejących commitów.

| Etap | Opis | Pliki |
|---|---|---|
| **Laboratorium 2** — stan zastany | Konwersja CSV ↔ JSON, schemat z kolumnami, UTF-8, błędy danych | `konwertery.py`, `main.py`, `przyklady/` |
| **Laboratorium 3** — stan zastany | TXT ↔ DOCX, DOCX → PDF, ODT → PDF, zewnętrzny LibreOffice | `konwertery.py`, `main.py` |
| **Laboratorium 4** — rozbudowa | Nowe GUI Tkinter/ttk, wybór pliku, katalogu, dynamiczna lista formatów, przycisk, status, pasek pracy, praca w tle bez zawieszania, blokowanie niedozwolonych wyborów | `gui.py`, `uruchom_gui.bat` |
| **Laboratorium 5** — rozbudowa | Logowanie sukcesów i błędów, komunikaty, testy poprawnych i wadliwych danych, kontrola procesu LibreOffice, instrukcja, raport testów | `usluga.py`, `tests/`, `README.md`, `RAPORT_TESTOW.md`, `.gitignore` |

**Oryginalne pliki `main.py`, `konwertery.py`, `requirements.txt` oraz `przyklady/` pozostają bez zmian.**

## Jak zachować Git na Windows

```powershell
git status
git add gui.py usluga.py uruchom_gui.bat tests README.md RAPORT_TESTOW.md HISTORIA_ZMIAN.md .gitignore
git commit -m "Laboratoria 4 i 5: Tkinter GUI, walidacja, logowanie i testy"
```

