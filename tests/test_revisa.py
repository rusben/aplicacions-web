import unittest

import revisa


def question(attrs, options='', check=True, feedback=True):
    controls = '<button class="cq-check-btn">Comprova</button>' if check else ''
    result = '<div class="cq-feedback"></div>' if feedback else ''
    return (f'<div class="cq-question" {attrs}>'
            f'<div class="statement">Pregunta</div>{options}{controls}{result}</div>')


class QuizValidationTests(unittest.TestCase):
    def test_accepts_valid_single_and_multi_questions(self):
        single = question(
            'data-id="single" data-type="single"',
            '<button class="cq-option" data-correct="true">A</button>'
            '<button class="cq-option" data-correct="false">B</button>')
        multi = question(
            'data-id="multi" data-type="multi"',
            '<button class="cq-option" data-correct="true">A</button>'
            '<button class="cq-option" data-correct="true">B</button>')

        errors, ids = revisa.quiz_errors(single + multi)

        self.assertEqual(errors, [])
        self.assertEqual(ids, ['single', 'multi'])

    def test_rejects_missing_identity_type_and_options(self):
        errors, ids = revisa.quiz_errors(question('', ''))

        self.assertEqual(ids, [])
        self.assertIn('pregunta sense data-id: ?', errors)
        self.assertIn('pregunta ?: data-type invàlid o absent', errors)
        self.assertIn('pregunta ?: no té opcions', errors)

    def test_single_requires_exactly_one_correct_option(self):
        src = question(
            'data-id="doble" data-type="single"',
            '<button class="cq-option" data-correct="true">A</button>'
            '<button class="cq-option" data-correct="true">B</button>')

        errors, _ = revisa.quiz_errors(src)

        self.assertIn('pregunta doble: single amb 2 respostes correctes', errors)

    def test_multi_requires_a_correct_option_and_valid_option_metadata(self):
        src = question(
            'data-id="cap" data-type="multi"',
            '<button class="cq-option" data-correct="false">A</button>'
            '<button class="cq-option">B</button>')

        errors, _ = revisa.quiz_errors(src)

        self.assertIn('pregunta cap: opció 2 sense data-correct vàlid', errors)
        self.assertIn('pregunta cap: multi sense resposta correcta', errors)

    def test_requires_check_button_and_feedback(self):
        src = question(
            'data-id="controls" data-type="single"',
            '<button class="cq-option" data-correct="true">A</button>',
            check=False, feedback=False)

        errors, _ = revisa.quiz_errors(src)

        self.assertIn('pregunta controls: falta el botó de comprovació', errors)
        self.assertIn('pregunta controls: falta el feedback', errors)


if __name__ == '__main__':
    unittest.main()
