# Raport sprawdzenia projektu — laboratorium 5

**Data weryfikacji:** 22.10.2026  
**Kod bazowy:** `python-course.zip` dostarczony przez użytkownika.  
**Środowisko weryfikacji:** Linux, Python 3.13, python-docx 1.2, LibreOffice, Tkinter na wirtualnym ekranie Xvfb.  
**Uruchomienie:** `xvfb-run -a python -m unittest discover -s tests -v`

## Wynik automatyczny

**28 testów: 28 zaliczonych, 0 błędów, 0 pominiętych** w środowisku wirtualnego ekranu z dostępnym LibreOffice.

| Scenariusz | Oczekiwany rezultat | Wynik |
|---|---|---|
| Rejestr formatów w zależności od rozszerzenia | Tylko obsługiwane kierunki, reszta zablokowana | PASS |
| CSV → JSON | Unikalne nagłówki, poprawne rekordy, polskie znaki | PASS |
| JSON → CSV | Zachowanie kolejności kolumn i polskich znaków | PASS |
| CSV → JSON → CSV | Wiodące zera i puste pola zachowane | PASS |
| Błędny JSON / schemat JSON | Kontrolowany komunikat błędu | PASS |
| Niepoprawne kolumny CSV | Kontrolowany komunikat błędu | PASS |
| TXT → DOCX / DOCX → TXT | Akapity i polskie znaki czytelne | PASS |
| Uszkodzony DOCX | Kontrolowany komunikat | PASS |
| DOCX → PDF i ODT → PDF | Poprawny plik zaczynający się od `%PDF` | PASS |
| Brak LibreOffice (symulowany) | Czytelny błąd | PASS |
| LibreOffice zwraca błąd / nie tworzy PDF | Zatrzymanie i komunikat zamiast fałszywego sukcesu | PASS |
| Uruchomienie procesu zewnętrznego | `shell=False`, limit 90 s | PASS |
| Nieistniejący plik/katalog, niedozwolona para | Operacja zablokowana | PASS |
| Plik wynikowy już istnieje | Bezpieczny sufiks `_1`, `_2` | PASS |
| Logowanie informacji i błędów | Zapisane zdarzenia `SUKCES` i `BŁĄD` | PASS |
| GUI: wybór typu źródłowego | Lista formatów aktualizuje się dynamicznie | PASS |
| GUI: zmiana pliku | Niedozwolony poprzedni format zostaje wyczyszczony | PASS |
| GUI: nieznane rozszerzenie | Combobox nieaktywny | PASS |
| GUI: niepoprawne dane/pary | Obsługa weryfikacji przed konwersją | PASS |
| GUI: niekompletny formularz | Pokazanie błędu bez uruchomienia wątku | PASS |
| GUI: konwersja w tle | Blokada przycisków w trakcie, sukces i odblokowanie | PASS |
| GUI: błąd konwersji | Dialog błędu, ponowne odblokowanie interfejsu | PASS |

## Ograniczenia weryfikacji

- Kod Tkinter został sprawdzony automatycznie na wirtualnym ekranie. **Nie wykonano testu interaktywnego na rzeczywistym Windowsie użytkownika**, dlatego warto przejść poniższą listę demonstracyjną w VS Code.
- Test PDF sprawdza, czy plik istnieje i ma nagłówek PDF; nie porównuje piksel po pikselu wyglądu dokumentu.
- Przykładowe pliki pozostają identyczne z udostępnionym źródłem. Generator wyników działa bez modyfikowania danych wejściowych.

## Krótka demonstracja na zaliczenie

1. Uruchom GUI poleceniem `py gui.py`.
2. Wybierz `przyklady/osoby.csv`, pokaż, że format docelowy to tylko `JSON`, zrób konwersję i otwórz wynik.
3. Wybierz `przyklady/dokument.docx`, pokaż, że dostępne są `PDF` i `TXT`; wybierz `PDF`, uruchom konwersję i otwórz plik.
4. Uruchom konwersję do PDF ponownie; nowy plik powinien otrzymać sufiks `_1` (bez nadpisania poprzedniego).
5. Wybierz `przyklady/bledny.json`, ustaw `CSV`, zademonstruj czytelny błąd zamiast awarii.
6. Otwórz `logs/konwerter.log` i pokaż wpisy startu, sukcesu i błędu (zostaną utworzone po konwersjach GUI).
7. Uruchom `py -m unittest discover -s tests -v`. Testy PDF wykonają się, jeśli LibreOffice jest zainstalowany.
8. Pokaż, że stare polecenie `py main.py przyklady/osoby.csv json` nadal działa i że stare pliki zostały zachowane.

## Na co zwrócić uwagę podczas obrony

- `konwertery.py` ma rejestr `REJESTR`, funkcję `dostepne_formaty()` oraz walidację `Zlecenie.sprawdz()`.
- `gui.py` tylko tworzy `Zlecenie`; **nie zawiera kodu konwersji formatów**.
- Wykonanie trwa w osobnym wątku (`threading.Thread`); komunikat do GUI jest przekazywany przez `queue.Queue`, a zmiany widgetów zachodzą w wątku głównym po `after()`.
- LibreOffice jest uruchamiany przez `subprocess.run()` bez `shell=True`, z kontrolą kodu zakończenia i sprawdzeniem wyniku.
- Błędny JSON to obsłużony `BladKonwersji`, a nie nieobsłużony wyjątek aplikacji.
- Każde uruchomienie na GUI jest rejestrowane przez `usluga.wykonaj_z_logowaniem()`.
