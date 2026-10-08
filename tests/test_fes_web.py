import importlib
import unittest


fesweb = importlib.import_module('fes-web')


class AggregatePageTests(unittest.TestCase):
    def test_removes_page_navigation_and_main_landmark(self):
        body = ('<!-- === NAVEGACIÓ INICI === --><nav>barra</nav>'
                '<!-- === NAVEGACIÓ FI === -->\n<main><h1>Contingut</h1>'
                '<!-- === PEU DE NAVEGACIÓ INICI === --><nav>peu</nav>'
                '<!-- === PEU DE NAVEGACIÓ FI === -->\n</main>')

        cleaned = fesweb.neteja_cos(body)

        self.assertEqual(cleaned, '<h1>Contingut</h1>')
        self.assertNotIn('<main>', cleaned)
        self.assertNotIn('<nav>', cleaned)


if __name__ == '__main__':
    unittest.main()
