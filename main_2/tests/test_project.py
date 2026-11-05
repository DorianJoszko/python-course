import tempfile
import unittest
from pathlib import Path

import pandas as pd
from studio.session import DataSession
from studio.plots import make_figure, correlation_table

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / 'data'


class TestLab6(unittest.TestCase):
    def test_separators(self):
        a = DataSession.from_csv(DATA / 'test_01_przecinek.csv')
        b = DataSession.from_csv(DATA / 'test_02_srednik.csv')
        self.assertEqual(a.raw.shape, (3, 3))
        pd.testing.assert_frame_equal(a.raw, b.raw)

    def test_bad_row(self):
        with self.assertRaisesRegex(ValueError, 'wiersz'):
            DataSession.from_csv(DATA / 'test_05_bledne_wiersze.csv')

    def test_missing_duplicates(self):
        s = DataSession.from_csv(DATA / 'test_03_braki_duplikaty.csv')
        self.assertEqual(s.profile()['duplikaty_pelne'], 1)
        self.assertEqual(s.drop_exact_duplicates(), 1)
        self.assertEqual(s.fill_missing('value', 'median'), 1)
        self.assertEqual(s.fill_missing('group', 'mode'), 1)
        self.assertEqual(len(s.current), 4)
        self.assertEqual(s.current.isna().sum().sum(), 0)
        self.assertEqual(s.audit_log[0]['rekordy_dotkniete'], 1)
        self.assertTrue(s.raw.isna().any().any())
        s.reset()
        self.assertEqual(len(s.current), 5)

    def test_drop_missing(self):
        s = DataSession.from_csv(DATA / 'test_03_braki_duplikaty.csv')
        self.assertEqual(s.drop_missing(['value']), 2)
        self.assertEqual(len(s.current), 3)

    def test_range_and_outliers(self):
        s = DataSession.from_csv(DATA / 'test_04_zakres_outlier.csv')
        original_rooms = s.current['AveRooms'].copy()
        self.assertEqual(s.range_mask('HouseAge', 0, 52).sum(), 1)
        self.assertEqual(s.apply_range('HouseAge', 0, 52, 'nan'), 1)
        self.assertEqual(s.current.HouseAge.isna().sum(), 1)
        self.assertEqual(s.handle_outliers('AveRooms', 1.5, 'mark'), 1)
        self.assertEqual(s.current['AveRooms_outlier_IQR'].sum(), 1)
        pd.testing.assert_series_equal(s.current['AveRooms'], original_rooms)
        with self.assertRaises(ValueError):
            s.apply_range('HouseAge', 10, 0)

    def test_export_reload(self):
        s = DataSession.from_csv(DATA / 'test_03_braki_duplikaty.csv')
        s.drop_exact_duplicates()
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / 'cleaned.csv'
            s.export_csv(output)
            reloaded = DataSession.from_csv(output)
            pd.testing.assert_frame_equal(s.current.reset_index(drop=True), reloaded.current)
            s.export_report(tmp)
            self.assertTrue((Path(tmp) / 'raport_zmian.csv').is_file())


class TestLab7(unittest.TestCase):
    def setUp(self):
        self.s = DataSession(pd.DataFrame({'number': [1, 2, 3, 4, 5, 6], 'y': [3, 1, 4, 2, 7, 6], 'cat': ['A', 'B', 'A', 'C', 'B', 'A'], 'constant': [5]*6}))

    def test_four_plots_and_export(self):
        for kind, x, y in [('histogram', 'number', None), ('scatter', 'number', 'y'), ('box', 'number', None), ('bar', 'cat', None)]:
            fig = make_figure(self.s, kind, x, y)
            with tempfile.TemporaryDirectory() as tmp:
                file = Path(tmp) / f'{kind}.png'
                fig.savefig(file)
                self.assertGreater(file.stat().st_size, 500)

    def test_reject_text_and_constant(self):
        for kind, x in [('histogram', 'cat'), ('box', 'cat'), ('histogram', 'constant')]:
            with self.assertRaises(ValueError):
                make_figure(self.s, kind, x)
        with self.assertRaises(ValueError):
            make_figure(self.s, 'scatter', 'number', 'cat')

    def test_correlation(self):
        corr = correlation_table(self.s)
        self.assertIn('number', corr)
        self.assertNotIn('constant', corr)
        self.assertAlmostEqual(corr.loc['number','number'], 1)


if __name__ == '__main__':
    unittest.main()
