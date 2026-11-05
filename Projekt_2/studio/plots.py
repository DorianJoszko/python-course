"""Wykresy i analiza korelacji (laboratorium 7). Funkcje zwracają Figure."""
from __future__ import annotations

import pandas as pd
import seaborn as sns
from matplotlib.figure import Figure
from .session import DataSession


def make_figure(session: DataSession, kind: str, x: str, y: str | None = None,
                source: str = 'current', title: str | None = None) -> Figure:
    """Rodzaje: histogram, scatter, box, bar; źródło: raw/current."""
    frame = session._source(source)
    if kind not in ('histogram', 'scatter', 'box', 'bar'):
        raise ValueError('Rodzaj wykresu: histogram, scatter, box, bar.')
    if x not in frame.columns:
        raise ValueError(f'Nie istnieje kolumna {x!r}.')
    if kind == 'scatter' and (not y or y not in frame.columns):
        raise ValueError('Scatter wymaga istniejącej kolumny Y.')
    fig = Figure(figsize=(8, 5), dpi=110)
    ax = fig.add_subplot(111)
    if kind in ('histogram', 'scatter', 'box'):
        cols = [x, y] if kind == 'scatter' else [x]
        for col in cols:
            if not pd.api.types.is_numeric_dtype(frame[col]):
                raise ValueError(f'Wykres {kind} wymaga kolumn liczbowych: {col}.')
            valid = pd.to_numeric(frame[col], errors='coerce').dropna()
            if valid.empty:
                raise ValueError(f'Brak wartości liczbowych w kolumnie {col}.')
            if valid.nunique() < 2:
                raise ValueError(f'Kolumna {col} jest stała; wybierz zmienną o różnych wartościach.')
    if kind == 'histogram':
        sns.histplot(frame[x].dropna(), bins=30, ax=ax, color='#2563eb')
        ax.set(xlabel=x, ylabel='Liczba rekordów')
    elif kind == 'scatter':
        points = frame[[x, y]].dropna()
        if points.empty:
            raise ValueError('Brak kompletnych par obserwacji X/Y.')
        sns.scatterplot(data=points, x=x, y=y, ax=ax, s=15, alpha=.45)
        ax.set(xlabel=x, ylabel=y)
    elif kind == 'box':
        sns.boxplot(y=frame[x], ax=ax, color='#93c5fd')
        ax.set(xlabel='Rozkład wartości', ylabel=x)
    else:
        valid = frame[x].dropna()
        if valid.empty:
            raise ValueError('Kolumna słupkowa jest pusta.')
        counts = valid.astype(str).value_counts().head(15)
        sns.barplot(x=counts.index, y=counts.values, ax=ax, color='#2563eb')
        ax.set(xlabel=x, ylabel='Liczba rekordów')
        ax.tick_params(axis='x', rotation=35)
    ax.set_title(title or f'{kind.capitalize()}: {x}' + (f' vs {y}' if y else '') + f' ({source})')
    ax.grid(axis='y', alpha=.18)
    fig.tight_layout()
    return fig


def correlation_table(session: DataSession, source: str = 'current') -> pd.DataFrame:
    """Pearson: liniowy współczynnik współzmienności, NIE dowód przyczynowości."""
    numeric = session._source(source).select_dtypes(include='number')
    numeric = numeric.loc[:, numeric.nunique(dropna=True) > 1]
    if numeric.shape[1] < 2:
        raise ValueError('Do korelacji potrzebne są dwie niestałe kolumny liczbowe.')
    return numeric.corr(method='pearson')


def correlation_figure(session: DataSession, source: str = 'current') -> Figure:
    corr = correlation_table(session, source)
    fig = Figure(figsize=(9, 7), dpi=110)
    ax = fig.add_subplot(111)
    sns.heatmap(corr, annot=True, fmt='.2f', cmap='coolwarm', center=0, vmin=-1, vmax=1, ax=ax)
    ax.set_title(f'Korelacje Pearsona ({source}) — nie oznaczają przyczynowości')
    fig.tight_layout()
    return fig
