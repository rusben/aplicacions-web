import pathlib
import tempfile
import unittest

import aplica
import publica


class ExternalitzaWebTests(unittest.TestCase):
    def test_source_pages_get_a_main_landmark_before_the_script(self):
        source = ('<body><header class="cq-header"><h1>Prova</h1></header>'
                  '<div class="cq-block">Contingut</div><script>test</script></body>')

        updated = aplica.aplica_principal(source)

        self.assertEqual(updated.count('<main>'), 1)
        self.assertLess(updated.index('<main>'), updated.index('<header class="cq-header">'))
        self.assertLess(updated.index('</main>'), updated.index('<script>'))

    def test_has_canonical_quiz_asset(self):
        self.assertTrue(publica.QUIZ.is_file())
        self.assertIn('cq-question', publica.QUIZ.read_text(encoding='utf-8'))

    def test_generates_shared_assets_and_accessible_page(self):
        with tempfile.TemporaryDirectory() as temporary:
            docs = pathlib.Path(temporary)
            page = docs / 'RA1' / 'teoria' / 't1.html'
            page.parent.mkdir(parents=True)
            page.write_text(
                '<html><head><style>/* === SINAPSI-CSS INICI */x/* === SINAPSI-CSS FI */</style></head>'
                '<body><header class="cq-header"><h1>Prova</h1></header>'
                '<div class="cq-block">Contingut</div><script>console.log("test");</script></body></html>',
                encoding='utf-8')

            public = publica.externalitza_web(docs, '/* css compartit */', '/* js compartit */')

            exported = page.read_text(encoding='utf-8')
            self.assertEqual(public, 1)
            self.assertTrue((docs / '_identitat' / 'sinapsi.css').read_text(
                encoding='utf-8').endswith('/* css compartit */'))
            self.assertEqual((docs / '_identitat' / 'quiz.js').read_text(encoding='utf-8'),
                             '/* js compartit */')
            self.assertIn('href="../../_identitat/sinapsi.css"', exported)
            self.assertIn('src="../../_identitat/quiz.js"', exported)
            self.assertEqual(exported.count('<main>'), 1)
            self.assertNotIn('<style>', exported)
            self.assertNotIn('<script>console.log', exported)

    def test_copies_local_fonts_and_removes_google_font_links(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = pathlib.Path(temporary)
            docs = root / 'docs'
            fonts = root / 'fonts'
            docs.mkdir()
            fonts.mkdir()
            (fonts / 'ubuntu-500.ttf').write_bytes(b'font-local')
            page = docs / 'index.html'
            page.write_text(
                '<html><head>'
                '<link rel="preconnect" href="https://fonts.googleapis.com">'
                '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>'
                '<link href="https://fonts.googleapis.com/css2?family=Ubuntu" rel="stylesheet">'
                '<style>/* css */</style></head><body>'
                '<header class="cq-header"><h1>Prova</h1></header>'
                '<script>test</script></body></html>',
                encoding='utf-8')

            publica.externalitza_web(docs, '/* css */', '/* js */', fonts)

            exported = page.read_text(encoding='utf-8')
            css = (docs / '_identitat' / 'sinapsi.css').read_text(encoding='utf-8')
            self.assertEqual((docs / '_identitat' / 'fonts' / 'ubuntu-500.ttf').read_bytes(),
                             b'font-local')
            self.assertNotIn('fonts.googleapis.com', exported)
            self.assertNotIn('fonts.gstatic.com', exported)
            self.assertIn('url("fonts/ubuntu-500.ttf")', css)


if __name__ == '__main__':
    unittest.main()
