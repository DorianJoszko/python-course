# Lab. 7 — obserwacje i interpretacja

## Histogram `MedInc`

Przed czyszczeniem część wartości jest pusta, przez co histogram korzysta wyłącznie z dostępnych obserwacji. Po zastosowaniu mediany dostępne jest więcej pomiarów; w okolicach mediany pojawia się dodatkowa liczebność. Imputacja nie „odzyskuje” prawdziwych pomiarów, tylko zastępuje wartości brakujące przyjętą statystyką.

## Scatter `MedInc` — `MedHouseVal`

Wykres służy do badania współzmienności poziomu dochodu i mediany wartości domów. Można sprawdzić kierunek oraz siłę zależności poprzez macierz korelacji; **na podstawie wykresu lub współczynnika Pearsona nie wolno twierdzić, że jedna zmienna powoduje drugą**. Obydwie mogą zależeć od innych uwarunkowań, np. regionu i charakterystyki lokalnego rynku.

## Boxplot `AveRooms`

Występują wartości silnie odbiegające od większości rozkładu. Reguła IQR oznacza je flagą bez usuwania ani przycinania. Ta decyzja jest celowa: odstające wartości mogą być rzeczywiste, a wycięcie ich zniekształciłoby obraz danych.

## Barplot `Region`

Wykres pokazuje liczebność regionów. Po uzupełnieniu wartości brakujących najczęstszą kategorią („moda”) zmienia się udział kategorii dominującej; imputacja jest decyzją analityczną i może wpływać na proporcje.

## Korelacja

`korelacja_raw.csv` i `korelacja_current.csv` zawierają współczynniki Pearsona, które mieszczą się od −1 do 1. Dodatni oznacza dodatnią liniową współzmienność, ujemny — ujemną, a wartość bliska 0 — brak silnego związku **liniowego** (nie oznacza automatycznie całkowitego braku zależności). Kolumny stałe i nienumeryczne nie są analizowane.

## Ograniczenia interpretacji

Zbiór California Housing opisuje dane historyczne, a część wad jest sztucznie wprowadzona na potrzeby dydaktyczne. Te wykresy nie są aktualną oceną rynku nieruchomości. Wartość wykraczająca poza IQR nie jest automatycznie błędem pomiarowym.
