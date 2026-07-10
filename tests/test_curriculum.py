import unittest
import xml.etree.ElementTree as ET

from backend.content import curriculum


class CurriculumIntegrityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = curriculum()

    def test_every_lesson_has_a_unique_quiz(self):
        lessons = self.data["lessons"]
        quizzes = self.data["quizzes"]
        self.assertEqual(len(lessons), 22)
        self.assertEqual(len(quizzes), len(lessons))
        self.assertEqual({quiz["lesson_id"] for quiz in quizzes}, {lesson["id"] for lesson in lessons})
        self.assertEqual(len({quiz["id"] for quiz in quizzes}), len(quizzes))

    def test_quiz_questions_are_well_formed_and_not_position_biased(self):
        answer_positions = set()
        for quiz in self.data["quizzes"]:
            self.assertGreaterEqual(len(quiz["questions"]), 3, quiz["id"])
            for question in quiz["questions"]:
                self.assertGreaterEqual(len(question["options"]), 3)
                self.assertIn(question["answer"], range(len(question["options"])))
                self.assertTrue(question["explain"].strip())
                answer_positions.add(question["answer"])
        self.assertGreaterEqual(len(answer_positions), 3)

    def test_all_mathml_is_parseable_and_explained(self):
        math_items = [item for lesson in self.data["lessons"] for item in lesson.get("math", [])]
        self.assertGreaterEqual(len(math_items), 29)
        for item in math_items:
            with self.subTest(formula=item["name"]):
                ET.fromstring(item["mathml"])
                self.assertTrue(item["latex"].strip())
                self.assertGreaterEqual(len(item["explain"].strip()), 12)
                self.assertTrue(item["validity"].strip())
                self.assertTrue(item["detail"]["symbols"])
                self.assertTrue(item["detail"]["steps"])
                self.assertTrue(item["detail"]["pitfalls"])

    def test_every_code_line_has_an_explanation(self):
        for lesson in self.data["lessons"]:
            explanation = lesson["code_explanation"]
            with self.subTest(lesson=lesson["id"]):
                self.assertTrue(explanation["purpose"].strip())
                self.assertTrue(explanation["execution_order"])
                self.assertEqual(len(explanation["line_notes"]), len(lesson["code"].splitlines()))
                self.assertTrue(all(len(item["explain"].strip()) >= 12 for item in explanation["line_notes"]))

    def test_practice_studios_cover_every_lesson(self):
        studios = self.data["practice_studios"]
        lesson_ids = {lesson["id"] for lesson in self.data["lessons"]}
        covered = {lesson_id for task in studios for lesson_id in task["lesson_ids"]}
        self.assertEqual(len({task["id"] for task in studios}), len(studios))
        self.assertEqual(covered, lesson_ids)
        for task in studios:
            self.assertTrue(task["starter_code"].strip())
            self.assertIn("_expect", task["test_code"])
            self.assertTrue(task["hints"])

    def test_official_material_metadata_is_explicit(self):
        for lesson in self.data["lessons"]:
            material = lesson["official_material"]
            with self.subTest(lesson=lesson["id"]):
                self.assertIn(material["kind"], {"slides-pdf", "lecture-trace", "schedule"})
                self.assertTrue(material["reader_url"] or material["url"])
                self.assertTrue(material["label"])


if __name__ == "__main__":
    unittest.main()
