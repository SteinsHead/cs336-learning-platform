import tempfile
import unittest
from pathlib import Path

from backend.content import curriculum
from backend import state as learning_state


class LearningStateTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.original_state_file = learning_state.STATE_FILE
        learning_state.STATE_FILE = Path(self.temp_dir.name) / "learning_state.json"
        self.data = curriculum()

    def tearDown(self):
        learning_state.STATE_FILE = self.original_state_file
        self.temp_dir.cleanup()

    def test_quiz_score_is_recomputed_from_the_question_bank(self):
        quiz = self.data["quizzes"][0]
        answers = [
            {"selected": (question["answer"] + 1) % len(question["options"])}
            for question in quiz["questions"]
        ]
        state = learning_state.add_quiz_attempt(
            {
                "quiz_id": quiz["id"],
                "lesson_id": quiz["lesson_id"],
                "score": 999,
                "total": 1,
                "answers": answers,
            },
            quiz,
        )
        attempt = state["quiz_attempts"][-1]
        self.assertEqual(attempt["score"], 0)
        self.assertEqual(attempt["total"], len(quiz["questions"]))

    def test_quiz_cannot_be_attached_to_another_lesson(self):
        quiz = self.data["quizzes"][0]
        with self.assertRaises(ValueError):
            learning_state.add_quiz_attempt({"lesson_id": "l19", "answers": []}, quiz)

    def test_evidence_requires_multiple_dimensions(self):
        strong = (
            "因为 softmax 先减去最大值，所以 exp(x-max(x)) 不会在大 logits 上溢出。"
            "公式 sum(exp(x_i-m)) 的 shape 仍沿 token 维度归约。代码实验可以用 assert 检查概率和等于 1。"
            "它的边界是浮点下溢仍可能让极小概率变成零，这不等于改变理论分布。"
        ) * 2
        quality = learning_state.score_evidence(strong, 0)
        self.assertTrue(quality["ready_for_review"])
        self.assertGreaterEqual(quality["rubric_score"], 3)
        chinese_only = (
            "因为稳定化能限制指数输入，所以公式中的概率归一化更可靠。"
            "代码实验用测试检查概率和，边界是极小数仍可能下溢。"
        ) * 4
        self.assertTrue(learning_state.score_evidence(chinese_only, 1)["dimensions"]["math_or_shape"])
        self.assertFalse(learning_state.score_evidence("我已经懂了" * 30, 3)["ready_for_review"])

    def test_review_requires_closed_book_recall(self):
        with self.assertRaises(ValueError):
            learning_state.add_review({"lesson_id": "l01", "quality": "easy", "recall_text": "太短"})
        state = learning_state.add_review(
            {
                "lesson_id": "l01",
                "quality": "good",
                "recall_text": "BPE 每一步统计词内相邻符号对，合并频率最高的一对，并且不能跨越单词边界。",
            }
        )
        self.assertEqual(state["reviews"]["l01"]["count"], 1)

    def test_diagnostic_does_not_inflate_mastery_and_practice_does(self):
        state = learning_state.default_state()
        state["diagnostics"] = {
            "diag-transformer": {"level": 3, "competency": "modeling", "updated_at": learning_state.now_iso()}
        }
        learning_state.save_state(state)
        lesson = next(item for item in self.data["lessons"] if item["id"] == "l03")
        self.assertEqual(learning_state.lesson_mastery_row(lesson, learning_state.load_state())["score"], 0)

        learning_state.add_lab_attempt(
            {
                "lab_id": "studio:attention-reference",
                "lesson_id": "l03",
                "summary": "3/3 tests passed",
                "metrics": {"passed": 3, "total": 3},
            }
        )
        row = learning_state.lesson_mastery_row(lesson, learning_state.load_state())
        self.assertEqual(row["components"]["practice"], 30)

    def test_prerequisite_path_crosses_phase_boundaries(self):
        graph = learning_state.course_knowledge_graph(self.data)
        prerequisites = [edge for edge in graph["edges"] if edge["type"] == "prerequisite"]
        self.assertEqual(len(prerequisites), len(self.data["lessons"]) - 1)
        self.assertIn({"source": "prep-training-loop", "target": "l01", "type": "prerequisite"}, prerequisites)

    def test_next_action_uses_mastery_evidence_not_reading_completion(self):
        state = learning_state.default_state()
        state["lesson_progress"]["prep-python"] = {
            "status": "completed",
            "updated_at": learning_state.now_iso(),
        }
        learning_state.save_state(state)
        actions = learning_state.compute_next_actions(self.data, learning_state.load_state())
        learn = next(action for action in actions if action["type"] == "learn")
        self.assertEqual(learn["lesson_id"], "prep-python")
        self.assertIn("形成性自测", learn["reason"])


if __name__ == "__main__":
    unittest.main()
