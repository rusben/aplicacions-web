import pathlib
import unittest

import aplica


class ReferenceTests(unittest.TestCase):
    def test_links_multi_digit_references_and_preserves_protected_ones(self):
        source = (
            '<div class="cq-block"><p>T6.10 A1.10 G5.12 RA10 '
            '<code>T6.10</code> <a href="fet.html">A1.10</a></p>\n</div>')
        mapping = {
            'T6.10': 'RA6/teoria/t6-10.html',
            'A1.10': 'RA1/activitats/a1-10.html',
            'G5.12': 'RA5/guies/g5-12.html',
            'RA10': 'RA10/index.html',
        }

        updated = aplica.enllaça(source, mapping, 'G5.12', pathlib.Path('/tmp'))

        self.assertEqual(updated.count('class="cq-ref"'), 3)
        self.assertIn('<code>T6.10</code>', updated)
        self.assertIn('<a href="fet.html">A1.10</a>', updated)
        self.assertIn(' G5.12 ', updated)


if __name__ == '__main__':
    unittest.main()
