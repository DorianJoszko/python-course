# Projekt 1 — Uniwersalny konwerter plików

**Przedmiot:** Programowanie V  
**Zakres:** laboratoria 2–5  
**Autor:** Dorian Joszko
**Grupa laboratoryjna:** L2

## 1. Cel projektu

Celem projektu jest opracowanie aplikacji desktopowej w języku Python, umożliwiającej konwersję plików między wybranymi formatami. Program udostępnia interfejs graficzny Tkinter/ttk, w którym można wskazać plik źródłowy, format docelowy i katalog zapisu. Aplikacja sprawdza poprawność zlecenia, wykonuje konwersję oraz informuje o jej wyniku. Logika konwersji jest oddzielona od interfejsu.

## 2. Wymagania

- Python 3.10 lub nowszy, z obsługą Tkinter/ttk.
- Biblioteka `python-docx`, wskazana w pliku `requirements.txt`.
- LibreOffice zainstalowany w systemie — wymagany wyłącznie do konwersji DOCX → PDF oraz ODT → PDF.
- System Windows 10/11 lub inne środowisko obsługujące Python, Tkinter i wymagane zależności.

## 3. Instalacja

Po rozpakowaniu projektu należy otworzyć terminal w katalogu zawierającym pliki `gui.py`, `main.py` i `requirements.txt` oraz zainstalować zależności:

```powershell
py -m pip install -r requirements.txt
```

LibreOffice jest instalowany osobno, z oficjalnej strony: https://www.libreoffice.org/download/download-libreoffice/ . Program automatycznie wyszukuje LibreOffice w standardowych lokalizacjach systemowych. W przypadku instalacji niestandardowej ścieżkę można wskazać zmienną środowiskową (przykład dla PowerShell):

```powershell
$env:LIBREOFFICE_PATH = 'C:\Program Files\LibreOffice\program\soffice.exe'
```

## 4. Uruchomienie

Aplikacja z interfejsem graficznym:

```powershell
py gui.py
```

Na Windows dostępny jest również plik `uruchom_gui.bat`.

Po uruchomieniu okna użytkownik wybiera plik wejściowy, katalog wynikowy oraz format docelowy z listy dostępnych konwersji, a następnie uruchamia operację przyciskiem **Konwertuj plik**. Domyślnym katalogiem zapisu jest `wyniki`.

Projekt zachowuje również wersję konsolową:

```powershell
py main.py --lista
py main.py przyklady/osoby.csv json
py main.py przyklady/dokument.docx pdf
```

Opcja `-o` umożliwia określenie innego folderu zapisu, np. `py main.py przyklady/osoby.csv json -o dokumenty`.

## 5. Obsługiwane funkcje

| Format wejściowy | Format wynikowy | Sposób konwersji |
|---|---|---|
| CSV | JSON | Biblioteki `csv` i `json` |
| JSON | CSV | Biblioteki `json` i `csv` |
| TXT | DOCX | `python-docx` |
| DOCX | TXT | `python-docx` |
| DOCX | PDF | LibreOffice w trybie bez interfejsu |
| ODT | PDF | LibreOffice w trybie bez interfejsu |

Dodatkowe funkcje aplikacji obejmują wybór pliku i katalogu, automatyczne ograniczenie listy formatów do obsługiwanych par, walidację danych, komunikaty sukcesu i błędów, wykonywanie konwersji w osobnym wątku, zapisywanie informacji o operacjach w `logs/konwerter.log` oraz ochronę przed nadpisaniem plików przez dodawanie numeru do nazwy wyniku (np. `_1`, `_2`).

Konwersje CSV/JSON zachowują kolejność nagłówków, dane tekstowe oraz polskie znaki. Przyjęto CSV z przecinkiem jako separatorem i nagłówkami w pierwszym wierszu. Akceptowany JSON ma postać obiektu zawierającego `columns` (lista unikalnych nagłówków) i `rows` (lista rekordów z wartościami tekstowymi). Dane wejściowe CSV, JSON i TXT są odczytywane jako UTF-8, z obsługą BOM.

Przykładowe pliki wejściowe znajdują się w katalogu `przyklady`. Testy automatyczne można uruchomić poleceniem:

```powershell
py -m unittest discover -s tests -v
```

Szczegóły weryfikacji opisano w `RAPORT_TESTOW.md`.

## 6. Znane ograniczenia

- Obsługiwanych jest sześć wskazanych kierunków konwersji; nie wszystkie kombinacje formatów są dostępne.
- Konwersja DOCX → TXT przenosi tekst akapitów, ale nie zachowuje tabel, obrazów ani formatowania.
- Konwersja TXT → DOCX przenosi linie tekstu do akapitów, bez odtwarzania zaawansowanego formatowania.
- Wygląd wynikowych plików PDF zależy od LibreOffice i czcionek zainstalowanych w systemie.
- Konwersje do PDF nie są dostępne bez zainstalowanego LibreOffice.
- Dane JSON muszą być zgodne z przyjętym schematem `columns` / `rows`; program nie obsługuje dowolnych struktur JSON.

## 7. Autorzy i wykorzystane narzędzia

**Autor projektu:** Dorian Joszko 
**Technologie i biblioteki:** Python, Tkinter/ttk, `python-docx`, standardowe biblioteki Pythona, LibreOffice.

W pracach wykorzystano **ChatGPT (OpenAI)** jako narzędzie wspomagające tworzenie i rozwijanie kodu, przygotowanie interfejsu, opracowanie testów, analizę błędów oraz redakcję dokumentacji. Narzędzie nie stanowi odrębnego autora projektu; zakres jego użycia został wskazany zgodnie z zasadami przedmiotu.

Źródła techniczne:

- Dokumentacja Python: https://docs.python.org/3/
- Dokumentacja `python-docx`: https://python-docx.readthedocs.io/
- Dokumentacja LibreOffice: https://help.libreoffice.org/
- Instrukcja przedmiotu „Projekt 1. Uniwersalny konwerter plików” oraz „Warunki prowadzenia przedmiotu i zasady zaliczenia”, 7.10.2026.
