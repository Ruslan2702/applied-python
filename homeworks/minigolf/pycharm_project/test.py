import unittest

from golf import  Player, HitsMatch, HolesMatch


class PeopleCreatingTest(unittest.TestCase):
    def _test_init_people(self):
        people_list = [Player(i) for i in range(5)]
        names = [people_list[i].name for i in range(5)]
        self.assertEqual(names, ['0', '1', '2', '3', '4'])


class HitsMatchTestCase(unittest.TestCase):
    def setUp(self):
        self.people_list = [Player(i) for i in range(3)]
        self.match = HitsMatch(3, self.people_list)

    def test_hit(self):
        self.match.hit()  # 1
        self.match.hit()  # 2
        self.match.hit(True)  # 3
        self.match.hit(True)  # 1
        for _ in range(8):
            self.match.hit()  # 2
        self.assertFalse(self.match.finished)

        self.match.hit()  # 2
        for _ in range(3):
            self.match.hit(True)  # 3, 1, 2
        self.assertFalse(self.match.finished)

        self.match.hit()     # 3
        self.match.hit(True) # 1
        self.match.hit()     # 2
        self.match.hit(True) # 3
        self.match.hit()     # 2
        self.match.hit(True) # 2
        self.assertTrue(self.match.finished)

        with self.assertRaises(RuntimeError):
            self.match.hit()

    def test_get_winners(self):
        self.match.hit()  # 1
        self.match.hit()  # 2
        self.match.hit(True)  # 3
        self.match.hit(True)  # 1

        for _ in range(8):
            self.match.hit()  # 2

        self.match.hit()  # 2

        for _ in range(3):
            self.match.hit(True)  # 3, 1, 2

        with self.assertRaises(RuntimeError):
            self.match.get_winners()

        self.match.hit()     # 3
        self.match.hit(True) # 1
        self.match.hit()     # 2
        self.match.hit(True) # 3
        self.match.hit()     # 2
        self.match.hit(True) # 2
        self.assertEqual(self.match.get_winners(), [
            self.people_list[0], self.people_list[2]
        ])

    def test_get_table(self):
        self.match.hit()  # 1
        self.match.hit()  # 2
        self.match.hit(True)  # 3
        self.match.hit(True)  # 1
        for _ in range(8):
            self.match.hit()  # 2

        self.assertEqual(self.match.get_table(), [
            ('0', '1', '2'),
            (2, 10, 1),
            (None, None, None),
            (None, None, None),
        ])

        self.match.hit()  # 2
        for _ in range(3):
            self.match.hit(True)  # 3, 1, 2

        self.assertEqual(self.match.get_table(), [
            ('0', '1', '2'),
            (2, 10, 1),
            (1, 2, 1),
            (None, None, None),
        ])

        self.match.hit()  # 3
        self.match.hit(True)  # 1
        self.match.hit()  # 2
        self.assertEqual(self.match.get_table(), [
            ('0', '1', '2'),
            (2, 10, 1),
            (1, 2, 1),
            (1, None, None),
        ])
        self.match.hit(True)  # 3
        self.match.hit()  # 2
        self.match.hit(True)  # 2

        self.assertEqual(self.match.get_table(), [
            ('0', '1', '2'),
            (2, 10, 1),
            (1, 2, 1),
            (1, 3, 2),
        ])


class HolesMatchTestCase(unittest.TestCase):
    def setUp(self):
        self.people_list = [Player(i) for i in range(3)]
        self.match = HolesMatch(3, self.people_list)

    def test_hit(self):
        self.match.hit(True)  # 1
        self.match.hit()  # 2
        self.match.hit()  # 3

        self.assertFalse(self.match.finished)

        for i in range(10):
            for j in range(3):
                self.match.hit() # 2, 3, 1
        self.assertFalse(self.match.finished)

        for _ in range(9):
            for _ in range(3):
                self.match.hit() # 3, 1, 2

        self.match.hit(True) # 3
        self.match.hit(True) # 1
        self.match.hit()     # 2
        self.assertTrue(self.match.finished)

        with self.assertRaises(RuntimeError):
            self.match.hit()

    def test_get_winners(self):
        self.match.hit(True)  # 1
        self.match.hit()  # 2
        self.match.hit()  # 3

        for i in range(10):
            for j in range(3):
                self.match.hit()  # 2, 3, 1

        for _ in range(9):
            for _ in range(3):
                self.match.hit()  # 3, 1, 2

        self.match.hit(True)  # 3
        self.match.hit(True)  # 1
        self.match.hit()  # 2
        self.assertEqual(self.match.get_winners(), [self.people_list[0]])

    def test_get_table(self):
        self.match.hit(True)  # 1
        self.match.hit()  # 2
        self.match.hit()  # 3
        self.assertEqual(self.match.get_table(), [
            ('0', '1', '2'),
            (1, 0, 0),
            (None, None, None),
            (None, None, None),
        ])

        for i in range(10):
            for j in range(3):
                self.match.hit() # 2, 3, 1
        self.assertEqual(self.match.get_table(), [
            ('0', '1', '2'),
            (1, 0, 0),
            (0, 0, 0),
            (None, None, None),
        ])

        for _ in range(9):
            for _ in range(3):
                self.match.hit() # 3, 1, 2
        self.match.hit(True) # 3
        self.assertEqual(self.match.get_table(), [
            ('0', '1', '2'),
            (1, 0, 0),
            (0, 0, 0),
            (None, None, 1),
        ])



if __name__ == '__main__':
    unittest.main()