from copy import deepcopy
from datetime import datetime, timedelta, timezone
from pathlib import Path
import json
import re
import threading
import uuid

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
STATE_FILE = DATA_DIR / "learning_state.json"
STATE_LOCK = threading.RLock()


COMPETENCIES = [
    {"id": "foundations", "title": "基础工程与张量直觉", "description": "Python、shape、训练循环、概率和线代。"},
    {"id": "modeling", "title": "语言模型与 Transformer", "description": "tokenizer、LM objective、attention、MLP、normalization、optimizer。"},
    {"id": "math", "title": "数学推导与资源核算", "description": "softmax、cross entropy、FLOPs、显存、scaling law。"},
    {"id": "systems", "title": "系统优化与并行", "description": "GPU/TPU、kernel、FlashAttention、data/tensor/pipeline parallel。"},
    {"id": "evaluation", "title": "推理、Scaling 与评测", "description": "inference、KV cache、benchmark、contamination、scaling extrapolation。"},
    {"id": "data", "title": "数据管线", "description": "数据来源、过滤、去重、混合、合成数据和许可风险。"},
    {"id": "alignment", "title": "后训练与对齐", "description": "SFT、RLHF、DPO、RLVR、安全对齐和多模态。"},
]


LESSON_COMPETENCIES = {
    "prep-python": ["foundations"],
    "prep-tensors": ["foundations", "math"],
    "prep-training-loop": ["foundations", "modeling"],
    "l01": ["modeling", "math"],
    "l02": ["math", "systems"],
    "l03": ["modeling", "math"],
    "l04": ["modeling", "systems"],
    "l05": ["systems"],
    "l06": ["systems", "math"],
    "l07": ["systems"],
    "l08": ["systems"],
    "l09": ["math", "evaluation"],
    "l10": ["evaluation", "systems"],
    "l11": ["math", "evaluation"],
    "l12": ["evaluation"],
    "l13": ["data"],
    "l14": ["data", "evaluation"],
    "l15": ["alignment"],
    "l16": ["alignment", "math"],
    "l17": ["alignment", "modeling"],
    "l18": ["evaluation"],
    "l19": ["foundations", "modeling", "systems", "evaluation", "data", "alignment"],
}


DIAGNOSTIC_ITEMS = [
    {"id": "diag-shapes", "competency": "foundations", "prompt": "我能看懂 B、T、D、V 等 shape 约定，并能发现维度错误。"},
    {"id": "diag-prob", "competency": "math", "prompt": "我能手算 softmax、cross entropy 和简单梯度更新。"},
    {"id": "diag-transformer", "competency": "modeling", "prompt": "我能从 token ids 讲到 logits，包括 attention 和 MLP。"},
    {"id": "diag-resources", "competency": "systems", "prompt": "我能估算 FLOPs、显存和判断 compute/memory bound。"},
    {"id": "diag-eval", "competency": "evaluation", "prompt": "我能设计评测并说明 benchmark contamination 风险。"},
    {"id": "diag-data", "competency": "data", "prompt": "我能设计数据过滤、去重、混合和污染控制流程。"},
    {"id": "diag-align", "competency": "alignment", "prompt": "我能区分 SFT、RLHF、DPO、RLVR 和它们的训练信号。"},
]


def now_iso():
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def parse_iso(value):
    if not value:
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None


def default_state():
    return {
        "profile": {
            "level": "beginner",
            "weekly_hours": 10,
            "goal": "从零掌握 CS336 的理论、数学和基础实现",
            "target_date": "",
            "updated_at": now_iso(),
        },
        "lesson_progress": {},
        "quiz_attempts": [],
        "evidence": [],
        "reviews": {},
        "notes": {},
        "diagnostics": {},
        "lab_attempts": [],
        "events": [],
        "created_at": now_iso(),
        "updated_at": now_iso(),
    }


def load_state():
    with STATE_LOCK:
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        if not STATE_FILE.exists():
            state = default_state()
            save_state(state)
            return state
        with STATE_FILE.open("r", encoding="utf-8") as file:
            state = json.load(file)
        return migrate_state(state)


def save_state(state):
    with STATE_LOCK:
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        state["updated_at"] = now_iso()
        tmp = STATE_FILE.with_name(f"{STATE_FILE.name}.{uuid.uuid4().hex}.tmp")
        with tmp.open("w", encoding="utf-8") as file:
            json.dump(state, file, ensure_ascii=False, indent=2)
        tmp.replace(STATE_FILE)
        return state


def migrate_state(state):
    base = default_state()
    merged = deepcopy(base)
    for key, value in state.items():
        if isinstance(value, dict) and isinstance(merged.get(key), dict):
            merged[key].update(value)
        else:
            merged[key] = value
    return merged


def record_event(state, verb, object_id, object_type, result=None, context=None):
    event = {
        "id": str(uuid.uuid4()),
        "timestamp": now_iso(),
        "actor": "local learner",
        "verb": verb,
        "object": {"id": object_id, "type": object_type},
        "result": result or {},
        "context": context or {},
    }
    state.setdefault("events", []).append(event)
    state["events"] = state["events"][-500:]
    return event


def update_profile(payload):
    state = load_state()
    profile = state.setdefault("profile", {})
    for key in ("level", "weekly_hours", "goal", "target_date"):
        if key in payload:
            profile[key] = payload[key]
    profile["updated_at"] = now_iso()
    record_event(state, "updated", "profile", "learner-profile", {"profile": profile})
    save_state(state)
    return state


def reset_state():
    state = default_state()
    record_event(state, "reset", "learning-state", "system")
    save_state(state)
    return state


def update_lesson_progress(payload):
    state = load_state()
    lesson_id = payload["lesson_id"]
    progress = state.setdefault("lesson_progress", {}).setdefault(
        lesson_id,
        {"status": "not_started", "confidence": 0, "started_at": now_iso(), "updated_at": now_iso()},
    )
    for key in ("status", "confidence", "active_tab"):
        if key in payload:
            progress[key] = payload[key]
    if payload.get("status") == "completed":
        progress["completed_at"] = now_iso()
    if payload.get("status") == "mastered":
        progress["mastered_at"] = now_iso()
    progress["updated_at"] = now_iso()
    record_event(state, "progressed", lesson_id, "lesson", {"progress": progress})
    save_state(state)
    return state


def add_quiz_attempt(payload, quiz=None):
    state = load_state()
    if quiz is None:
        raise ValueError("quiz definition is required")
    lesson_id = payload.get("lesson_id")
    if quiz.get("lesson_id") != lesson_id:
        raise ValueError("quiz does not belong to this lesson")
    submitted = payload.get("answers", [])
    selected_by_index = {
        index: item.get("selected")
        for index, item in enumerate(submitted)
        if isinstance(item, dict)
    }
    answers = []
    for index, question in enumerate(quiz.get("questions", [])):
        selected = selected_by_index.get(index)
        answers.append(
            {
                "question": question["prompt"],
                "selected": selected,
                "correct": question["answer"],
                "is_correct": selected == question["answer"],
            }
        )
    score = sum(1 for answer in answers if answer["is_correct"])
    total = len(answers)
    attempt = {
        "id": str(uuid.uuid4()),
        "quiz_id": quiz["id"],
        "lesson_id": lesson_id,
        "score": score,
        "total": total,
        "answers": answers,
        "created_at": now_iso(),
    }
    attempt["percent"] = round(100 * attempt["score"] / max(1, attempt["total"]))
    state.setdefault("quiz_attempts", []).append(attempt)
    record_event(state, "answered", attempt["quiz_id"], "quiz", {"attempt": attempt})
    save_state(state)
    return state


def add_lab_attempt(payload):
    state = load_state()
    attempt = {
        "id": str(uuid.uuid4()),
        "lab_id": payload.get("lab_id"),
        "lesson_id": payload.get("lesson_id"),
        "summary": payload.get("summary", "").strip(),
        "metrics": payload.get("metrics", {}),
        "created_at": now_iso(),
    }
    state.setdefault("lab_attempts", []).append(attempt)
    record_event(state, "ran", attempt["lab_id"], "interactive-lab", {"attempt": attempt})
    save_state(state)
    return state


def add_evidence(payload):
    state = load_state()
    evidence = {
        "id": str(uuid.uuid4()),
        "lesson_id": payload.get("lesson_id"),
        "gate_id": payload.get("gate_id"),
        "type": payload.get("type", "self-explanation"),
        "text": payload.get("text", "").strip(),
        "confidence": int(payload.get("confidence", 2)),
        "status": "submitted",
        "created_at": now_iso(),
    }
    evidence["quality"] = score_evidence(evidence["text"], evidence["confidence"])
    state.setdefault("evidence", []).append(evidence)
    record_event(state, "submitted", evidence["lesson_id"], "mastery-evidence", {"evidence": evidence})
    save_state(state)
    return state


def update_diagnostic(payload):
    state = load_state()
    item_by_id = {item["id"]: item for item in DIAGNOSTIC_ITEMS}
    responses = payload.get("responses")
    if responses is None and "item_id" in payload:
        responses = {payload["item_id"]: payload.get("level", 0)}
    if not isinstance(responses, dict):
        responses = {}

    normalized = {}
    for item_id, raw_level in responses.items():
        if item_id not in item_by_id:
            continue
        try:
            level = int(raw_level)
        except (TypeError, ValueError):
            level = 0
        level = max(0, min(3, level))
        item = item_by_id[item_id]
        normalized[item_id] = {
            "level": level,
            "competency": item["competency"],
            "prompt": item["prompt"],
            "updated_at": now_iso(),
        }

    state.setdefault("diagnostics", {}).update(normalized)
    record_event(state, "diagnosed", "self-assessment", "diagnostic", {"responses": normalized})
    save_state(state)
    return state


def save_note(payload):
    state = load_state()
    lesson_id = payload.get("lesson_id")
    state.setdefault("notes", {})[lesson_id] = {
        "text": payload.get("text", ""),
        "updated_at": now_iso(),
    }
    record_event(state, "noted", lesson_id, "lesson-note")
    save_state(state)
    return state


def add_review(payload):
    state = load_state()
    lesson_id = payload["lesson_id"]
    quality = payload.get("quality", "good")
    recall_text = str(payload.get("recall_text", "")).strip()
    if len(recall_text) < 30:
        raise ValueError("review recall must contain at least 30 characters")
    current = state.setdefault("reviews", {}).get(lesson_id, {})
    interval = next_interval(current.get("interval_days", 0), quality)
    review = {
        "lesson_id": lesson_id,
        "quality": quality,
        "recall_text": recall_text,
        "interval_days": interval,
        "last_reviewed_at": now_iso(),
        "due_at": (datetime.now(timezone.utc) + timedelta(days=interval)).replace(microsecond=0).isoformat(),
        "count": int(current.get("count", 0)) + 1,
    }
    state["reviews"][lesson_id] = review
    record_event(state, "reviewed", lesson_id, "lesson", {"review": review})
    save_state(state)
    return state


def next_interval(previous, quality):
    if quality == "again":
        return 1
    if quality == "hard":
        return max(1, min(3, previous + 1))
    if quality == "easy":
        return max(4, previous * 2 if previous else 7)
    return max(2, previous * 2 if previous else 3)


def score_evidence(text, confidence):
    normalized = str(text or "").strip()
    lower = normalized.lower()
    dimensions = {
        "reasoning": any(token in lower for token in ("因为", "所以", "因此", "前提", "because", "therefore")),
        "math_or_shape": bool(re.search(r"[=<>]|\b(shape|softmax|loss|flops|bytes|kl)\b|概率|公式|维度", lower)),
        "implementation": any(token in lower for token in ("代码", "伪代码", "def ", "tensor", "变量", "实验", "test", "assert")),
        "boundary": any(token in lower for token in ("近似", "限制", "失败", "误区", "风险", "边界", "不能", "不等于")),
    }
    length_score = 2 if len(normalized) >= 300 else 1 if len(normalized) >= 160 else 0
    rubric_score = sum(1 for value in dimensions.values() if value)
    confidence_score = min(3, max(0, int(confidence)))
    return {
        "length_score": length_score,
        "confidence_score": confidence_score,
        "rubric_score": rubric_score,
        "dimensions": dimensions,
        "ready_for_review": length_score >= 1 and rubric_score >= 3,
    }


def dashboard(curriculum):
    state = load_state()
    lessons = curriculum["lessons"]
    progress = state.get("lesson_progress", {})
    completed = [lesson_id for lesson_id, item in progress.items() if item.get("status") in {"completed", "mastered"}]
    mastery_rows = [lesson_mastery_row(lesson, state) for lesson in lessons]
    mastered = [row["lesson_id"] for row in mastery_rows if row["score"] >= 90]
    due_reviews = review_queue(curriculum, state)
    next_actions = compute_next_actions(curriculum, state)
    phase_rows = []
    for phase in curriculum["roadmap"]:
        ids = phase["lessons"]
        done = sum(1 for lesson_id in ids if progress.get(lesson_id, {}).get("status") in {"completed", "mastered"})
        phase_rows.append(
            {
                "id": phase["id"],
                "title": phase["title"],
                "done": done,
                "total": len(ids),
                "percent": round(100 * done / max(1, len(ids))),
            }
        )
    return {
        "profile": state["profile"],
        "totals": {
            "lessons": len(lessons),
            "completed": len(completed),
            "mastered": len(mastered),
            "evidence": len(state.get("evidence", [])),
            "diagnostics": len(state.get("diagnostics", {})),
            "lab_attempts": len(state.get("lab_attempts", [])),
            "quiz_attempts": len(state.get("quiz_attempts", [])),
            "events": len(state.get("events", [])),
        },
        "mastery_snapshot": mastery_snapshot(curriculum, state),
        "phase_progress": phase_rows,
        "due_reviews": due_reviews,
        "next_actions": next_actions,
        "recent_events": list(reversed(state.get("events", [])[-8:])),
    }


def review_queue(curriculum, state=None):
    state = state or load_state()
    lessons_by_id = {lesson["id"]: lesson for lesson in curriculum["lessons"]}
    now = datetime.now(timezone.utc)
    queue = []
    for lesson_id, progress in state.get("lesson_progress", {}).items():
        if progress.get("status") not in {"completed", "mastered"}:
            continue
        review = state.get("reviews", {}).get(lesson_id)
        due_at = parse_iso(review.get("due_at")) if review else None
        is_due = due_at is None or due_at <= now
        if is_due and lesson_id in lessons_by_id:
            queue.append(
                {
                    "lesson_id": lesson_id,
                    "title": lessons_by_id[lesson_id]["title"],
                    "lecture": lessons_by_id[lesson_id]["lecture"],
                    "reason": "首次复习" if review is None else "到期复习",
                    "due_at": review.get("due_at") if review else now_iso(),
                }
            )
    return queue[:8]


def compute_next_actions(curriculum, state=None):
    state = state or load_state()
    actions = []
    if len(state.get("diagnostics", {})) < len(DIAGNOSTIC_ITEMS):
        actions.append(
            {
                "type": "diagnostic",
                "title": "完成入门诊断",
                "lesson_id": curriculum["lessons"][0]["id"],
                "reason": "先确认基础能力，系统才能把时间分配到数学、代码、系统或数据薄弱点。",
            }
        )

    due = review_queue(curriculum, state)
    if due:
        actions.append(
            {
                "type": "review",
                "title": f"复习：{due[0]['lecture']} · {due[0]['title']}",
                "lesson_id": due[0]["lesson_id"],
                "reason": "间隔复习到期，先巩固再学新内容。",
            }
        )

    for lesson in curriculum["lessons"]:
        row = lesson_mastery_row(lesson, state)
        if row["score"] < 75:
            actions.append(
                {
                    "type": "learn",
                    "title": f"继续学习：{lesson['lecture']} · {lesson['title']}",
                    "lesson_id": lesson["id"],
                    "reason": row["next_step"],
                }
            )
            break

    weak = weakest_quiz_area(curriculum, state)
    if weak:
        actions.append(weak)

    if len(state.get("evidence", [])) < 3:
        actions.append(
            {
                "type": "evidence",
                "title": "提交一份掌握证据",
                "lesson_id": actions[0].get("lesson_id") if actions else curriculum["lessons"][0]["id"],
                "reason": "学习闭环需要你写出解释或小实验结果，而不是只看页面。",
            }
        )
    return actions[:4]


def weakest_quiz_area(curriculum, state):
    attempts = state.get("quiz_attempts", [])
    if not attempts:
        return {
            "type": "quiz",
            "title": "完成一次形成性自测",
            "lesson_id": curriculum["lessons"][0]["id"],
            "reason": "还没有测验记录，系统无法判断薄弱点。",
        }
    last = attempts[-1]
    if last["percent"] < 80:
        return {
            "type": "quiz",
            "title": f"重做测验：{last['quiz_id']}",
            "lesson_id": last.get("lesson_id") or curriculum["lessons"][0]["id"],
            "reason": f"最近一次得分 {last['percent']}%，未达到 80% 掌握线。",
        }
    return None


def learning_model(curriculum):
    return {
        "competencies": COMPETENCIES,
        "diagnostic_items": DIAGNOSTIC_ITEMS,
        "lesson_competencies": LESSON_COMPETENCIES,
        "knowledge_graph": course_knowledge_graph(curriculum),
        "cycle": [
            {"id": "diagnose", "title": "诊断", "description": "先确认基础能力和学习目标。"},
            {"id": "learn", "title": "学习", "description": "按官方课程顺序学习概念、数学和代码。"},
            {"id": "check", "title": "自测", "description": "用形成性测验发现误解。"},
            {"id": "practice", "title": "实践", "description": "在浏览器 CPU 环境实现核心算法并通过测试。"},
            {"id": "evidence", "title": "证据", "description": "写出解释、伪代码或实验分析。"},
            {"id": "review", "title": "复习", "description": "按间隔复习巩固薄弱单元。"},
        ],
        "rubric": {
            "progress": 10,
            "quiz": 25,
            "practice": 30,
            "evidence": 20,
            "review": 15,
        },
    }


def course_knowledge_graph(curriculum):
    nodes = []
    edges = []
    for competency in COMPETENCIES:
        nodes.append({"id": competency["id"], "type": "competency", "title": competency["title"]})

    lesson_by_id = {lesson["id"]: lesson for lesson in curriculum["lessons"]}
    previous = None
    for phase in curriculum["roadmap"]:
        for index, lesson_id in enumerate(phase["lessons"]):
            lesson = lesson_by_id.get(lesson_id)
            if not lesson:
                continue
            nodes.append(
                {
                    "id": lesson_id,
                    "type": "lesson",
                    "title": lesson["title"],
                    "lecture": lesson["lecture"],
                    "phase": phase["id"],
                    "order": index,
                    "competencies": LESSON_COMPETENCIES.get(lesson_id, []),
                }
            )
            if previous:
                edges.append({"source": previous, "target": lesson_id, "type": "prerequisite"})
            previous = lesson_id
            for competency_id in LESSON_COMPETENCIES.get(lesson_id, []):
                edges.append({"source": competency_id, "target": lesson_id, "type": "covers"})
    return {"nodes": nodes, "edges": edges}


def mastery_report(curriculum, state=None):
    state = state or load_state()
    lesson_rows = [lesson_mastery_row(lesson, state) for lesson in curriculum["lessons"]]
    competency_rows = competency_mastery_rows(curriculum, state, lesson_rows)
    weak_lessons = sorted(lesson_rows, key=lambda item: item["score"])[:6]
    weak_competencies = [item for item in sorted(competency_rows, key=lambda row: row["score"]) if item["score"] < 75][:4]
    blockers = learning_blockers(curriculum, state, lesson_rows, competency_rows)
    average = round(sum(row["score"] for row in lesson_rows) / max(1, len(lesson_rows)))
    return {
        "generated_at": now_iso(),
        "average_score": average,
        "status": score_status(average),
        "rubric": learning_model(curriculum)["rubric"],
        "competencies": competency_rows,
        "lessons": lesson_rows,
        "weak_lessons": weak_lessons,
        "weak_competencies": weak_competencies,
        "blockers": blockers,
    }


def mastery_snapshot(curriculum, state=None):
    report = mastery_report(curriculum, state)
    return {
        "average_score": report["average_score"],
        "status": report["status"],
        "weak_competencies": report["weak_competencies"][:2],
        "blockers": report["blockers"][:2],
    }


def lesson_mastery_row(lesson, state):
    lesson_id = lesson["id"]
    progress = state.get("lesson_progress", {}).get(lesson_id, {})
    status = progress.get("status", "not_started")
    progress_points = {"not_started": 0, "in_progress": 3, "completed": 7, "mastered": 10}.get(status, 0)

    quiz = latest_quiz_for_lesson(state, lesson_id)
    quiz_points = round((quiz["percent"] / 100) * 25) if quiz else 0

    practice = best_practice_for_lesson(state, lesson_id)
    practice_points = round((practice["percent"] / 100) * 30) if practice else 0

    evidence = best_evidence_for_lesson(state, lesson_id)
    evidence_points = evidence_points_for(evidence)

    review = state.get("reviews", {}).get(lesson_id)
    review_points = min(15, int(review.get("count", 0)) * 4) if review and len(review.get("recall_text", "")) >= 30 else 0
    if review_points and review.get("quality") == "easy":
        review_points = min(15, review_points + 1)

    score = min(100, progress_points + quiz_points + practice_points + evidence_points + review_points)
    next_step = lesson_next_step(score, status, quiz, practice, evidence, review)
    return {
        "lesson_id": lesson_id,
        "title": lesson["title"],
        "lecture": lesson["lecture"],
        "phase": lesson["phase"],
        "competencies": LESSON_COMPETENCIES.get(lesson_id, []),
        "score": score,
        "status": score_status(score),
        "components": {
            "progress": progress_points,
            "quiz": quiz_points,
            "practice": practice_points,
            "evidence": evidence_points,
            "review": review_points,
        },
        "latest_quiz_percent": quiz["percent"] if quiz else None,
        "latest_practice_percent": practice["percent"] if practice else None,
        "evidence_ready": bool(evidence and evidence.get("quality", {}).get("ready_for_review")),
        "review_count": int(review.get("count", 0)) if review else 0,
        "next_step": next_step,
    }


def competency_mastery_rows(curriculum, state, lesson_rows):
    lesson_rows_by_id = {row["lesson_id"]: row for row in lesson_rows}
    diagnostic_by_comp = diagnostic_scores_by_competency(state)
    rows = []
    for competency in COMPETENCIES:
        lesson_scores = [
            lesson_rows_by_id[lesson_id]["score"]
            for lesson_id, comp_ids in LESSON_COMPETENCIES.items()
            if competency["id"] in comp_ids and lesson_id in lesson_rows_by_id
        ]
        lesson_score = round(sum(lesson_scores) / max(1, len(lesson_scores)))
        diagnostic_score = diagnostic_by_comp.get(competency["id"])
        score = lesson_score
        weak_lesson_ids = [
            row["lesson_id"]
            for row in sorted(
                (lesson_rows_by_id[lesson_id] for lesson_id, comp_ids in LESSON_COMPETENCIES.items() if competency["id"] in comp_ids and lesson_id in lesson_rows_by_id),
                key=lambda item: item["score"],
            )[:3]
        ]
        rows.append(
            {
                "id": competency["id"],
                "title": competency["title"],
                "description": competency["description"],
                "score": score,
                "status": score_status(score),
                "diagnostic_score": diagnostic_score,
                "lesson_count": len(lesson_scores),
                "weak_lessons": weak_lesson_ids,
            }
        )
    return rows


def study_plan(curriculum, state=None, weeks=4):
    state = state or load_state()
    profile = state.get("profile", {})
    weekly_hours = int(profile.get("weekly_hours", 10) or 10)
    sessions_per_week = max(3, min(7, round(weekly_hours * 60 / 70)))
    lesson_rows = {row["lesson_id"]: row for row in [lesson_mastery_row(lesson, state) for lesson in curriculum["lessons"]]}
    pending_lessons = [lesson for lesson in curriculum["lessons"] if lesson_rows[lesson["id"]]["score"] < 75]
    target_date = str(profile.get("target_date", "") or "")
    available_weeks = None
    if target_date:
        try:
            days = (datetime.fromisoformat(target_date).date() - datetime.now(timezone.utc).date()).days
            available_weeks = max(1, (max(0, days) + 6) // 7)
        except ValueError:
            available_weeks = None
    weeks = max(1, min(8, available_weeks or int(weeks or 4)))
    required_sessions = len(pending_lessons)
    pace_status = "on_track" if weeks * sessions_per_week >= required_sessions else "over_capacity"
    due = review_queue(curriculum, state)
    plan_weeks = []
    cursor = 0

    for week_index in range(weeks):
        sessions = []
        if week_index == 0:
            for review in due[:2]:
                sessions.append(
                    {
                        "type": "review",
                        "title": f"复习：{review['lecture']} · {review['title']}",
                        "lesson_id": review["lesson_id"],
                        "minutes": 25,
                        "activities": ["先闭卷写回忆答案", "再对照公式/代码路径纠错", "记录复习质量"],
                    }
                )

        while len(sessions) < sessions_per_week and cursor < len(pending_lessons):
            lesson = pending_lessons[cursor]
            row = lesson_rows[lesson["id"]]
            sessions.append(
                {
                    "type": "lesson",
                    "title": f"{lesson['lecture']} · {lesson['title']}",
                    "lesson_id": lesson["id"],
                    "minutes": 70,
                    "activities": activities_for_score(row["score"]),
                    "target": row["next_step"],
                }
            )
            cursor += 1

        if len(sessions) < sessions_per_week:
            sessions.append(
                {
                    "type": "capstone",
                    "title": "阶段复盘与勘误",
                    "lesson_id": curriculum["lessons"][-1]["id"],
                    "minutes": 60,
                    "activities": ["整理错题", "补一份掌握证据", "对照官方材料修正笔记"],
                    "target": "把本周最弱的一个概念讲清楚。",
                }
            )

        plan_weeks.append(
            {
                "week": week_index + 1,
                "hours": round(sum(session["minutes"] for session in sessions) / 60, 1),
                "sessions": sessions,
            }
        )

    return {
        "generated_at": now_iso(),
        "goal": profile.get("goal", ""),
        "level": profile.get("level", "beginner"),
        "target_date": target_date,
        "pace_status": pace_status,
        "remaining_lessons": required_sessions,
        "weekly_hours": weekly_hours,
        "sessions_per_week": sessions_per_week,
        "rules": [
            "分数低于 75 的单元优先进入计划。",
            "到期复习在每周第一批 session 中优先安排。",
            "每个新单元必须覆盖概念、数学、代码和产出证据。",
            "诊断只调整提示和优先级，不直接增加掌握分。",
        ],
        "weeks": plan_weeks,
    }


def latest_quiz_for_lesson(state, lesson_id):
    attempts = [item for item in state.get("quiz_attempts", []) if item.get("lesson_id") == lesson_id]
    return attempts[-1] if attempts else None


def best_evidence_for_lesson(state, lesson_id):
    evidence = [item for item in state.get("evidence", []) if item.get("lesson_id") == lesson_id]
    if not evidence:
        return None
    return sorted(evidence, key=lambda item: evidence_points_for(item), reverse=True)[0]


def best_practice_for_lesson(state, lesson_id):
    attempts = []
    for item in state.get("lab_attempts", []):
        if item.get("lesson_id") != lesson_id or not str(item.get("lab_id", "")).startswith("studio:"):
            continue
        metrics = item.get("metrics", {})
        total = int(metrics.get("total", 0) or 0)
        passed = int(metrics.get("passed", 0) or 0)
        if total <= 0:
            continue
        attempts.append({**item, "percent": round(100 * passed / total)})
    return max(attempts, key=lambda item: item["percent"], default=None)


def evidence_points_for(evidence):
    if not evidence:
        return 0
    quality = evidence.get("quality", {})
    points = quality.get("length_score", 0) * 4 + quality.get("rubric_score", 0) * 3
    return min(20, points)


def diagnostic_scores_by_competency(state):
    values = {}
    for item in state.get("diagnostics", {}).values():
        values.setdefault(item.get("competency"), []).append(int(item.get("level", 0)))
    return {competency_id: round((sum(levels) / max(1, len(levels))) / 3 * 100) for competency_id, levels in values.items()}


def diagnostic_points_for_lesson(state, lesson_id):
    scores = diagnostic_scores_by_competency(state)
    comp_scores = [scores[comp_id] for comp_id in LESSON_COMPETENCIES.get(lesson_id, []) if comp_id in scores]
    if not comp_scores:
        return 0
    return round((sum(comp_scores) / len(comp_scores)) / 100 * 10)


def score_status(score):
    if score >= 90:
        return "掌握"
    if score >= 75:
        return "达标"
    if score >= 50:
        return "待巩固"
    if score >= 25:
        return "刚入门"
    return "薄弱"


def lesson_next_step(score, status, quiz, practice, evidence, review):
    if status == "not_started":
        return "先读总览，再完成数学和代码页面的逐条讲解。"
    if not quiz:
        return "完成形成性自测，让系统知道误解在哪里。"
    if quiz["percent"] < 80:
        return "重做测验，并把错题写成一条笔记。"
    if not practice:
        return "完成本讲 CPU 实践任务，并通过自动测试。"
    if practice["percent"] < 100:
        return "修复实践任务中的失败测试，再解释错误原因。"
    if not evidence or not evidence.get("quality", {}).get("ready_for_review"):
        return "提交一份包含公式、shape 或伪代码的掌握证据。"
    if not review:
        return "做一次间隔复习，确认不是短期记忆。"
    if score < 75:
        return "回到官方材料，对照本项目解释补齐薄弱点。"
    return "可以进入下一个单元，同时保留后续复习。"


def activities_for_score(score):
    if score < 25:
        return ["读总览", "列出核心概念", "手抄并解释公式符号", "运行 CPU 实践任务"]
    if score < 50:
        return ["逐行读代码", "通过 CPU 实践测试", "做本讲形成性自测", "记录错题"]
    if score < 75:
        return ["补掌握证据", "复习错题", "对照官方材料修正理解"]
    return ["间隔复习", "把本讲内容讲给未来的自己", "进入下一讲"]


def learning_blockers(curriculum, state, lesson_rows, competency_rows):
    blockers = []
    if len(state.get("diagnostics", {})) < len(DIAGNOSTIC_ITEMS):
        blockers.append({"type": "diagnostic", "title": "诊断未完成", "reason": "系统缺少基础能力画像，学习计划只能按默认顺序推进。"})
    if len(state.get("evidence", [])) < 3:
        blockers.append({"type": "evidence", "title": "掌握证据不足", "reason": "阅读记录不能证明你会推导、实现或解释。"})
    weak = [item for item in competency_rows if item["score"] < 40]
    if weak:
        blockers.append({"type": "competency", "title": f"{weak[0]['title']} 很薄弱", "reason": "该能力低于 40 分，会影响后续单元理解。"})
    first_pending = next((row for row in lesson_rows if row["score"] < 25), None)
    if first_pending:
        blockers.append({"type": "lesson", "title": f"当前入口：{first_pending['lecture']} · {first_pending['title']}", "reason": first_pending["next_step"]})
    due = review_queue(curriculum, state)
    if due:
        blockers.append({"type": "review", "title": "存在到期复习", "reason": "复习队列到期后应优先处理，避免只学新内容。"})
    return blockers[:5]
