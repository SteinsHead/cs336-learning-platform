from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from pathlib import Path
from urllib.parse import parse_qs, unquote, urlparse
import argparse
import json
import mimetypes
import sys

ROOT = Path(__file__).resolve().parents[1]
FRONTEND = ROOT / "frontend"
sys.path.insert(0, str(ROOT))

from backend.content import (  # noqa: E402
    ASSIGNMENTS,
    GLOSSARY,
    LABS,
    MASTERY_GATES,
    ROADMAP,
    SOURCE_MAP,
    curriculum,
    enriched_lessons,
    lesson_by_id,
    quiz_by_id,
)
from backend.state import (  # noqa: E402
    add_evidence,
    add_lab_attempt,
    add_quiz_attempt,
    add_review,
    compute_next_actions,
    dashboard,
    learning_model,
    load_state,
    mastery_report,
    reset_state,
    save_note,
    study_plan,
    update_lesson_progress,
    update_profile,
    update_diagnostic,
    review_queue,
)


class LearningAppHandler(SimpleHTTPRequestHandler):
    server_version = "CS336LearningApp/1.0"

    def log_message(self, format, *args):
        sys.stderr.write("[server] " + format % args + "\n")

    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path

        if path == "/api/health":
            self.json_response({"ok": True, "service": "cs336-learning-app"})
            return

        if path == "/api/curriculum":
            self.json_response(curriculum())
            return

        if path == "/api/state":
            self.json_response(load_state())
            return

        if path == "/api/dashboard":
            self.json_response(dashboard(curriculum()))
            return

        if path == "/api/learning-model":
            self.json_response(learning_model(curriculum()))
            return

        if path == "/api/mastery-report":
            self.json_response(mastery_report(curriculum()))
            return

        if path == "/api/study-plan":
            self.json_response(study_plan(curriculum()))
            return

        if path == "/api/next-actions":
            self.json_response({"actions": compute_next_actions(curriculum())})
            return

        if path == "/api/review-queue":
            self.json_response({"reviews": review_queue(curriculum())})
            return

        if path.startswith("/api/lessons/"):
            lesson_id = unquote(path.rsplit("/", 1)[-1])
            lesson = lesson_by_id(lesson_id)
            if lesson is None:
                self.json_response({"error": "lesson not found"}, status=404)
                return
            self.json_response(lesson)
            return

        if path == "/api/lessons":
            query = parse_qs(parsed.query).get("q", [""])[0].strip().lower()
            lessons = enriched_lessons()
            if query:
                lessons = [lesson for lesson in lessons if query in searchable_text(lesson)]
            self.json_response({"lessons": lessons})
            return

        if path.startswith("/api/quizzes/"):
            quiz_id = unquote(path.rsplit("/", 1)[-1])
            quiz = quiz_by_id(quiz_id)
            if quiz is None:
                self.json_response({"error": "quiz not found"}, status=404)
                return
            self.json_response(quiz)
            return

        if path == "/api/labs":
            self.json_response({"labs": LABS})
            return

        if path == "/api/mastery":
            self.json_response({"source_map": SOURCE_MAP, "mastery_gates": MASTERY_GATES})
            return

        if path == "/api/glossary":
            self.json_response({"glossary": GLOSSARY})
            return

        if path == "/api/assignments":
            self.json_response({"assignments": ASSIGNMENTS})
            return

        if path == "/api/roadmap":
            self.json_response({"roadmap": ROADMAP})
            return

        self.serve_static(path)

    def do_POST(self):
        parsed = urlparse(self.path)
        if parsed.path == "/api/explain":
            self.handle_explain()
            return

        if parsed.path in {
            "/api/profile",
            "/api/progress",
            "/api/quiz-attempt",
            "/api/evidence",
            "/api/diagnostic",
            "/api/lab-attempt",
            "/api/review",
            "/api/notes",
            "/api/reset-state",
        }:
            self.handle_learning_mutation(parsed.path)
            return

        self.json_response({"error": "not found"}, status=404)

    def read_json_body(self):
        length = int(self.headers.get("Content-Length", "0"))
        try:
            return json.loads(self.rfile.read(length) or b"{}")
        except json.JSONDecodeError:
            self.json_response({"error": "invalid json"}, status=400)
            return None

    def handle_learning_mutation(self, path):
        payload = self.read_json_body()
        if payload is None:
            return
        try:
            if path == "/api/profile":
                result = update_profile(payload)
            elif path == "/api/progress":
                result = update_lesson_progress(payload)
            elif path == "/api/quiz-attempt":
                result = add_quiz_attempt(payload)
            elif path == "/api/evidence":
                result = add_evidence(payload)
            elif path == "/api/diagnostic":
                result = update_diagnostic(payload)
            elif path == "/api/lab-attempt":
                result = add_lab_attempt(payload)
            elif path == "/api/review":
                result = add_review(payload)
            elif path == "/api/notes":
                result = save_note(payload)
            elif path == "/api/reset-state":
                result = reset_state()
            else:
                self.json_response({"error": "not found"}, status=404)
                return
        except KeyError as error:
            self.json_response({"error": f"missing field: {error}"}, status=400)
            return
        self.json_response({"state": result, "dashboard": dashboard(curriculum())})

    def handle_explain(self):
        parsed = urlparse(self.path)
        if parsed.path != "/api/explain":
            self.json_response({"error": "not found"}, status=404)
            return

        payload = self.read_json_body()
        if payload is None:
            return

        topic = str(payload.get("topic", "")).strip().lower()
        if not topic:
            self.json_response({"error": "topic is required"}, status=400)
            return

        matches = []
        for lesson in enriched_lessons():
            score = 0
            haystack = searchable_text(lesson)
            for word in topic.split():
                if word in haystack:
                    score += 1
            if topic in haystack:
                score += 3
            if score:
                matches.append((score, lesson))

        matches.sort(key=lambda item: item[0], reverse=True)
        top = [lesson for _, lesson in matches[:3]]
        if not top:
            top = enriched_lessons()[:3]

        response = {
            "topic": payload.get("topic", ""),
            "explanation": make_explanation(top),
            "relatedLessons": top,
        }
        self.json_response(response)

    def serve_static(self, path):
        if path in ("", "/"):
            target = FRONTEND / "index.html"
        else:
            requested = (FRONTEND / path.lstrip("/")).resolve()
            if not str(requested).startswith(str(FRONTEND.resolve())):
                self.send_error(403)
                return
            target = requested
            if target.is_dir():
                target = target / "index.html"
            if not target.exists():
                target = FRONTEND / "index.html"

        content_type = mimetypes.guess_type(str(target))[0] or "application/octet-stream"
        body = target.read_bytes()
        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def json_response(self, payload, status=200):
        body = json.dumps(payload, ensure_ascii=False, indent=2).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


def searchable_text(lesson):
    parts = [
        lesson.get("id", ""),
        lesson.get("lecture", ""),
        lesson.get("title", ""),
        lesson.get("summary", ""),
        lesson.get("beginner_view", ""),
        " ".join(lesson.get("concepts", [])),
        " ".join(item.get("name", "") + " " + item.get("formula", "") for item in lesson.get("math", [])),
    ]
    return " ".join(parts).lower()


def make_explanation(lessons):
    first = lessons[0]
    concepts = "、".join(first.get("concepts", [])[:4])
    math = first.get("math", [{}])[0]
    return {
        "plain": first["beginner_view"],
        "why_it_matters": first["summary"],
        "concepts": concepts,
        "math_anchor": {
            "name": math.get("name", "核心公式"),
            "formula": math.get("formula", ""),
            "latex": math.get("latex", math.get("formula", "")),
            "mathml": math.get("mathml", ""),
            "kind": math.get("kind", "数学表达"),
            "validity": math.get("validity", ""),
            "explain": math.get("explain", ""),
        },
        "next_step": first.get("practice", ["回到课程卡片完成练习。"])[0],
    }


def main():
    parser = argparse.ArgumentParser(description="Run the CS336 learning app.")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8765)
    args = parser.parse_args()

    host = args.host
    port = args.port
    server = ThreadingHTTPServer((host, port), LearningAppHandler)
    print(f"CS336 learning app running at http://{host}:{port}")
    print("Press Ctrl+C to stop.")
    server.serve_forever()


if __name__ == "__main__":
    main()
