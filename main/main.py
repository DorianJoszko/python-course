"""Uruchomienie konwertera w terminalu (bez GUI - laboratoria 2 i 3)."""

import argparse
from pathlib import Path
from konwertery import BladKonwersji, REJESTR, Zlecenie, wykonaj


def main() -> None:
    parser = argparse.ArgumentParser(description="Konwerter plików - laboratoria 2 i 3")
    parser.add_argument("plik", nargs="?", help="Ścieżka do pliku wejściowego")
    parser.add_argument("format", nargs="?", help="Format wynikowy, np. json, csv, docx, txt, pdf")
    parser.add_argument("-o", "--output", default="wyniki", help="Katalog wynikowy (domyślnie: wyniki)")
    parser.add_argument("--lista", action="store_true", help="Pokaż obsługiwane konwersje")
    argumenty = parser.parse_args()

    if argumenty.lista:
        print("Obsługiwane konwersje:")
        for zrodlo, cel in sorted(REJESTR):
            print(f"  {zrodlo} -> {cel}")
        return

    if not argumenty.plik or not argumenty.format:
        parser.error("Podaj plik i format. Przykład: python main.py przyklady/osoby.csv json")

    zrodlo = Path(argumenty.plik)
    cel = "." + argumenty.format.lower().lstrip(".")
    katalog = Path(argumenty.output)
    try:
        katalog.mkdir(parents=True, exist_ok=True)
        wynik = wykonaj(Zlecenie(zrodlo, cel, katalog))
        print(f"OK: zapisano plik {wynik.resolve()}")
    except (BladKonwersji, OSError) as blad:
        parser.exit(1, f"BŁĄD: {blad}\n")


if __name__ == "__main__":
    main()
