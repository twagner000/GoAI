import unittest

import numpy as np

from match import Match

class TestMatch(unittest.TestCase):
    def setUp(self):
        self.board_size = 9
        self.min_for_move = 2
        self.match = Match(None, None, self.board_size, self.min_for_move)
    
    def test_init(self):
        self.assertIsInstance(self.match,Match)
        self.assertEqual(len(self.match._players), 2)
        self.assertEqual(self.match._board_size,self.board_size)
        self.assertEqual(self.match._min_for_move,self.min_for_move)
        self.assertIsNone(self.match._dragons)
        self.assertIsNone(self.match._board)
        self.assertIsNone(self.match._scores)

if __name__ == '__main__':
    unittest.main()
