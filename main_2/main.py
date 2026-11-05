"""Uruchom: python main.py --input data/california_housing_z_problemami.csv"""
from __future__ import annotations

import argparse
from pathlib import Path
import pandas as pd

from studio.session import DataSession
from studio.plots import make_figure, correlation_table, correlation_figure


def run(input_path: Path, out_dir: Path) -> DataSession:
    out_dir.mkdir(parents=True, exist_ok=True)
    session = DataSession.from_csv(input_path)
    print(f'Wczytano {len(session.raw)} rekordów i {len(session.raw.columns)} kolumn.')
    print('Profil PRZED:')
    print(session.profile('raw')['kolumny'].to_string())

    # LAB 6: jawna, zachowawcza polityka jakości. Najpierw wykrywanie/naprawa,
    # następnie imputacja. Kolumny niewskazane przez reguły pozostają nietknięte.
    session.drop_exact_duplicates()
    if 'HouseAge' in session.current:
        session.apply_range('HouseAge', 0, 52, 'nan')
    if 'MedInc' in session.current:
        session.apply_range('MedInc', 0, 20, 'mark')
    for col in ['MedInc', 'HouseAge']:
        if col in session.current and session.current[col].isna().any():
            session.fill_missing(col, 'median')
    if 'Region' in session.current and session.current['Region'].isna().any():
        session.fill_missing('Region', 'mode')
    if 'AveRooms' in session.current:
        session.handle_outliers('AveRooms', 1.5, 'mark')

    session.export_csv(out_dir / 'cleaned.csv')
    session.export_report(out_dir)
    print('\nProfil PO:')
    print(session.profile()['kolumny'].to_string())
    print('\nRaport operacji:')
    print(pd.DataFrame(session.audit_log).to_string(index=False))

    # LAB 7: przed/po oraz korelacje — walidacja następuje w make_figure.
    plans = [
        ('histogram', 'MedInc', None),
        ('scatter', 'MedInc', 'MedHouseVal'),
        ('box', 'AveRooms', None),
        ('bar', 'Region', None),
    ]
    for kind, x, y in plans:
        if x not in session.raw or (y and y not in session.raw):
            continue
        for source in ('raw', 'current'):
            fig = make_figure(session, kind, x, y, source=source)
            name = f'{kind}_{source}'
            fig.savefig(out_dir / f'{name}.png', dpi=160, bbox_inches='tight')
            fig.savefig(out_dir / f'{name}.pdf', bbox_inches='tight')
            print(f'Zapisano: {name}.png + .pdf')
    try:
        for source in ('raw', 'current'):
            correlation_table(session, source).to_csv(out_dir / f'korelacja_{source}.csv', encoding='utf-8-sig')
            correlation_figure(session, source).savefig(out_dir / f'korelacja_{source}.png', dpi=150, bbox_inches='tight')
    except ValueError as exc:
        print('Pominięto korelację:', exc)
    return session


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Laboratoria 6–7: profil, czyszczenie i wykresy danych CSV')
    parser.add_argument('--input', type=Path, default=Path('data/california_housing_z_problemami.csv'))
    parser.add_argument('--output', type=Path, default=Path('wyniki'))
    args = parser.parse_args()
    try:
        run(args.input, args.output)
    except (OSError, ValueError) as exc:
        parser.exit(1, f'Błąd: {exc}\n')
