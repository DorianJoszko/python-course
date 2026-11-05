# Studio jakości i wizualizacji danych

**Programowanie V — Projekt 2, laboratoria 6–7**

## Opis i cel projektu

Studio jakości i wizualizacji danych to aplikacja konsolowa napisana w Pythonie, służąca do wczytywania danych z plików CSV, oceny ich jakości, stosowania wybranych operacji czyszczenia oraz tworzenia wykresów. Projekt realizuje etapy dotyczące analizy i przetwarzania danych (laboratorium 6) oraz wizualizacji i korelacji (laboratorium 7).

Analiza wykonywana jest na dwóch niezależnych wersjach zbioru: oryginalnej (`raw`) i roboczej (`current`). Pozwala to porównywać stan danych przed czyszczeniem i po nim bez nadpisywania oryginału.

Obecna wersja wykorzystuje interfejs wiersza poleceń. Interfejs graficzny przewidziany w dalszych etapach Projektu 2 (laboratoria 8–9) nie jest częścią tej wersji.

## Wymagania techniczne

- Python 3.10 lub nowszy;
- biblioteki: `pandas`, `numpy`, `matplotlib`, `seaborn`, `pytest`;
- system Windows, Linux lub macOS z obsługiwanym środowiskiem Pythona;
- plik wejściowy CSV z nagłówkami kolumn.

Wersje bibliotek określono w pliku `requirements.txt`. Wykorzystanie projektu nie wymaga dostępu do internetu po zainstalowaniu zależności.

## Instalacja

W terminalu otwartym w głównym katalogu projektu:

```powershell
python -m pip install -r requirements.txt
```

Opcjonalnie można utworzyć osobne środowisko wirtualne:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

## Uruchamianie

Podstawowe uruchomienie z dołączonym zbiorem California Housing:

```powershell
python main.py
```

Wskazanie własnej ścieżki wejściowej i katalogu wynikowego:

```powershell
python main.py --input data/california_housing_z_problemami.csv --output wyniki
```

Dostępne argumenty:

| Argument | Znaczenie | Wartość domyślna |
| --- | --- | --- |
| `--input` | Ścieżka do pliku CSV | `data/california_housing_z_problemami.csv` |
| `--output` | Katalog zapisu raportów i wykresów | `wyniki` |

Program wypisuje w terminalu profil danych przed przetwarzaniem i po nim, raport wykonanych operacji oraz komunikaty o zapisanych wykresach.

## Funkcjonalności — laboratorium 6

### Import i profilowanie

- wczytywanie danych CSV z obsługą separatorów `,` i `;`;
- podstawowa obsługa błędów odczytu;
- liczba wierszy i kolumn, typy danych, liczba wartości unikalnych;
- liczba i procent brakujących wartości;
- statystyki opisowe oraz identyfikacja pełnych duplikatów;
- porównanie danych przed czyszczeniem i po nim.

### Czyszczenie danych

Przykładowy przebieg dla dołączonego zbioru California Housing:

1. Usunięcie pełnych, powtarzających się rekordów.
2. Kontrola `HouseAge` w zakresie od 0 do 52; wartości spoza tego przedziału są zamieniane na braki.
3. Kontrola `MedInc` w zakresie od 0 do 20; potencjalne naruszenia są oznaczane dodatkową kolumną.
4. Uzupełnienie brakujących wartości `MedInc` i `HouseAge` medianą.
5. Uzupełnienie brakujących wartości `Region` dominantą (modą).
6. Wykrycie wartości odstających w `AveRooms` metodą IQR i oznaczenie ich w dodatkowej kolumnie logicznej.
7. Zapis przetworzonego zbioru oraz raportów profilowania i zmian.

Klasa `DataSession` zawiera również operacje: `drop_missing()`, `fill_missing()`, `apply_range()`, `handle_outliers()` i `reset()`. Dostępne strategie obejmują m.in. usuwanie braków, uzupełnianie średnią, medianą lub dominantą oraz oznaczanie, ograniczanie lub usuwanie wybranych obserwacji.

Zmiany danych roboczych rejestrowane są w dzienniku operacji (`audit_log`) zawierającym czas, nazwę operacji, liczbę rekordów przed zmianą i po niej, liczbę rekordów objętych operacją oraz parametry.

## Funkcjonalności — laboratorium 7

Moduł wizualizacji wykorzystuje Matplotlib i Seaborn. Dostępne są cztery typy wykresów:

| Wykres | Zastosowanie |
| --- | --- |
| Histogram (`histogram`) | Rozkład wartości w kolumnie liczbowej |
| Punktowy (`scatter`) | Zależność dwóch zmiennych liczbowych |
| Pudełkowy (`box`) | Rozkład, kwartyle i obserwacje odstające |
| Słupkowy (`bar`) | Liczebności kategorii, do 15 najczęstszych wartości |

Funkcja `make_figure()` sprawdza poprawność doboru kolumn, w tym ich istnienie i typ danych. Każdy z czterech wykresów generowany jest dla danych oryginalnych i roboczych, co daje osiem podstawowych wykresów w dwóch formatach: PNG oraz PDF.

Moduł wyznacza również macierze korelacji Pearsona dla odpowiednich kolumn liczbowych i zapisuje wizualizacje korelacji w formacie PNG. Korelacja opisuje zależność liniową i sama w sobie nie świadczy o związku przyczynowo-skutkowym.

## Struktura projektu

```text
Lab6_Lab7_Studio_Danych/
├── main.py                       # Punkt wejścia i przebieg analizy
├── requirements.txt              # Zależności środowiska
├── README.md                     # Dokumentacja projektu
├── RAPORT_TESTOW.md              # Opis i wyniki testów
├── WNIOSKI_LAB7.md               # Analiza wyników wizualizacji
├── studio/
│   ├── __init__.py
│   ├── session.py                 # Profilowanie, czyszczenie, eksport i audit_log
│   └── plots.py                   # Wykresy i korelacje
├── tests/
│   └── test_project.py           # Testy automatyczne
├── data/                          # Zbiór referencyjny i 6 małych plików testowych
└── wyniki/                        # Rezultaty generowane podczas uruchomienia
```

## Pliki wynikowe

Po uruchomieniu analizy w katalogu `wyniki/` zapisywane są:

- `cleaned.csv` — oczyszczone dane;
- `profil_przed.csv`, `profil_po.csv` — zestawienia jakości danych;
- `profil_przed_statystyki.csv`, `profil_po_statystyki.csv` — statystyki opisowe;
- `raport_zmian.csv` — historia operacji;
- `podsumowanie.txt` — podsumowanie analizy;
- `histogram_raw.*`, `histogram_current.*` — histogramy PNG/PDF;
- `scatter_raw.*`, `scatter_current.*` — wykresy punktowe PNG/PDF;
- `box_raw.*`, `box_current.*` — wykresy pudełkowe PNG/PDF;
- `bar_raw.*`, `bar_current.*` — wykresy słupkowe PNG/PDF;
- `korelacja_raw.csv`, `korelacja_current.csv` — macierze korelacji;
- `korelacja_raw.png`, `korelacja_current.png` — mapy korelacji.

## Testowanie

Automatyczne testy jednostkowe:

```powershell
python -m unittest discover -s tests -v
```

Alternatywnie:

```powershell
python -m pytest -q
```

Zestaw obejmuje dziewięć testów automatycznych. Dodatkowe dane kontrolne znajdują się w folderze `data/` (`test_01`–`test_06`), a opis testów i oczekiwanych zachowań w pliku `RAPORT_TESTOW.md`.

## Znane ograniczenia

- Automatyczna sekwencja w `main.py` została przygotowana dla schematu California Housing. W przypadku innego zestawu kolumn reguły czyszczenia i konfiguracja wykresów mogą wymagać dostosowania.
- Odczyt CSV korzysta z kodowania UTF-8 i obsługuje separatory przecinek oraz średnik.
- Reguła zakresu `HouseAge` od 0 do 52 dotyczy danych referencyjnych, a nie wszystkich możliwych zbiorów.
- Metoda IQR wskazuje obserwacje statystycznie odstające, które nie muszą być błędne. W domyślnej analizie są oznaczane, nie usuwane.
- Wykres słupkowy ogranicza liczbę kategorii do 15 najczęstszych.
- Wersja laboratoriów 6–7 nie zawiera jeszcze interfejsu graficznego.

## Autorstwo i wykorzystanie AI

Projekt opracowano w ramach przedmiotu Programowanie V jako rozwiązanie zadania dotyczącego analizy, czyszczenia i wizualizacji danych.

Wkład własny obejmował analizę wymagań projektowych, opracowanie założeń funkcjonalnych, rozwój i integrację poszczególnych elementów aplikacji, konfigurację środowiska programistycznego, uruchamianie i testowanie programu, weryfikację poprawności działania zaimplementowanych funkcji, analizę i interpretację uzyskanych wyników, formułowanie wniosków na podstawie przeprowadzonych analiz oraz przygotowanie dokumentacji projektowej.

W procesie tworzenia oprogramowania wykorzystano ChatGPT (OpenAI) jako narzędzie wspomagające projektowanie struktury aplikacji, przygotowywanie propozycji kodu źródłowego i testów, opracowywanie dokumentacji oraz rozwiązywanie problemów technicznych.

## Wykorzystane źródła i biblioteki

- Instrukcja projektowa „Programowanie V — Projekt 2: Studio jakości i wizualizacji danych”, materiały do laboratoriów 6–9.
- Dokument „Programowanie V — warunki prowadzenia przedmiotu i zasady zaliczenia”, 7 października 2026 r.
- [Pandas — dokumentacja](https://pandas.pydata.org/docs/)
- [NumPy — dokumentacja](https://numpy.org/doc/)
- [Matplotlib — dokumentacja](https://matplotlib.org/stable/)
- [Seaborn — dokumentacja](https://seaborn.pydata.org/)
- [Pytest — dokumentacja](https://docs.pytest.org/)
- [California Housing — scikit-learn](https://scikit-learn.org/stable/modules/generated/sklearn.datasets.fetch_california_housing.html)

Zbiór California Housing oraz sześć mniejszych zestawów testowych pochodzą z pakietu materiałów do Projektu 2. Dane referencyjne zawierają celowo wprowadzone błędy na potrzeby ćwiczeń.
