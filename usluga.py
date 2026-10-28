"""Warstwa aplikacyjna: logowanie i pomiar czasu bez zmian w konwerterach z lab. 2–3."""

import logging
import time
from pathlib import Path

from konwertery import Zlecenie, wykonaj

LOGGER = logging.getLogger("konwerter")


def skonfiguruj_logi(plik: Path | None = None) -> Path:
    """Konfiguruje dziennik konwersji w pliku logs/konwerter.log.

    Wywołanie jest idempotentne: nie powoduje wielokrotnego zapisu tej samej linii.
    """
    if plik is None:
        plik = Path(__file__).resolve().parent / "logs" / "konwerter.log"
    plik = plik.resolve()
    plik.parent.mkdir(parents=True, exist_ok=True)

    for handler in LOGGER.handlers:
        if isinstance(handler, logging.FileHandler) and Path(handler.baseFilename) == plik:
            return plik

    handler = logging.FileHandler(plik, encoding="utf-8")
    handler.setFormatter(logging.Formatter("%(asctime)s | %(levelname)s | %(message)s"))
    LOGGER.addHandler(handler)
    LOGGER.setLevel(logging.INFO)
    return plik


def wykonaj_z_logowaniem(zlecenie: Zlecenie) -> Path:
    """Deleguje do starego silnika; zapisuje sukces i wyjątki w dzienniku."""
    poczatek = time.perf_counter()
    LOGGER.info(
        "START | plik=%s | format=%s | katalog=%s",
        zlecenie.plik, zlecenie.format_docelowy, zlecenie.katalog,
    )
    try:
        wynik = wykonaj(zlecenie)
    except Exception:
        LOGGER.exception(
            "BŁĄD | plik=%s | po=%.2fs", zlecenie.plik,
            time.perf_counter() - poczatek,
        )
        raise
    LOGGER.info("SUKCES | wynik=%s | czas=%.2fs", wynik, time.perf_counter() - poczatek)
    return wynik
