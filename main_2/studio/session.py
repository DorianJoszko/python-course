"""Model sesji i jawne operacje jakości danych (laboratorium 6)."""
from __future__ import annotations

import csv
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path

import numpy as np
import pandas as pd


@dataclass
class DataSession:
    raw: pd.DataFrame
    current: pd.DataFrame = field(init=False)
    audit_log: list[dict] = field(default_factory=list)

    def __post_init__(self) -> None:
        if self.raw.empty or self.raw.shape[1] == 0:
            raise ValueError('Zbiór nie zawiera rekordów lub kolumn.')
        self.raw = self.raw.copy(deep=True)
        self.current = self.raw.copy(deep=True)

    @classmethod
    def from_csv(cls, path: str | Path) -> 'DataSession':
        path = Path(path)
        if not path.is_file():
            raise FileNotFoundError(f'Brak pliku: {path}')
        try:
            with path.open('r', encoding='utf-8-sig', newline='') as handle:
                sample = handle.read(8192)
                if not sample.strip():
                    raise ValueError('Plik CSV jest pusty.')
                try:
                    delimiter = csv.Sniffer().sniff(sample, delimiters=',;').delimiter
                except csv.Error:
                    delimiter = ';' if sample.splitlines()[0].count(';') > sample.splitlines()[0].count(',') else ','
            df = pd.read_csv(path, sep=delimiter, encoding='utf-8-sig', on_bad_lines='error')
        except UnicodeError as exc:
            raise ValueError('Nieprawidłowe kodowanie CSV. Zapisz plik jako UTF-8.') from exc
        except pd.errors.ParserError as exc:
            raise ValueError(f'Niepoprawny wiersz CSV (liczba pól nie pasuje do nagłówka): {exc}') from exc
        except pd.errors.EmptyDataError as exc:
            raise ValueError('Plik CSV nie ma danych.') from exc
        if len(df.columns) == 1 and (',' in df.columns[0] or ';' in df.columns[0]):
            raise ValueError('Nie udało się poprawnie odczytać separatora CSV.')
        return cls(df)

    def _record(self, operation: str, before: int, affected: int, **params) -> int:
        self.audit_log.append({
            'czas': datetime.now().isoformat(timespec='seconds'),
            'operacja': operation,
            'rekordy_przed': int(before),
            'rekordy_po': int(len(self.current)),
            'rekordy_dotkniete': int(affected),
            'parametry': str(params),
        })
        return int(affected)

    def profile(self, source: str = 'current') -> dict:
        df = self._source(source)
        description = df.describe(include='all').transpose().replace({np.nan: None})
        summary = pd.DataFrame({
            'typ': df.dtypes.astype(str),
            'braki': df.isna().sum(),
            'braki_proc': (df.isna().mean() * 100).round(2),
            'unikalne': df.nunique(dropna=True),
        })
        return {
            'wiersze': len(df), 'kolumny': df.shape[1],
            'duplikaty_pelne': int(df.duplicated().sum()),
            'kolumny': summary,
            'statystyki': description,
        }

    def _source(self, source: str) -> pd.DataFrame:
        if source == 'raw':
            return self.raw
        if source == 'current':
            return self.current
        raise ValueError('Źródło musi być raw albo current.')

    def _column(self, column: str) -> None:
        if column not in self.current.columns:
            raise ValueError(f'Brak kolumny {column!r}. Dostępne: {list(self.current.columns)}')

    def numeric(self, column: str, source: str = 'current') -> pd.Series:
        df = self._source(source)
        if column not in df:
            raise ValueError(f'Nie istnieje kolumna: {column}')
        if not pd.api.types.is_numeric_dtype(df[column]):
            raise ValueError(f'Kolumna {column} nie jest liczbowa.')
        return pd.to_numeric(df[column], errors='coerce')

    def drop_exact_duplicates(self) -> int:
        before = len(self.current)
        duplicate_mask = self.current.duplicated()
        self.current = self.current.loc[~duplicate_mask].copy()
        return self._record('Usuwanie pełnych duplikatów', before, int(duplicate_mask.sum()))

    def range_mask(self, column: str, lower: float, upper: float) -> pd.Series:
        self._column(column)
        if not np.isfinite(lower) or not np.isfinite(upper) or lower > upper:
            raise ValueError('Zakres musi mieć skończone granice i dolna <= górna.')
        values = self.numeric(column)
        return values.notna() & ~values.between(lower, upper)

    def apply_range(self, column: str, lower: float, upper: float, strategy: str = 'mark') -> int:
        if strategy not in ('mark', 'nan', 'clip'):
            raise ValueError('Strategia zakresu: mark, nan lub clip.')
        mask = self.range_mask(column, lower, upper)
        before = len(self.current)
        if strategy == 'mark':
            self.current[f'{column}_poza_zakresem'] = mask
        elif strategy == 'nan':
            self.current.loc[mask, column] = np.nan
        elif strategy == 'clip':
            self.current[column] = self.numeric(column).clip(lower, upper)
        return self._record('Reguła zakresu', before, mask.sum(), kolumna=column,
                            minimum=lower, maksimum=upper, strategia=strategy)

    def fill_missing(self, column: str, strategy: str = 'median') -> int:
        self._column(column)
        if strategy not in ('median', 'mean', 'mode'):
            raise ValueError('Strategia braków: median, mean lub mode.')
        series = self.current[column]
        before = len(self.current)
        mask = series.isna()
        if not mask.any():
            return self._record('Uzupełnienie braków', before, 0, kolumna=column, strategia=strategy)
        if strategy in ('median', 'mean'):
            values = self.numeric(column)
            replacement = values.median() if strategy == 'median' else values.mean()
        else:
            modes = series.mode(dropna=True)
            replacement = modes.iloc[0] if not modes.empty else np.nan
        if pd.isna(replacement):
            raise ValueError(f'Nie można uzupełnić {column}: brak wartości do wyliczenia zastępstwa.')
        self.current.loc[mask, column] = replacement
        return self._record('Uzupełnienie braków', before, mask.sum(), kolumna=column,
                            strategia=strategy, wartosc=repr(replacement))

    def drop_missing(self, columns: list[str] | None = None) -> int:
        selected = columns if columns is not None else list(self.current.columns)
        if not selected:
            raise ValueError('Należy podać przynajmniej jedną kolumnę.')
        for col in selected:
            self._column(col)
        before = len(self.current)
        mask = self.current[selected].isna().any(axis=1)
        self.current = self.current.loc[~mask].copy()
        return self._record('Usuwanie wierszy z brakami', before, mask.sum(), kolumny=selected)

    def iqr_bounds(self, column: str, factor: float = 1.5) -> tuple[float, float] | None:
        if not np.isfinite(factor) or factor <= 0:
            raise ValueError('Współczynnik IQR musi być większy od zera.')
        values = self.numeric(column).dropna()
        if len(values) < 4:
            return None
        q1, q3 = values.quantile([0.25, 0.75])
        iqr = q3 - q1
        if not np.isfinite(iqr) or iqr == 0:
            return None
        return (float(q1 - factor * iqr), float(q3 + factor * iqr))

    def iqr_mask(self, column: str, factor: float = 1.5) -> pd.Series:
        bounds = self.iqr_bounds(column, factor)
        if bounds is None:
            return pd.Series(False, index=self.current.index, dtype=bool)
        values = self.numeric(column)
        return values.notna() & ~values.between(*bounds)

    def handle_outliers(self, column: str, factor: float = 1.5, strategy: str = 'mark') -> int:
        if strategy not in ('mark', 'clip', 'drop'):
            raise ValueError('Strategia odstających: mark, clip lub drop.')
        bounds = self.iqr_bounds(column, factor)
        mask = self.iqr_mask(column, factor)
        before = len(self.current)
        if strategy == 'mark':
            self.current[f'{column}_outlier_IQR'] = mask
        elif strategy == 'clip' and bounds is not None:
            self.current[column] = self.numeric(column).clip(*bounds)
        elif strategy == 'drop':
            self.current = self.current.loc[~mask].copy()
        return self._record('Outliery IQR', before, mask.sum(), kolumna=column,
                            factor=factor, progi=bounds, strategia=strategy)

    def reset(self) -> None:
        before = len(self.current)
        self.current = self.raw.copy(deep=True)
        self._record('Reset do danych surowych', before, len(self.raw))

    def export_csv(self, path: str | Path) -> None:
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        self.current.to_csv(path, index=False, encoding='utf-8-sig')

    def export_report(self, directory: str | Path) -> None:
        directory = Path(directory)
        directory.mkdir(parents=True, exist_ok=True)
        pd.DataFrame(self.audit_log, columns=['czas','operacja','rekordy_przed','rekordy_po','rekordy_dotkniete','parametry']).to_csv(directory / 'raport_zmian.csv', index=False, encoding='utf-8-sig')
        for source, name in [('raw', 'profil_przed'), ('current', 'profil_po')]:
            p = self.profile(source)
            p['kolumny'].to_csv(directory / f'{name}.csv', encoding='utf-8-sig')
            p['statystyki'].to_csv(directory / f'{name}_statystyki.csv', encoding='utf-8-sig')
        with (directory / 'podsumowanie.txt').open('w', encoding='utf-8') as f:
            for source in ('raw', 'current'):
                p = self.profile(source)
                f.write(f'{source}: wiersze={p["wiersze"]}, kolumny={p["kolumny"]}, pelne_duplikaty={p["duplikaty_pelne"]}\n')
            f.write('\nOperacje: kolejno w pliku raport_zmian.csv\n')
