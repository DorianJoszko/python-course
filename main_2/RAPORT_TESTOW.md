# Raport testów — laboratoria 6–7

## Uruchomienie

`python -m unittest discover -s tests -v`

**Wynik lokalny:** 9 testów, wszystkie zakończone poprawnie (`OK`).

| Test | Oczekiwany rezultat | Status |
|---|---|---|
| `test_01_przecinek.csv` i `test_02_srednik.csv` | 3 wiersze × 3 kolumny, identyczne dane | OK |
| `test_03_braki_duplikaty.csv` | 1 pełny duplikat; po usunięciu 4 wiersze | OK |
| Braki liczbowe i tekstowe | Uzupełnienie 1 wartości liczbowej medianą i 1 tekstowej modą | OK |
| Reset | Powrót do niezmienionej kopii 5 wierszy | OK |
| Usuwanie braków w kolumnie `value` | Usunięte 2 wiersze | OK |
| `test_04_zakres_outlier.csv` | Wykrycie 1 wieku poza zakresem 0–52 i 1 outliera `AveRooms` | OK |
| `test_05_bledne_wiersze.csv` | Kontrolowany `ValueError`, bez cichego pominięcia rekordu | OK |
| `test_06_stala_tekst.csv` / ramka testowa | Stała kolumna i nienumeryczna kolumna odrzucone przy wykresach liczbowych | OK (ramka testowa) |
| Cztery wykresy | Każdy prawidłowo zapisuje PNG | OK |
| Korelacja | Macierz jest symetryczna, diagonalne wartości 1; kolumna stała wykluczona | OK |
| Eksport/ponowny import CSV | Ponownie wczytana ramka danych jest identyczna | OK |

## Wynik na dostarczonym California Housing

- Wiersze surowe: **20670**; po usunięciu duplikatów: **20640**.
- Pełne duplikaty: **30**.
- Braki `MedInc`: **80**, uzupełnione medianą.
- Braki `Region`: **40**, uzupełnione modą.
- Wartości `HouseAge` spoza demonstracyjnego zakresu 0–52: **40**, zastąpione brakami, potem medianą.
- IQR `AveRooms`: **553** oznaczonych obserwacji, **bez ich usuwania**.
- `MedInc` poza zakresem 0–20: **0**, reguła została jednak wykonana i zapisana w audycie.
- 8 wykresów porównawczych zapisano do PNG oraz PDF; 2 heatmapy korelacji do PNG.

**Uwaga:** „rekordy dotknięte” to liczba trafień danej operacji, a nie liczba unikalnych rekordów dotkniętych przez wszystkie operacje łącznie. Nie należy sumować tych wartości jako liczby różnych wierszy.

## Obserwacja metodologiczna

Część wykrytych przez IQR wartości odstających może pochodzić z rzeczywistych obserwacji i nie powinna być automatycznie usuwana. Dlatego projekt oznacza je kolumną `AveRooms_outlier_IQR`. Sprawdzane są osobno reguły biznesowe (zakres wieku) i statystyczne (IQR).

## Zakres testów

Testy wykonują się bez otwierania GUI, ponieważ interfejs jest przewidziany dopiero w laboratoriach 8–9. Pliki wynikowe zostały wygenerowane w środowisku Python i są dołączone do paczki.
