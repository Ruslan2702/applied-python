from unittest import TestCase
from dirdict import DirDict

class DirDictTests(TestCase):
    def test_add(self):
        m = DirDict('/home/ruslan/temp/')
        self.assertEqual(0, len(m))
        self.assertFalse(m)
        m['F1'] = 'S1\n'
        self.assertEqual(1, len(m))
        self.assertEqual('S1\n', m['F1'])
        del m['F1']
        self.assertEqual(0, len(m))

    def test_del(self):
        m = DirDict('/home/ruslan/temp/')
        m['F1'] = 'S1\n'
        del m['F1']
        self.assertEqual(0, len(m))
        with self.assertRaises(KeyError):
            del m['F2']

    def test_len(self):
        m = DirDict('/home/ruslan/temp/')
        self.assertEqual(0, len(m))
        self.assertFalse(m)
        m['F1'] = 'S1\n'
        self.assertEqual(1, len(m))
        m['F2'] = 'S2\n'
        self.assertEqual(2, len(m))
        del m['F1']
        del m['F2']
        self.assertEqual(0, len(m))

    def test_items(self):
        m = DirDict('/home/ruslan/temp/')
        with self.assertRaises(KeyError):
            print(m['F2'])

