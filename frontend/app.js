const STATIC_CURRICULUM_URL = "data/curriculum.json";
const LOCAL_STATE_KEY = "cs336.learning_state.v2";
const CONFIG = globalThis.CS336_CONFIG || {};

const state = {
  data: null,
  currentLessonId: "prep-python",
  tab: "overview",
  completed: new Set(JSON.parse(localStorage.getItem("cs336.completed") || "[]")),
  activeQuiz: "q-basics",
  activeLab: "bpe",
  copyPayloads: new Map(),
  dashboard: null,
  serverState: null,
  learningModel: null,
  masteryReport: null,
  studyPlan: null,
  apiMode: "api",
  staticCurriculum: null,
  staticCurriculumPromise: null,
  cloud: {
    configured: false,
    client: null,
    user: null,
    loading: true,
    syncing: false,
    lastSync: "",
    message: "",
    error: "",
  },
  quizSelections: {},
};

const els = {
  phaseList: document.querySelector("#phaseList"),
  lessonMeta: document.querySelector("#lessonMeta"),
  lessonTitle: document.querySelector("#lessonTitle"),
  lessonBody: document.querySelector("#lessonBody"),
  progressText: document.querySelector("#progressText"),
  progressBar: document.querySelector("#progressBar"),
  markDone: document.querySelector("#markDone"),
  resetProgress: document.querySelector("#resetProgress"),
  searchInput: document.querySelector("#searchInput"),
  labSelect: document.querySelector("#labSelect"),
  labPanel: document.querySelector("#labPanel"),
  explainInput: document.querySelector("#explainInput"),
  explainButton: document.querySelector("#explainButton"),
  explainResult: document.querySelector("#explainResult"),
  quizSelect: document.querySelector("#quizSelect"),
  quizPanel: document.querySelector("#quizPanel"),
  refreshDashboard: document.querySelector("#refreshDashboard"),
  nextActionPanel: document.querySelector("#nextActionPanel"),
  evidenceText: document.querySelector("#evidenceText"),
  evidenceConfidence: document.querySelector("#evidenceConfidence"),
  saveEvidence: document.querySelector("#saveEvidence"),
  accountPanel: document.querySelector("#accountPanel"),
  cloudModeBadge: document.querySelector("#cloudModeBadge"),
  accountOpen: document.querySelector("#accountOpen"),
  accountStatusDot: document.querySelector("#accountStatusDot"),
  accountStatusText: document.querySelector("#accountStatusText"),
  accountStatusHint: document.querySelector("#accountStatusHint"),
  accountModal: document.querySelector("#accountModal"),
  accountModalBody: document.querySelector("#accountModalBody"),
};

init();

async function init() {
  const [course, dashboard, serverState, model, report, plan] = await Promise.all([
    apiGet("curriculum"),
    apiGet("dashboard"),
    apiGet("state"),
    apiGet("learning-model"),
    apiGet("mastery-report"),
    apiGet("study-plan"),
  ]);
  state.data = course;
  state.dashboard = dashboard;
  state.serverState = serverState;
  state.learningModel = model;
  state.masteryReport = report;
  state.studyPlan = plan;
  await initCloud();
  await hydrateCloudState();
  state.serverState = await apiGet("state");
  state.dashboard = await apiGet("dashboard");
  state.masteryReport = await apiGet("mastery-report");
  state.studyPlan = await apiGet("study-plan");
  state.currentLessonId = state.data.lessons[0].id;
  state.activeLab = state.data.labs[0].id;
  state.activeQuiz = state.data.quizzes[0].id;
  state.completed = completedFromServer(state.serverState);

  renderControls();
  renderPhases();
  renderLesson();
  renderLab();
  renderQuiz();
  renderLearningConsole();
  renderAccountPanel();
  updateProgress();
  attachEvents();
}

function attachEvents() {
  document.querySelectorAll(".tab").forEach((button) => {
    button.addEventListener("click", () => {
      state.tab = button.dataset.tab;
      document.querySelectorAll(".tab").forEach((tab) => tab.classList.toggle("active", tab === button));
      renderLesson();
    });
  });

  els.markDone.addEventListener("click", async () => {
    if (state.completed.has(state.currentLessonId)) {
      state.completed.delete(state.currentLessonId);
      await postJson("progress", { lesson_id: state.currentLessonId, status: "not_started", confidence: 0, active_tab: state.tab });
    } else {
      state.completed.add(state.currentLessonId);
      await postJson("progress", { lesson_id: state.currentLessonId, status: "completed", confidence: 2, active_tab: state.tab });
    }
    saveProgress();
    await refreshLearningState(false);
    renderPhases();
    renderLessonHeader();
    updateProgress();
  });

  els.resetProgress.addEventListener("click", async () => {
    state.completed.clear();
    saveProgress();
    await postJson("reset-state", {});
    await refreshLearningState(false);
    renderPhases();
    renderLessonHeader();
    updateProgress();
  });

  els.searchInput.addEventListener("input", () => renderPhases(els.searchInput.value));
  els.labSelect.addEventListener("change", () => {
    state.activeLab = els.labSelect.value;
    renderLab();
  });
  els.quizSelect.addEventListener("change", () => {
    state.activeQuiz = els.quizSelect.value;
    state.quizSelections = {};
    renderQuiz();
  });
  els.explainButton.addEventListener("click", explainTopic);
  els.explainInput.addEventListener("keydown", (event) => {
    if (event.key === "Enter") explainTopic();
  });
  els.refreshDashboard.addEventListener("click", refreshLearningState);
  els.saveEvidence.addEventListener("click", submitEvidence);
  els.accountOpen?.addEventListener("click", openAccountModal);
  els.accountModal?.addEventListener("click", (event) => {
    if (event.target === els.accountModal || event.target.closest("[data-account-close]")) closeAccountModal();
  });
  document.addEventListener("keydown", (event) => {
    if (event.key === "Escape" && els.accountModal && !els.accountModal.hidden) closeAccountModal();
  });
  document.querySelectorAll("[data-review]").forEach((button) => {
    button.addEventListener("click", () => submitReview(button.dataset.review));
  });
  document.addEventListener("click", handleCopyClick);
}

async function apiGet(name) {
  if (state.apiMode === "api") {
    try {
      const response = await fetch(`api/${name}`, { cache: "no-store" });
      const contentType = response.headers.get("content-type") || "";
      if (response.ok && contentType.includes("application/json")) return response.json();
    } catch {
      // GitHub Pages has no Python API. Fall through to static mode.
    }
    state.apiMode = "static";
  }
  return staticGet(name);
}

async function apiPost(name, payload) {
  if (state.apiMode === "api") {
    try {
      const response = await fetch(`api/${name}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });
      const contentType = response.headers.get("content-type") || "";
      if (response.ok && contentType.includes("application/json")) return response.json();
    } catch {
      // Switch to browser-local persistence when the API is unavailable.
    }
    state.apiMode = "static";
  }
  return staticPost(name, payload);
}

async function ensureStaticCurriculum() {
  if (state.staticCurriculum) return state.staticCurriculum;
  if (!state.staticCurriculumPromise) {
    state.staticCurriculumPromise = fetch(STATIC_CURRICULUM_URL, { cache: "no-store" }).then((response) => {
      if (!response.ok) throw new Error("无法加载静态课程数据。请先运行静态构建。");
      return response.json();
    });
  }
  state.staticCurriculum = await state.staticCurriculumPromise;
  return state.staticCurriculum;
}

async function staticGet(name) {
  const curriculum = await ensureStaticCurriculum();
  const localState = loadBrowserState();
  if (name === "curriculum") return curriculum;
  if (name === "state") return localState;
  if (name === "dashboard") return buildDashboard(curriculum, localState);
  if (name === "learning-model") return buildLearningModel(curriculum);
  if (name === "mastery-report") return buildMasteryReport(curriculum, localState);
  if (name === "study-plan") return buildStudyPlan(curriculum, localState);
  if (name === "next-actions") return { actions: computeNextActions(curriculum, localState) };
  if (name === "review-queue") return { reviews: buildReviewQueue(curriculum, localState) };
  throw new Error(`Unsupported static GET: ${name}`);
}

async function staticPost(name, payload) {
  const curriculum = await ensureStaticCurriculum();
  if (name === "explain") return buildStaticExplanation(curriculum, payload.topic || "");

  const localState = loadBrowserState();
  if (name === "profile") updateLocalProfile(localState, payload);
  if (name === "progress") updateLocalProgress(localState, payload);
  if (name === "quiz-attempt") addLocalQuizAttempt(localState, payload);
  if (name === "evidence") addLocalEvidence(localState, payload);
  if (name === "review") addLocalReview(localState, payload);
  if (name === "notes") saveLocalNote(localState, payload);
  if (name === "diagnostic") updateLocalDiagnostic(localState, payload);
  if (name === "lab-attempt") addLocalLabAttempt(localState, payload);
  if (name === "reset-state") {
    const reset = defaultBrowserState();
    recordLocalEvent(reset, "reset", "learning-state", "system");
    saveBrowserState(reset);
    await saveCloudState(reset);
    return { state: reset, dashboard: buildDashboard(curriculum, reset) };
  }
  saveBrowserState(localState);
  await saveCloudState(localState);
  return { state: localState, dashboard: buildDashboard(curriculum, localState) };
}

async function initCloud() {
  state.cloud.configured = Boolean(CONFIG.supabaseUrl && CONFIG.supabaseAnonKey);
  state.cloud.loading = true;
  state.cloud.message = "";
  state.cloud.error = "";
  if (!state.cloud.configured) {
    state.cloud.loading = false;
    return;
  }

  try {
    const moduleUrl = CONFIG.supabaseModuleUrl || "https://esm.sh/@supabase/supabase-js@2";
    const { createClient } = await import(moduleUrl);
    state.cloud.client = createClient(CONFIG.supabaseUrl, CONFIG.supabaseAnonKey, {
      auth: {
        persistSession: true,
        autoRefreshToken: true,
        detectSessionInUrl: true,
      },
    });
    const { data, error } = await state.cloud.client.auth.getSession();
    if (error) throw error;
    state.cloud.user = data.session?.user || null;
    state.cloud.client.auth.onAuthStateChange(async (_event, session) => {
      state.cloud.user = session?.user || null;
      if (state.cloud.user) await hydrateCloudState();
      await refreshLearningState();
      renderAccountPanel();
    });
  } catch (error) {
    state.cloud.error = readableError(error);
  } finally {
    state.cloud.loading = false;
  }
}

async function hydrateCloudState() {
  if (!canUseCloud()) return;
  state.cloud.syncing = true;
  state.cloud.error = "";
  try {
    const localState = loadBrowserState();
    const remoteState = await fetchCloudState();
    if (!remoteState) {
      await saveCloudState(localState);
      state.cloud.message = "已创建云端学习档案。";
      return;
    }
    const merged = mergeLearningStates(localState, remoteState);
    saveBrowserState(merged);
    await saveCloudState(merged);
    state.cloud.message = "云端学习状态已合并。";
  } catch (error) {
    state.cloud.error = readableError(error);
  } finally {
    state.cloud.syncing = false;
    state.cloud.lastSync = nowIso();
  }
}

function canUseCloud() {
  return Boolean(state.cloud.configured && state.cloud.client && state.cloud.user);
}

async function fetchCloudState() {
  if (!canUseCloud()) return null;
  const { data, error } = await state.cloud.client
    .from("learning_states")
    .select("state, updated_at")
    .eq("user_id", state.cloud.user.id)
    .maybeSingle();
  if (error) throw error;
  return data?.state || null;
}

async function saveCloudState(nextState) {
  if (!canUseCloud()) return;
  state.cloud.syncing = true;
  state.cloud.error = "";
  try {
    const payload = {
      user_id: state.cloud.user.id,
      state: nextState,
      updated_at: nowIso(),
    };
    const { error } = await state.cloud.client.from("learning_states").upsert(payload, { onConflict: "user_id" });
    if (error) throw error;
    state.cloud.lastSync = payload.updated_at;
    state.cloud.message = "已同步到云端。";
  } catch (error) {
    state.cloud.error = readableError(error);
  } finally {
    state.cloud.syncing = false;
  }
}

function mergeLearningStates(localState, remoteState) {
  const merged = defaultBrowserState();
  const localTime = Date.parse(localState.updated_at || "") || 0;
  const remoteTime = Date.parse(remoteState.updated_at || "") || 0;
  const newer = remoteTime > localTime ? remoteState : localState;

  merged.profile = { ...merged.profile, ...(newer.profile || {}) };
  merged.lesson_progress = mergeByUpdatedAt(localState.lesson_progress || {}, remoteState.lesson_progress || {});
  merged.reviews = mergeByUpdatedAt(localState.reviews || {}, remoteState.reviews || {}, "last_reviewed_at");
  merged.notes = mergeByUpdatedAt(localState.notes || {}, remoteState.notes || {});
  merged.diagnostics = mergeByUpdatedAt(localState.diagnostics || {}, remoteState.diagnostics || {});
  merged.quiz_attempts = mergeArrayById(localState.quiz_attempts || [], remoteState.quiz_attempts || []);
  merged.evidence = mergeArrayById(localState.evidence || [], remoteState.evidence || []);
  merged.lab_attempts = mergeArrayById(localState.lab_attempts || [], remoteState.lab_attempts || []);
  merged.events = mergeArrayById(localState.events || [], remoteState.events || []).slice(-500);
  merged.created_at = [localState.created_at, remoteState.created_at].filter(Boolean).sort()[0] || merged.created_at;
  merged.updated_at = nowIso();
  return merged;
}

function mergeByUpdatedAt(left, right, field = "updated_at") {
  const output = { ...left };
  Object.entries(right).forEach(([key, value]) => {
    const current = output[key];
    if (!current || (Date.parse(value?.[field] || value?.updated_at || "") || 0) >= (Date.parse(current?.[field] || current?.updated_at || "") || 0)) {
      output[key] = value;
    }
  });
  return output;
}

function mergeArrayById(left, right) {
  const output = new Map();
  [...left, ...right].forEach((item) => {
    if (!item?.id) return;
    const current = output.get(item.id);
    if (!current || (Date.parse(item.updated_at || item.created_at || item.timestamp || "") || 0) >= (Date.parse(current.updated_at || current.created_at || current.timestamp || "") || 0)) {
      output.set(item.id, item);
    }
  });
  return [...output.values()].sort((a, b) => String(a.created_at || a.timestamp || "").localeCompare(String(b.created_at || b.timestamp || "")));
}

async function sendMagicLink(trigger) {
  if (!state.cloud.client) return;
  const scope = trigger?.closest(".account-stack") || document;
  const email = scope.querySelector("[data-account-email]")?.value.trim();
  if (!email) {
    state.cloud.error = "请输入邮箱。";
    renderAccountPanel();
    return;
  }
  state.cloud.syncing = true;
  state.cloud.error = "";
  try {
    const redirectTo = CONFIG.supabaseAuthRedirectUrl || location.href.split("#")[0];
    const { error } = await state.cloud.client.auth.signInWithOtp({ email, options: { emailRedirectTo: redirectTo } });
    if (error) throw error;
    state.cloud.message = "登录邮件已发送，请在邮箱中打开链接。";
  } catch (error) {
    state.cloud.error = readableError(error);
  } finally {
    state.cloud.syncing = false;
    renderAccountPanel();
  }
}

async function signInWithGitHub() {
  if (!state.cloud.client) return;
  state.cloud.syncing = true;
  state.cloud.error = "";
  try {
    const redirectTo = CONFIG.supabaseAuthRedirectUrl || location.href.split("#")[0];
    const { error } = await state.cloud.client.auth.signInWithOAuth({ provider: "github", options: { redirectTo } });
    if (error) throw error;
  } catch (error) {
    state.cloud.error = readableError(error);
    state.cloud.syncing = false;
    renderAccountPanel();
  }
}

async function signOutCloud() {
  if (!state.cloud.client) return;
  await state.cloud.client.auth.signOut();
  state.cloud.user = null;
  state.cloud.message = "已退出账号，本机学习记录仍保留。";
  renderAccountPanel();
}

async function manualCloudSync() {
  await hydrateCloudState();
  await refreshLearningState();
  renderAccountPanel();
}

function readableError(error) {
  return error?.message || String(error || "未知错误");
}

function defaultBrowserState() {
  const timestamp = nowIso();
  return {
    profile: {
      level: "beginner",
      weekly_hours: 10,
      goal: "从零掌握 CS336 的理论、数学和基础实现",
      target_date: "",
      updated_at: timestamp,
    },
    lesson_progress: {},
    quiz_attempts: [],
    evidence: [],
    reviews: {},
    notes: {},
    diagnostics: {},
    lab_attempts: [],
    events: [],
    created_at: timestamp,
    updated_at: timestamp,
  };
}

function loadBrowserState() {
  const base = defaultBrowserState();
  try {
    const saved = JSON.parse(localStorage.getItem(LOCAL_STATE_KEY) || "{}");
    return {
      ...base,
      ...saved,
      profile: { ...base.profile, ...(saved.profile || {}) },
      lesson_progress: saved.lesson_progress || {},
      quiz_attempts: saved.quiz_attempts || [],
      evidence: saved.evidence || [],
      reviews: saved.reviews || {},
      notes: saved.notes || {},
      diagnostics: saved.diagnostics || {},
      lab_attempts: saved.lab_attempts || [],
      events: saved.events || [],
    };
  } catch {
    return base;
  }
}

function saveBrowserState(localState) {
  localState.updated_at = nowIso();
  localStorage.setItem(LOCAL_STATE_KEY, JSON.stringify(localState));
  return localState;
}

function updateLocalProfile(localState, payload) {
  ["level", "weekly_hours", "goal", "target_date"].forEach((key) => {
    if (key in payload) localState.profile[key] = payload[key];
  });
  localState.profile.updated_at = nowIso();
  recordLocalEvent(localState, "updated", "profile", "learner-profile", { profile: localState.profile });
}

function updateLocalProgress(localState, payload) {
  const lessonId = payload.lesson_id;
  const progress = localState.lesson_progress[lessonId] || { status: "not_started", confidence: 0, started_at: nowIso() };
  ["status", "confidence", "active_tab"].forEach((key) => {
    if (key in payload) progress[key] = payload[key];
  });
  if (payload.status === "completed") progress.completed_at = nowIso();
  if (payload.status === "mastered") progress.mastered_at = nowIso();
  progress.updated_at = nowIso();
  localState.lesson_progress[lessonId] = progress;
  recordLocalEvent(localState, "progressed", lessonId, "lesson", { progress });
}

function addLocalQuizAttempt(localState, payload) {
  const score = Number(payload.score || 0);
  const total = Number(payload.total || 0);
  const attempt = {
    id: cryptoId(),
    quiz_id: payload.quiz_id,
    lesson_id: payload.lesson_id,
    score,
    total,
    answers: payload.answers || [],
    percent: Math.round((100 * score) / Math.max(1, total)),
    created_at: nowIso(),
  };
  localState.quiz_attempts.push(attempt);
  recordLocalEvent(localState, "answered", attempt.quiz_id, "quiz", { attempt });
}

function addLocalEvidence(localState, payload) {
  const evidence = {
    id: cryptoId(),
    lesson_id: payload.lesson_id,
    gate_id: payload.gate_id,
    type: payload.type || "self-explanation",
    text: String(payload.text || "").trim(),
    confidence: Number(payload.confidence || 2),
    status: "submitted",
    created_at: nowIso(),
  };
  evidence.quality = scoreEvidence(evidence.text, evidence.confidence);
  localState.evidence.push(evidence);
  recordLocalEvent(localState, "submitted", evidence.lesson_id, "mastery-evidence", { evidence });
}

function addLocalReview(localState, payload) {
  const lessonId = payload.lesson_id;
  const quality = payload.quality || "good";
  const current = localState.reviews[lessonId] || {};
  const interval = nextInterval(Number(current.interval_days || 0), quality);
  const review = {
    lesson_id: lessonId,
    quality,
    interval_days: interval,
    last_reviewed_at: nowIso(),
    due_at: new Date(Date.now() + interval * 86400000).toISOString(),
    count: Number(current.count || 0) + 1,
  };
  localState.reviews[lessonId] = review;
  recordLocalEvent(localState, "reviewed", lessonId, "lesson", { review });
}

function saveLocalNote(localState, payload) {
  localState.notes[payload.lesson_id] = { text: payload.text || "", updated_at: nowIso() };
  recordLocalEvent(localState, "noted", payload.lesson_id, "lesson-note");
}

function updateLocalDiagnostic(localState, payload) {
  const itemById = new Map(DIAGNOSTIC_ITEMS.map((item) => [item.id, item]));
  const responses = payload.responses || (payload.item_id ? { [payload.item_id]: payload.level } : {});
  const normalized = {};
  Object.entries(responses).forEach(([itemId, rawLevel]) => {
    const item = itemById.get(itemId);
    if (!item) return;
    const level = Math.max(0, Math.min(3, Number(rawLevel) || 0));
    normalized[itemId] = { level, competency: item.competency, prompt: item.prompt, updated_at: nowIso() };
  });
  localState.diagnostics = { ...localState.diagnostics, ...normalized };
  recordLocalEvent(localState, "diagnosed", "self-assessment", "diagnostic", { responses: normalized });
}

function addLocalLabAttempt(localState, payload) {
  const attempt = {
    id: cryptoId(),
    lab_id: payload.lab_id,
    lesson_id: payload.lesson_id,
    summary: String(payload.summary || "").trim(),
    metrics: payload.metrics || {},
    created_at: nowIso(),
  };
  localState.lab_attempts.push(attempt);
  recordLocalEvent(localState, "ran", attempt.lab_id, "interactive-lab", { attempt });
}

function recordLocalEvent(localState, verb, objectId, objectType, result = {}, context = {}) {
  localState.events.push({
    id: cryptoId(),
    timestamp: nowIso(),
    actor: "browser learner",
    verb,
    object: { id: objectId, type: objectType },
    result,
    context,
  });
  localState.events = localState.events.slice(-500);
}

const COMPETENCIES = [
  { id: "foundations", title: "基础工程与张量直觉", description: "Python、shape、训练循环、概率和线代。" },
  { id: "modeling", title: "语言模型与 Transformer", description: "tokenizer、LM objective、attention、MLP、normalization、optimizer。" },
  { id: "math", title: "数学推导与资源核算", description: "softmax、cross entropy、FLOPs、显存、scaling law。" },
  { id: "systems", title: "系统优化与并行", description: "GPU/TPU、kernel、FlashAttention、data/tensor/pipeline parallel。" },
  { id: "evaluation", title: "推理、Scaling 与评测", description: "inference、KV cache、benchmark、contamination、scaling extrapolation。" },
  { id: "data", title: "数据管线", description: "数据来源、过滤、去重、混合、合成数据和许可风险。" },
  { id: "alignment", title: "后训练与对齐", description: "SFT、RLHF、DPO、RLVR、安全对齐和多模态。" },
];

const LESSON_COMPETENCIES = {
  "prep-python": ["foundations"],
  "prep-tensors": ["foundations", "math"],
  "prep-training-loop": ["foundations", "modeling"],
  l01: ["modeling", "math"],
  l02: ["math", "systems"],
  l03: ["modeling", "math"],
  l04: ["modeling", "systems"],
  l05: ["systems"],
  l06: ["systems", "math"],
  l07: ["systems"],
  l08: ["systems"],
  l09: ["math", "evaluation"],
  l10: ["evaluation", "systems"],
  l11: ["math", "evaluation"],
  l12: ["evaluation"],
  l13: ["data"],
  l14: ["data", "evaluation"],
  l15: ["alignment"],
  l16: ["alignment", "math"],
  l17: ["alignment", "modeling"],
  l18: ["evaluation"],
  l19: ["foundations", "modeling", "systems", "evaluation", "data", "alignment"],
};

const DIAGNOSTIC_ITEMS = [
  { id: "diag-shapes", competency: "foundations", prompt: "我能看懂 B、T、D、V 等 shape 约定，并能发现维度错误。" },
  { id: "diag-prob", competency: "math", prompt: "我能手算 softmax、cross entropy 和简单梯度更新。" },
  { id: "diag-transformer", competency: "modeling", prompt: "我能从 token ids 讲到 logits，包括 attention 和 MLP。" },
  { id: "diag-resources", competency: "systems", prompt: "我能估算 FLOPs、显存和判断 compute/memory bound。" },
  { id: "diag-eval", competency: "evaluation", prompt: "我能设计评测并说明 benchmark contamination 风险。" },
  { id: "diag-data", competency: "data", prompt: "我能设计数据过滤、去重、混合和污染控制流程。" },
  { id: "diag-align", competency: "alignment", prompt: "我能区分 SFT、RLHF、DPO、RLVR 和它们的训练信号。" },
];

function buildLearningModel(curriculum) {
  return {
    competencies: COMPETENCIES,
    diagnostic_items: DIAGNOSTIC_ITEMS,
    lesson_competencies: LESSON_COMPETENCIES,
    knowledge_graph: buildKnowledgeGraph(curriculum),
    cycle: [
      { id: "diagnose", title: "诊断", description: "先确认基础能力和学习目标。" },
      { id: "learn", title: "学习", description: "按官方课程顺序学习概念、数学和代码。" },
      { id: "practice", title: "实验", description: "用玩具实验把公式变成可观察结果。" },
      { id: "check", title: "自测", description: "用形成性测验发现误解。" },
      { id: "evidence", title: "证据", description: "写出解释、伪代码或实验分析。" },
      { id: "review", title: "复习", description: "按间隔复习巩固薄弱单元。" },
    ],
    rubric: { progress: 35, quiz: 20, evidence: 20, review: 15, diagnostic: 10 },
  };
}

function buildKnowledgeGraph(curriculum) {
  const nodes = COMPETENCIES.map((competency) => ({ id: competency.id, type: "competency", title: competency.title }));
  const edges = [];
  const lessonById = new Map(curriculum.lessons.map((lesson) => [lesson.id, lesson]));
  curriculum.roadmap.forEach((phase) => {
    let previous = null;
    phase.lessons.forEach((lessonId, index) => {
      const lesson = lessonById.get(lessonId);
      if (!lesson) return;
      nodes.push({
        id: lessonId,
        type: "lesson",
        title: lesson.title,
        lecture: lesson.lecture,
        phase: phase.id,
        order: index,
        competencies: LESSON_COMPETENCIES[lessonId] || [],
      });
      if (previous) edges.push({ source: previous, target: lessonId, type: "prerequisite" });
      previous = lessonId;
      (LESSON_COMPETENCIES[lessonId] || []).forEach((competencyId) => edges.push({ source: competencyId, target: lessonId, type: "covers" }));
    });
  });
  return { nodes, edges };
}

function buildDashboard(curriculum, localState) {
  const progress = localState.lesson_progress || {};
  const completed = Object.entries(progress).filter(([, item]) => ["completed", "mastered"].includes(item.status)).map(([id]) => id);
  const mastered = Object.entries(progress).filter(([, item]) => item.status === "mastered").map(([id]) => id);
  const phaseProgress = curriculum.roadmap.map((phase) => {
    const done = phase.lessons.filter((lessonId) => ["completed", "mastered"].includes(progress[lessonId]?.status)).length;
    return { id: phase.id, title: phase.title, done, total: phase.lessons.length, percent: Math.round((100 * done) / Math.max(1, phase.lessons.length)) };
  });
  return {
    profile: localState.profile,
    totals: {
      lessons: curriculum.lessons.length,
      completed: completed.length,
      mastered: mastered.length,
      evidence: localState.evidence.length,
      diagnostics: Object.keys(localState.diagnostics).length,
      lab_attempts: localState.lab_attempts.length,
      quiz_attempts: localState.quiz_attempts.length,
      events: localState.events.length,
    },
    mastery_snapshot: masterySnapshot(curriculum, localState),
    phase_progress: phaseProgress,
    due_reviews: buildReviewQueue(curriculum, localState),
    next_actions: computeNextActions(curriculum, localState),
    recent_events: [...localState.events].slice(-8).reverse(),
  };
}

function buildReviewQueue(curriculum, localState) {
  const lessonsById = new Map(curriculum.lessons.map((lesson) => [lesson.id, lesson]));
  return Object.entries(localState.lesson_progress || {})
    .filter(([, progress]) => ["completed", "mastered"].includes(progress.status))
    .map(([lessonId]) => {
      const review = localState.reviews[lessonId];
      const dueAt = review?.due_at ? Date.parse(review.due_at) : 0;
      if (review && dueAt > Date.now()) return null;
      const lesson = lessonsById.get(lessonId);
      if (!lesson) return null;
      return {
        lesson_id: lessonId,
        title: lesson.title,
        lecture: lesson.lecture,
        reason: review ? "到期复习" : "首次复习",
        due_at: review?.due_at || nowIso(),
      };
    })
    .filter(Boolean)
    .slice(0, 8);
}

function computeNextActions(curriculum, localState) {
  const actions = [];
  if (Object.keys(localState.diagnostics || {}).length < DIAGNOSTIC_ITEMS.length) {
    actions.push({ type: "diagnostic", title: "完成入门诊断", lesson_id: curriculum.lessons[0].id, reason: "先确认基础能力，系统才能把时间分配到数学、代码、系统或数据薄弱点。" });
  }
  const due = buildReviewQueue(curriculum, localState);
  if (due.length) actions.push({ type: "review", title: `复习：${due[0].lecture} · ${due[0].title}`, lesson_id: due[0].lesson_id, reason: "间隔复习到期，先巩固再学新内容。" });

  const nextLesson = curriculum.lessons.find((lesson) => !["completed", "mastered"].includes(localState.lesson_progress[lesson.id]?.status));
  if (nextLesson) actions.push({ type: "learn", title: `继续学习：${nextLesson.lecture} · ${nextLesson.title}`, lesson_id: nextLesson.id, reason: "这是当前路径中第一个未完成单元。" });

  const weakQuiz = weakestQuizArea(curriculum, localState);
  if (weakQuiz) actions.push(weakQuiz);
  if ((localState.evidence || []).length < 3) {
    actions.push({ type: "evidence", title: "提交一份掌握证据", lesson_id: actions[0]?.lesson_id || curriculum.lessons[0].id, reason: "学习闭环需要你写出解释或小实验结果，而不是只看页面。" });
  }
  return actions.slice(0, 4);
}

function weakestQuizArea(curriculum, localState) {
  const attempts = localState.quiz_attempts || [];
  if (!attempts.length) {
    return { type: "quiz", title: "完成一次形成性自测", lesson_id: curriculum.lessons[0].id, reason: "还没有测验记录，系统无法判断薄弱点。" };
  }
  const last = attempts[attempts.length - 1];
  if (last.percent < 80) {
    return { type: "quiz", title: `重做测验：${last.quiz_id}`, lesson_id: last.lesson_id || curriculum.lessons[0].id, reason: `最近一次得分 ${last.percent}%，未达到 80% 掌握线。` };
  }
  return null;
}

function buildMasteryReport(curriculum, localState) {
  const lessonRows = curriculum.lessons.map((lesson) => lessonMasteryRow(lesson, localState));
  const competencyRows = competencyMasteryRows(localState, lessonRows);
  const average = Math.round(lessonRows.reduce((sum, row) => sum + row.score, 0) / Math.max(1, lessonRows.length));
  return {
    generated_at: nowIso(),
    average_score: average,
    status: scoreStatus(average),
    rubric: buildLearningModel(curriculum).rubric,
    competencies: competencyRows,
    lessons: lessonRows,
    weak_lessons: [...lessonRows].sort((a, b) => a.score - b.score).slice(0, 6),
    weak_competencies: competencyRows.filter((item) => item.score < 75).sort((a, b) => a.score - b.score).slice(0, 4),
    blockers: learningBlockers(curriculum, localState, lessonRows, competencyRows),
  };
}

function masterySnapshot(curriculum, localState) {
  const report = buildMasteryReport(curriculum, localState);
  return {
    average_score: report.average_score,
    status: report.status,
    weak_competencies: report.weak_competencies.slice(0, 2),
    blockers: report.blockers.slice(0, 2),
  };
}

function lessonMasteryRow(lesson, localState) {
  const lessonId = lesson.id;
  const progress = localState.lesson_progress[lessonId] || {};
  const progressPoints = { not_started: 0, in_progress: 15, completed: 30, mastered: 35 }[progress.status || "not_started"] || 0;
  const quiz = latestQuizForLesson(localState, lessonId);
  const quizPoints = quiz ? Math.round((quiz.percent / 100) * 20) : 0;
  const evidence = bestEvidenceForLesson(localState, lessonId);
  const evidencePoints = evidencePointsFor(evidence);
  const review = localState.reviews[lessonId];
  let reviewPoints = review ? Math.min(15, Number(review.count || 0) * 5) : 0;
  if (review?.quality === "easy") reviewPoints = Math.min(15, reviewPoints + 3);
  const diagnosticPoints = diagnosticPointsForLesson(localState, lessonId);
  const score = Math.min(100, progressPoints + quizPoints + evidencePoints + reviewPoints + diagnosticPoints);
  return {
    lesson_id: lessonId,
    title: lesson.title,
    lecture: lesson.lecture,
    phase: lesson.phase,
    competencies: LESSON_COMPETENCIES[lessonId] || [],
    score,
    status: scoreStatus(score),
    components: { progress: progressPoints, quiz: quizPoints, evidence: evidencePoints, review: reviewPoints, diagnostic: diagnosticPoints },
    latest_quiz_percent: quiz?.percent ?? null,
    evidence_ready: Boolean(evidence?.quality?.ready_for_review),
    review_count: Number(review?.count || 0),
    next_step: lessonNextStep(score, progress.status || "not_started", quiz, evidence, review),
  };
}

function competencyMasteryRows(localState, lessonRows) {
  const lessonRowsById = new Map(lessonRows.map((row) => [row.lesson_id, row]));
  const diagnosticScores = diagnosticScoresByCompetency(localState);
  return COMPETENCIES.map((competency) => {
    const rows = Object.entries(LESSON_COMPETENCIES)
      .filter(([, compIds]) => compIds.includes(competency.id))
      .map(([lessonId]) => lessonRowsById.get(lessonId))
      .filter(Boolean);
    const lessonScore = Math.round(rows.reduce((sum, row) => sum + row.score, 0) / Math.max(1, rows.length));
    const diagnosticScore = diagnosticScores[competency.id] ?? null;
    const score = diagnosticScore == null ? Math.round(lessonScore * 0.85) : Math.round(lessonScore * 0.7 + diagnosticScore * 0.3);
    return {
      id: competency.id,
      title: competency.title,
      description: competency.description,
      score,
      status: scoreStatus(score),
      diagnostic_score: diagnosticScore,
      lesson_count: rows.length,
      weak_lessons: [...rows].sort((a, b) => a.score - b.score).slice(0, 3).map((row) => row.lesson_id),
    };
  });
}

function buildStudyPlan(curriculum, localState, weeks = 4) {
  const weekCount = Math.max(1, Math.min(8, Number(weeks || 4)));
  const weeklyHours = Number(localState.profile.weekly_hours || 10);
  const sessionsPerWeek = Math.max(3, Math.min(7, Math.round((weeklyHours * 60) / 70)));
  const rowsById = new Map(curriculum.lessons.map((lesson) => [lesson.id, lessonMasteryRow(lesson, localState)]));
  const pending = curriculum.lessons.filter((lesson) => rowsById.get(lesson.id).score < 75);
  const due = buildReviewQueue(curriculum, localState);
  const output = [];
  let cursor = 0;
  for (let weekIndex = 0; weekIndex < weekCount; weekIndex += 1) {
    const sessions = [];
    if (weekIndex === 0) {
      due.slice(0, 2).forEach((review) => sessions.push({ type: "review", title: `复习：${review.lecture} · ${review.title}`, lesson_id: review.lesson_id, minutes: 25, activities: ["回忆公式/代码路径", "用 again/hard/good/easy 记录复习质量"] }));
    }
    while (sessions.length < sessionsPerWeek && cursor < pending.length) {
      const lesson = pending[cursor];
      const row = rowsById.get(lesson.id);
      sessions.push({ type: "lesson", title: `${lesson.lecture} · ${lesson.title}`, lesson_id: lesson.id, minutes: 70, activities: activitiesForScore(row.score), target: row.next_step });
      cursor += 1;
    }
    if (sessions.length < sessionsPerWeek) {
      sessions.push({ type: "capstone", title: "阶段复盘与勘误", lesson_id: curriculum.lessons[curriculum.lessons.length - 1].id, minutes: 60, activities: ["整理错题", "补一份掌握证据", "对照官方材料修正笔记"], target: "把本周最弱的一个概念讲清楚。" });
    }
    output.push({ week: weekIndex + 1, hours: Math.round((sessions.reduce((sum, session) => sum + session.minutes, 0) / 60) * 10) / 10, sessions });
  }
  return {
    generated_at: nowIso(),
    weekly_hours: weeklyHours,
    sessions_per_week: sessionsPerWeek,
    rules: ["分数低于 75 的单元优先进入计划。", "到期复习在每周第一批 session 中优先安排。", "每个新单元必须覆盖概念、数学、代码和产出证据。"],
    weeks: output,
  };
}

function buildStaticExplanation(curriculum, topic) {
  const normalized = String(topic || "").trim().toLowerCase();
  const scored = curriculum.lessons
    .map((lesson) => {
      const haystack = lessonSearchText(lesson);
      const score = normalized.split(/\s+/).filter((word) => word && haystack.includes(word)).length + (normalized && haystack.includes(normalized) ? 3 : 0);
      return { score, lesson };
    })
    .filter((item) => item.score > 0)
    .sort((a, b) => b.score - a.score);
  const top = scored.length ? scored.slice(0, 3).map((item) => item.lesson) : curriculum.lessons.slice(0, 3);
  const first = top[0];
  const math = first.math?.[0] || {};
  return {
    topic,
    explanation: {
      plain: first.beginner_view,
      why_it_matters: first.summary,
      concepts: first.concepts.slice(0, 4).join("、"),
      math_anchor: {
        name: math.name || "核心公式",
        formula: math.formula || "",
        latex: math.latex || math.formula || "",
        mathml: math.mathml || "",
        kind: math.kind || "数学表达",
        validity: math.validity || "",
        explain: math.explain || "",
      },
      next_step: first.practice?.[0] || "回到课程卡片完成练习。",
    },
    relatedLessons: top,
  };
}

function latestQuizForLesson(localState, lessonId) {
  return (localState.quiz_attempts || []).filter((attempt) => attempt.lesson_id === lessonId).at(-1) || null;
}

function bestEvidenceForLesson(localState, lessonId) {
  return [...(localState.evidence || [])].filter((item) => item.lesson_id === lessonId).sort((a, b) => evidencePointsFor(b) - evidencePointsFor(a))[0] || null;
}

function evidencePointsFor(evidence) {
  if (!evidence) return 0;
  const quality = evidence.quality || {};
  return Math.min(20, Number(quality.length_score || 0) * 4 + Number(quality.confidence_score || 0) * 2 + (quality.ready_for_review ? 2 : 0));
}

function diagnosticScoresByCompetency(localState) {
  const groups = {};
  Object.values(localState.diagnostics || {}).forEach((item) => {
    groups[item.competency] = groups[item.competency] || [];
    groups[item.competency].push(Number(item.level || 0));
  });
  return Object.fromEntries(Object.entries(groups).map(([key, values]) => [key, Math.round((values.reduce((sum, value) => sum + value, 0) / Math.max(1, values.length) / 3) * 100)]));
}

function diagnosticPointsForLesson(localState, lessonId) {
  const scores = diagnosticScoresByCompetency(localState);
  const values = (LESSON_COMPETENCIES[lessonId] || []).map((compId) => scores[compId]).filter((value) => value != null);
  if (!values.length) return 0;
  return Math.round((values.reduce((sum, value) => sum + value, 0) / values.length / 100) * 10);
}

function learningBlockers(curriculum, localState, lessonRows, competencyRows) {
  const blockers = [];
  if (Object.keys(localState.diagnostics || {}).length < DIAGNOSTIC_ITEMS.length) blockers.push({ type: "diagnostic", title: "诊断未完成", reason: "系统缺少基础能力画像，学习计划只能按默认顺序推进。" });
  if ((localState.evidence || []).length < 3) blockers.push({ type: "evidence", title: "掌握证据不足", reason: "阅读记录不能证明你会推导、实现或解释。" });
  const weakCompetency = competencyRows.find((item) => item.score < 40);
  if (weakCompetency) blockers.push({ type: "competency", title: `${weakCompetency.title} 很薄弱`, reason: "该能力低于 40 分，会影响后续单元理解。" });
  const firstPending = lessonRows.find((item) => item.score < 25);
  if (firstPending) blockers.push({ type: "lesson", title: `当前入口：${firstPending.lecture} · ${firstPending.title}`, reason: firstPending.next_step });
  if (buildReviewQueue(curriculum, localState).length) blockers.push({ type: "review", title: "存在到期复习", reason: "复习队列到期后应优先处理，避免只学新内容。" });
  return blockers.slice(0, 5);
}

function scoreEvidence(text, confidence) {
  const length = String(text || "").length;
  const lengthScore = length >= 600 ? 3 : length >= 300 ? 2 : length >= 120 ? 1 : 0;
  const confidenceScore = Math.max(0, Math.min(3, Number(confidence || 0)));
  return { length_score: lengthScore, confidence_score: confidenceScore, ready_for_review: lengthScore >= 2 && confidenceScore >= 2 };
}

function nextInterval(previous, quality) {
  if (quality === "again") return 1;
  if (quality === "hard") return Math.max(1, Math.min(3, previous + 1));
  if (quality === "easy") return Math.max(4, previous ? previous * 2 : 7);
  return Math.max(2, previous ? previous * 2 : 3);
}

function scoreStatus(score) {
  if (score >= 90) return "掌握";
  if (score >= 75) return "达标";
  if (score >= 50) return "待巩固";
  if (score >= 25) return "刚入门";
  return "薄弱";
}

function lessonNextStep(score, progressStatus, quiz, evidence, review) {
  if (progressStatus === "not_started") return "先读总览，再完成数学和代码页面的逐条讲解。";
  if (!quiz) return "完成形成性自测，让系统知道误解在哪里。";
  if (quiz.percent < 80) return "重做测验，并把错题写成一条笔记。";
  if (!evidence?.quality?.ready_for_review) return "提交一份包含公式、shape 或伪代码的掌握证据。";
  if (!review) return "做一次间隔复习，确认不是短期记忆。";
  if (score < 75) return "回到官方材料，对照本项目解释补齐薄弱点。";
  return "可以进入下一个单元，同时保留后续复习。";
}

function activitiesForScore(score) {
  if (score < 25) return ["读总览", "列出核心概念", "手抄并解释公式符号", "运行对应互动实验"];
  if (score < 50) return ["逐行读代码", "完成互动实验", "做形成性自测", "记录错题"];
  if (score < 75) return ["补掌握证据", "复习错题", "对照官方材料修正理解"];
  return ["间隔复习", "把本讲内容讲给未来的自己", "进入下一讲"];
}

function nowIso() {
  return new Date().toISOString();
}

function cryptoId() {
  return globalThis.crypto?.randomUUID?.() || `${Date.now()}-${Math.random().toString(16).slice(2)}`;
}

function renderControls() {
  els.labSelect.innerHTML = state.data.labs
    .map((lab) => `<option value="${lab.id}">${escapeHtml(lab.title)}</option>`)
    .join("");
  els.quizSelect.innerHTML = state.data.quizzes
    .map((quiz) => `<option value="${quiz.id}">${escapeHtml(quiz.title)}</option>`)
    .join("");
}

function renderPhases(filter = "") {
  const query = filter.trim().toLowerCase();
  const lessonById = new Map(state.data.lessons.map((lesson) => [lesson.id, lesson]));
  const phases = state.data.roadmap
    .map((phase) => {
      const lessons = phase.lessons
        .map((id) => lessonById.get(id))
        .filter(Boolean)
        .filter((lesson) => !query || lessonSearchText(lesson).includes(query));
      return { ...phase, lessons };
    })
    .filter((phase) => phase.lessons.length);

  els.phaseList.innerHTML = phases
    .map(
      (phase) => `
        <section class="phase">
          <button class="phase-header" type="button">
            <span class="phase-title">${escapeHtml(phase.title)}</span>
            <span class="phase-meta">${escapeHtml(phase.duration)} · ${escapeHtml(phase.goal)}</span>
          </button>
          <div class="lesson-list">
            ${phase.lessons
              .map(
                (lesson) => `
                  <button class="lesson-button ${lesson.id === state.currentLessonId ? "active" : ""} ${state.completed.has(lesson.id) ? "done" : ""}" data-lesson="${lesson.id}" type="button">
                    <span class="dot"></span>
                    <span>${escapeHtml(lesson.lecture)} · ${escapeHtml(lesson.title)}</span>
                  </button>
                `,
              )
              .join("")}
          </div>
        </section>
      `,
    )
    .join("");

  els.phaseList.querySelectorAll("[data-lesson]").forEach((button) => {
    button.addEventListener("click", () => {
      state.currentLessonId = button.dataset.lesson;
      state.tab = "overview";
      document.querySelectorAll(".tab").forEach((tab) => tab.classList.toggle("active", tab.dataset.tab === "overview"));
      renderPhases(els.searchInput.value);
      renderLesson();
    });
  });
}

function renderLesson() {
  state.copyPayloads.clear();
  renderLessonHeader();
  const lesson = getCurrentLesson();
  if (state.tab === "overview") renderOverview(lesson);
  if (state.tab === "source") renderSource(lesson);
  if (state.tab === "math") renderMath(lesson);
  if (state.tab === "code") renderCode(lesson);
  if (state.tab === "practice") renderPractice(lesson);
  if (state.tab === "map") renderMap(lesson);
  if (state.tab === "mastery") renderMastery(lesson);
  if (state.tab === "system") renderSystem();
}

function renderLessonHeader() {
  const lesson = getCurrentLesson();
  els.lessonMeta.textContent = lesson.lecture;
  els.lessonTitle.textContent = lesson.title;
  els.markDone.textContent = state.completed.has(lesson.id) ? "取消完成" : "标记完成";
}

function renderOverview(lesson) {
  const assignments = state.data.assignments.filter((assignment) => assignment.maps_to.includes(lesson.id));
  els.lessonBody.innerHTML = `
    <div class="content-grid">
      <section class="info-band">
        <h3>初学者视角</h3>
        <p>${escapeHtml(lesson.beginner_view)}</p>
      </section>
      <section class="info-band blue">
        <h3>本讲要解决的问题</h3>
        <p>${escapeHtml(lesson.summary)}</p>
      </section>
      <section>
        <h3>核心概念</h3>
        <ul class="concept-list">
          ${lesson.concepts.map((concept) => `<li>${escapeHtml(concept)}</li>`).join("")}
        </ul>
      </section>
      <section>
        <h3>对应作业理解版</h3>
        <div class="assignment-list">
          ${
            assignments.length
              ? assignments
                  .map(
                    (assignment) => `
                      <article class="assignment-item">
                        <strong>${escapeHtml(assignment.title)}</strong>
                        <p class="small-text">${escapeHtml(assignment.goal)}</p>
                        <ul class="practice-list">
                          ${assignment.study_version.map((item) => `<li>${escapeHtml(item)}</li>`).join("")}
                        </ul>
                      </article>
                    `,
                  )
                  .join("")
              : `<article class="assignment-item"><span class="small-text">这一讲主要用于建立背景，会在后续作业中反复出现。</span></article>`
          }
        </div>
      </section>
      <section class="info-band amber">
        <h3>完成检查点</h3>
        <p>${escapeHtml(lesson.checkpoint)}</p>
      </section>
    </div>
  `;
}

function renderSource(lesson) {
  const material = lesson.official_material || {
    label: "官方课程页面",
    url: lesson.official_source,
    embed_url: "",
    download_url: lesson.official_source,
    kind: "schedule",
    usage_steps: [],
    focus_points: [],
    explanation_prompts: [],
  };
  const primaryMath = lesson.math?.[0];
  const materialFrame = material.embed_url
    ? `
      <iframe
        class="material-frame"
        src="${escapeHtml(material.embed_url)}"
        title="${escapeHtml(lesson.lecture)} 官方材料"
        loading="lazy"
      ></iframe>
    `
    : `
      <div class="material-placeholder">
        <strong>这讲没有可嵌入的官方讲义。</strong>
        <p>请使用下方按钮打开 CS336 官方课程页面，并按本页的阅读流程记录笔记。</p>
      </div>
    `;

  els.lessonBody.innerHTML = `
    <div class="content-grid source-layout">
      <section class="official-material-card">
        <div class="material-head">
          <div>
            <span class="source-badge">${escapeHtml(material.label || "官方材料")}</span>
            <h3>${escapeHtml(lesson.lecture)} · ${escapeHtml(lesson.title)}</h3>
          </div>
          <div class="material-actions">
            <a class="secondary-link" href="${escapeHtml(material.url)}" target="_blank" rel="noreferrer">打开官方材料</a>
            ${
              material.download_url && material.download_url !== material.url
                ? `<a class="ghost-link" href="${escapeHtml(material.download_url)}" target="_blank" rel="noreferrer">打开原始文件</a>`
                : ""
            }
          </div>
        </div>
        ${materialFrame}
        <p class="source-disclaimer">官方材料来自 Stanford CS336 页面或其官方 GitHub 讲义链接。本平台只做嵌入、跳转和中文学习拆解；事实边界以官方材料为准。</p>
      </section>

      <section class="source-guidance-grid">
        <article class="source-guide-card">
          <h3>原始材料阅读顺序</h3>
          <ol>
            ${(material.usage_steps || []).map((item) => `<li>${escapeHtml(item)}</li>`).join("")}
          </ol>
        </article>
        <article class="source-guide-card">
          <h3>本讲讲解对应点</h3>
          <ul>
            ${(material.focus_points || []).map((item) => `<li>${escapeHtml(item)}</li>`).join("")}
          </ul>
        </article>
      </section>

      <section class="source-guidance-grid">
        <article class="source-guide-card">
          <h3>从讲义回到公式</h3>
          ${
            primaryMath
              ? `
                <p class="small-text">先在官方材料中定位和下面公式同义的定义、推导或资源估算，再打开“数学”标签逐项解释符号。</p>
                ${formulaMarkup(primaryMath)}
                <p>${escapeHtml(primaryMath.explain)}</p>
              `
              : `<p class="small-text">这讲更偏概念或研究视角。请优先记录材料中的问题设定、实验指标和失败模式。</p>`
          }
        </article>
        <article class="source-guide-card">
          <h3>从讲义回到代码</h3>
          <p class="small-text">把官方材料中的实现路径压缩成最小代码骨架，确认输入、核心操作和输出。完整逐行解释在“代码”标签。</p>
          ${codePanel(lesson.code, detectLanguage(lesson.code), "本平台最小对应代码")}
        </article>
      </section>

      <section class="info-band amber">
        <h3>学习产出要求</h3>
        <ul class="practice-list">
          ${(material.explanation_prompts || []).map((item) => `<li>${escapeHtml(item)}</li>`).join("")}
          <li>完成后在右侧“掌握证据”中提交一段解释，必须同时包含官方材料引用位置、一个公式解释和一个代码对应点。</li>
        </ul>
      </section>
    </div>
  `;
}

function renderMath(lesson) {
  els.lessonBody.innerHTML = `
    <div class="content-grid">
      ${lesson.math
        .map(
          (item) => `
            <article class="math-block">
              <div class="math-title-row">
                <h3>${escapeHtml(item.name)}</h3>
                <span class="math-kind">${escapeHtml(item.kind || "数学表达")}</span>
              </div>
              ${formulaMarkup(item)}
              ${inlineCodeSource("LaTeX", item.latex || item.formula)}
              <p>${escapeHtml(item.explain)}</p>
              <p class="math-validity"><strong>适用范围：</strong>${escapeHtml(item.validity || "以官方材料为准。")}</p>
              ${formulaDetailMarkup(item.detail)}
            </article>
          `,
        )
        .join("")}
      <section class="info-band">
        <h3>数学学习方法</h3>
        <p>先确认每个符号代表什么，再确认维度是否匹配，最后用一个极小例子手算一次。CS336 的公式大多服务于代码实现和资源估算。</p>
      </section>
    </div>
  `;
}

function renderCode(lesson) {
  const explanation = lesson.code_explanation;
  els.lessonBody.innerHTML = `
    <div class="content-grid">
      <section>
        <h3>最小代码骨架</h3>
        ${codePanel(lesson.code, detectLanguage(lesson.code), "课程示例")}
      </section>
      ${codeExplanationMarkup(explanation)}
      <section class="info-band blue">
        <h3>读代码顺序</h3>
        <p>先看输入输出 shape，再找核心数学操作，最后看参数更新或缓存状态。不要先纠结工程细节。</p>
      </section>
    </div>
  `;
}

function renderPractice(lesson) {
  els.lessonBody.innerHTML = `
    <div class="content-grid">
      <section>
        <h3>练习任务</h3>
        <ul class="practice-list">
          ${lesson.practice.map((item) => `<li>${escapeHtml(item)}</li>`).join("")}
        </ul>
      </section>
      <section>
        <h3>术语速查</h3>
        <ul class="glossary-list">
          ${state.data.glossary
            .filter((item) => lessonSearchText(lesson).toLowerCase().includes(item.term.toLowerCase()))
            .slice(0, 6)
            .map((item) => `<li><strong>${escapeHtml(item.term)}</strong><br><span class="small-text">${escapeHtml(item.definition)}</span></li>`)
            .join("") || `<li><span class="small-text">本讲术语已经在核心概念中列出。</span></li>`}
        </ul>
      </section>
    </div>
  `;
}

function renderMap(lesson) {
  els.lessonBody.innerHTML = `
    <div class="knowledge-map">
      <div class="pipeline">
        ${[
          ["Data", "网页、代码、书籍、数学题"],
          ["Tokenizer", "文本切成 token id"],
          ["Model", "Transformer 预测下一个 token"],
          ["Systems", "FLOPs、显存、并行和 kernel"],
          ["Evaluation", "PPL、benchmark、污染检查"],
          ["Alignment", "SFT、RLHF、RLVR、安全"],
        ]
          .map((step) => `<div class="pipeline-step"><strong>${step[0]}</strong><span>${step[1]}</span></div>`)
          .join("")}
      </div>
      <div class="map-canvas-wrap">
        <canvas id="mapCanvas" aria-label="课程知识图"></canvas>
      </div>
      <section class="info-band">
        <h3>当前课程位置</h3>
        <p>${escapeHtml(lesson.lecture)} 位于 ${escapeHtml(findPhase(lesson.phase).title)}。它和整条链路的关系是：${escapeHtml(lesson.summary)}</p>
      </section>
    </div>
  `;
  requestAnimationFrame(() => drawCourseMap(lesson));
}

function renderMastery(lesson) {
  const gate = lesson.mastery_gate;
  els.lessonBody.innerHTML = `
    <div class="content-grid">
      <section class="info-band blue">
        <h3>官方来源边界</h3>
        <p>本讲按 CS336 官方主题组织。中文解释用于入门拆解；最终事实、作业要求和细节以官方材料为准。</p>
        <p><a href="${escapeHtml(lesson.official_source)}" target="_blank" rel="noreferrer">打开本讲官方材料</a></p>
      </section>
      <section class="info-band amber">
        <h3>精度说明</h3>
        <p>${escapeHtml(lesson.precision_note)}</p>
      </section>
      <section>
        <h3>${escapeHtml(gate.title)}</h3>
        <p class="small-text">只有能拿出下面这些证据，才算达到这一阶段的学习要求。</p>
        <ul class="practice-list">
          ${gate.required_evidence.map((item) => `<li>${escapeHtml(item)}</li>`).join("")}
        </ul>
      </section>
      <section>
        <h3>常见失败信号</h3>
        <ul class="practice-list">
          ${gate.failure_signals.map((item) => `<li>${escapeHtml(item)}</li>`).join("")}
        </ul>
      </section>
      <section>
        <h3>课程级准确性规则</h3>
        <ul class="practice-list">
          ${state.data.course.accuracy_policy.map((item) => `<li>${escapeHtml(item)}</li>`).join("")}
        </ul>
      </section>
      <section>
        <h3>课程设计要求映射</h3>
        <ul class="practice-list">
          ${state.data.course.official_requirements.map((item) => `<li>${escapeHtml(item)}</li>`).join("")}
        </ul>
      </section>
    </div>
  `;
}

function renderSystem() {
  const dashboard = state.dashboard;
  const report = state.masteryReport;
  const plan = state.studyPlan;
  const model = state.learningModel;
  if (!dashboard || !report || !plan || !model) {
    els.lessonBody.innerHTML = `<div class="content-grid"><section class="info-band">正在加载学习闭环...</section></div>`;
    return;
  }
  els.lessonBody.innerHTML = `
    <div class="content-grid">
      <section class="learning-hero">
        <div>
          <p class="eyebrow">Learning OS</p>
          <h3>CS336 学习操作系统</h3>
          <p>这里把诊断、课程学习、数学推导、代码理解、互动实验、形成性自测、掌握证据和间隔复习连成闭环。</p>
        </div>
        <div class="metric-grid">
          <div class="metric"><span>完成课程</span><strong>${dashboard.totals.completed}/${dashboard.totals.lessons}</strong></div>
          <div class="metric"><span>掌握均分</span><strong>${report.average_score}</strong></div>
          <div class="metric"><span>证据</span><strong>${dashboard.totals.evidence}</strong></div>
          <div class="metric"><span>实验记录</span><strong>${dashboard.totals.lab_attempts}</strong></div>
        </div>
      </section>
      <section>
        <h3>闭环流程</h3>
        <div class="cycle-row">${model.cycle.map((step, index) => cycleStep(step, index)).join("")}</div>
      </section>
      <section>
        <h3>下一步推荐</h3>
        <div class="action-list">${actionCards(dashboard.next_actions)}</div>
      </section>
      <section>
        <h3>能力模型</h3>
        <div class="competency-grid">${competencyCards(report.competencies)}</div>
      </section>
      <section>
        <h3>掌握报告</h3>
        ${masteryReportMarkup(report)}
      </section>
      <section>
        <h3>个性化学习计划</h3>
        ${studyPlanMarkup(plan)}
      </section>
      <section>
        <h3>入门诊断</h3>
        ${diagnosticPanel(model.diagnostic_items)}
      </section>
      <section>
        <h3>知识图谱</h3>
        ${knowledgeGraphMarkup(model.knowledge_graph, report)}
      </section>
      <section>
        <h3>阶段进度</h3>
        <div class="phase-progress-grid">
          ${dashboard.phase_progress
            .map(
              (phase) => `
                <article class="phase-progress-card">
                  <strong>${escapeHtml(phase.title)}</strong>
                  <span>${phase.done} / ${phase.total}</span>
                  <div class="progress-track"><div style="width:${phase.percent}%"></div></div>
                </article>
              `,
            )
            .join("")}
        </div>
      </section>
      <section>
        <h3>到期复习</h3>
        ${dashboard.due_reviews.length ? `<div class="action-list">${dashboard.due_reviews.map((item) => reviewCard(item)).join("")}</div>` : `<p class="small-text">当前没有到期复习。完成课程后这里会出现复习队列。</p>`}
      </section>
      <section>
        <h3>最近学习记录</h3>
        <div class="event-list">
          ${dashboard.recent_events.length ? dashboard.recent_events.map((event) => eventRow(event)).join("") : `<p class="small-text">还没有学习事件。完成课程、提交证据或测验后会出现在这里。</p>`}
        </div>
      </section>
    </div>
  `;
}

function renderLearningConsole() {
  if (!state.dashboard) return;
  els.nextActionPanel.innerHTML = `
    <div class="mini-dashboard">
      <div class="metric"><span>完成</span><strong>${state.dashboard.totals.completed}/${state.dashboard.totals.lessons}</strong></div>
      <div class="metric"><span>掌握</span><strong>${state.masteryReport?.average_score ?? 0}</strong></div>
      <div class="metric"><span>复习</span><strong>${state.dashboard.due_reviews.length}</strong></div>
      <div class="metric"><span>诊断</span><strong>${state.dashboard.totals.diagnostics}/${state.learningModel?.diagnostic_items?.length || 0}</strong></div>
    </div>
    ${actionCards(state.dashboard.next_actions.slice(0, 2))}
  `;
}

function renderAccountPanel() {
  renderAccountEntry();
  renderAccountModal();
  if (!els.accountPanel) return;
  if (els.cloudModeBadge) {
    els.cloudModeBadge.textContent = cloudBadgeText();
    els.cloudModeBadge.dataset.mode = cloudBadgeMode();
  }

  els.accountPanel.innerHTML = accountMarkup("panel");
}

function renderAccountEntry() {
  if (!els.accountOpen) return;
  const mode = cloudBadgeMode();
  const text = state.cloud.user ? "账号已登录" : "账号 / 登录";
  const hint = state.cloud.loading
    ? "检查中"
    : state.cloud.user
      ? "云端同步"
      : state.cloud.configured
        ? "可登录"
        : "本机保存";
  if (els.accountStatusDot) els.accountStatusDot.dataset.mode = mode;
  if (els.accountStatusText) els.accountStatusText.textContent = text;
  if (els.accountStatusHint) els.accountStatusHint.textContent = hint;
  els.accountOpen.dataset.mode = mode;
}

function renderAccountModal() {
  if (!els.accountModalBody) return;
  els.accountModalBody.innerHTML = accountMarkup("modal");
}

function accountMarkup(context) {
  if (state.cloud.loading) {
    return `<p class="small-text">正在检查账号与云同步配置...</p>`;
  }

  if (!state.cloud.configured) {
    return `
      <div class="account-user local-account">
        <strong>本机学习档案</strong>
        <span>云登录未配置，当前浏览器会继续保存学习进度。</span>
      </div>
      <p class="small-text">你现在仍可完整学习、提交证据、做测验和记录复习。要启用个人账号与跨设备同步，需要给 GitHub Pages 注入 Supabase URL 和 Anon Key。</p>
      <div class="cloud-facts">
        <span>离线可用</span>
        <span>本机保存</span>
        <span>登录待配置</span>
      </div>
      <div class="account-login-disabled">
        <label class="account-field" for="accountEmail-${escapeHtml(context)}">
          <span>邮箱登录</span>
          <input id="accountEmail-${escapeHtml(context)}" type="email" placeholder="配置云同步后启用" disabled />
        </label>
        <div class="account-actions">
          <button class="secondary-button" type="button" disabled>发送登录邮件</button>
          <button class="ghost-button" type="button" disabled>GitHub 登录</button>
        </div>
      </div>
      <p class="cloud-message warning">登录入口已在这里；当前部署还没有 Supabase 配置，所以暂时只能使用本机模式。</p>
    `;
  }

  if (!state.cloud.client) {
    return `
      <p class="small-text">云同步配置存在，但客户端初始化失败。</p>
      ${cloudMessageMarkup()}
    `;
  }

  if (!state.cloud.user) {
    return `
      <p class="small-text">登录后，系统会把本机学习状态与云端档案合并，并在每次学习行为后同步。</p>
      <label class="account-field" for="accountEmail-${escapeHtml(context)}">
        <span>邮箱</span>
        <input id="accountEmail-${escapeHtml(context)}" data-account-email type="email" placeholder="you@example.com" autocomplete="email" />
      </label>
      <div class="account-actions">
        <button class="secondary-button" type="button" data-cloud-action="magic">发送登录邮件</button>
        <button class="ghost-button" type="button" data-cloud-action="github">GitHub 登录</button>
      </div>
      ${cloudMessageMarkup()}
    `;
  }

  const email = state.cloud.user.email || state.cloud.user.user_metadata?.user_name || state.cloud.user.id;
  return `
    <div class="account-user">
      <strong>${escapeHtml(email)}</strong>
      <span>${escapeHtml(state.cloud.user.id)}</span>
    </div>
    <div class="cloud-facts">
      <span>云端同步</span>
      <span>${state.cloud.lastSync ? `最近 ${formatTime(state.cloud.lastSync)}` : "等待同步"}</span>
      <span>${state.cloud.syncing ? "同步中" : "就绪"}</span>
    </div>
    <div class="account-actions">
      <button class="secondary-button" type="button" data-cloud-action="sync">立即同步</button>
      <button class="ghost-button" type="button" data-cloud-action="signout">退出</button>
    </div>
    ${cloudMessageMarkup()}
  `;
}

function openAccountModal() {
  if (!els.accountModal) return;
  renderAccountModal();
  els.accountModal.hidden = false;
  document.body.classList.add("modal-open");
  window.setTimeout(() => {
    const focusTarget = els.accountModal.querySelector("input:not([disabled]), button:not([disabled]), a");
    focusTarget?.focus();
  }, 0);
}

function closeAccountModal() {
  if (!els.accountModal) return;
  els.accountModal.hidden = true;
  document.body.classList.remove("modal-open");
  els.accountOpen?.focus();
}

function cloudBadgeText() {
  if (state.cloud.loading) return "检查中";
  if (!state.cloud.configured) return "本机";
  if (state.cloud.error) return "异常";
  if (state.cloud.syncing) return "同步中";
  if (state.cloud.user) return "云端";
  return "未登录";
}

function cloudBadgeMode() {
  if (!state.cloud.configured) return "local";
  if (state.cloud.error) return "error";
  if (state.cloud.user) return "cloud";
  return "ready";
}

function cloudMessageMarkup() {
  const messages = [];
  if (state.cloud.message) messages.push(`<p class="cloud-message">${escapeHtml(state.cloud.message)}</p>`);
  if (state.cloud.error) messages.push(`<p class="cloud-message error">${escapeHtml(state.cloud.error)}</p>`);
  return messages.join("");
}

function formatTime(value) {
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return value;
  return date.toLocaleString("zh-CN", { month: "2-digit", day: "2-digit", hour: "2-digit", minute: "2-digit" });
}

function actionCards(actions) {
  if (!actions || actions.length === 0) return `<p class="small-text">暂无推荐动作。</p>`;
  return actions
    .map(
      (action) => `
        <article class="action-card" data-action-lesson="${escapeHtml(action.lesson_id || "")}">
          <span>${escapeHtml(action.type)}</span>
          <strong>${escapeHtml(action.title)}</strong>
          <p>${escapeHtml(action.reason)}</p>
          ${action.lesson_id ? `<button class="ghost-button action-jump" data-jump-lesson="${escapeHtml(action.lesson_id)}" type="button">打开</button>` : ""}
        </article>
      `,
    )
    .join("");
}

function reviewCard(item) {
  return `
    <article class="action-card">
      <span>${escapeHtml(item.reason)}</span>
      <strong>${escapeHtml(item.lecture)} · ${escapeHtml(item.title)}</strong>
      <p>复习后在右侧选择“重来/困难/掌握/轻松”，系统会安排下一次复习。</p>
      <button class="ghost-button action-jump" data-jump-lesson="${escapeHtml(item.lesson_id)}" type="button">打开</button>
    </article>
  `;
}

function eventRow(event) {
  return `
    <article class="event-row">
      <span>${escapeHtml(event.timestamp)}</span>
      <strong>${escapeHtml(event.verb)} · ${escapeHtml(event.object.type)}</strong>
      <p>${escapeHtml(event.object.id)}</p>
    </article>
  `;
}

function cycleStep(step, index) {
  return `
    <article class="cycle-step">
      <span>${index + 1}</span>
      <strong>${escapeHtml(step.title)}</strong>
      <p>${escapeHtml(step.description)}</p>
    </article>
  `;
}

function competencyCards(competencies) {
  return competencies
    .map(
      (item) => `
        <article class="competency-card">
          <div class="score-head">
            <strong>${escapeHtml(item.title)}</strong>
            <span>${item.score}</span>
          </div>
          ${scoreBar(item.score)}
          <p>${escapeHtml(item.description)}</p>
          <p class="small-text">状态：${escapeHtml(item.status)} · 关联 ${item.lesson_count} 个单元</p>
        </article>
      `,
    )
    .join("");
}

function masteryReportMarkup(report) {
  const weakLessons = report.weak_lessons || [];
  const blockers = report.blockers || [];
  return `
    <div class="mastery-layout">
      <article class="mastery-score-card">
        <span>课程掌握度</span>
        <strong>${report.average_score}</strong>
        <p>${escapeHtml(report.status)} · 评分由进度、测验、证据、复习和诊断组成。</p>
        ${componentRubric(report.rubric)}
      </article>
      <div class="weak-panel">
        <h4>当前阻塞</h4>
        ${blockers.length ? blockers.map((item) => blockerRow(item)).join("") : `<p class="small-text">暂时没有明显阻塞。继续按计划学习并保留证据。</p>`}
      </div>
      <div class="weak-panel">
        <h4>最低分单元</h4>
        ${weakLessons.map((item) => weakLessonRow(item)).join("")}
      </div>
    </div>
  `;
}

function componentRubric(rubric) {
  return `
    <div class="rubric-grid">
      ${Object.entries(rubric)
        .map(([key, value]) => `<span>${escapeHtml(key)} ${value}</span>`)
        .join("")}
    </div>
  `;
}

function blockerRow(item) {
  return `
    <article class="blocker-row">
      <strong>${escapeHtml(item.title)}</strong>
      <p>${escapeHtml(item.reason)}</p>
    </article>
  `;
}

function weakLessonRow(item) {
  return `
    <article class="weak-row">
      <div>
        <strong>${escapeHtml(item.lecture)} · ${escapeHtml(item.title)}</strong>
        <p>${escapeHtml(item.next_step)}</p>
      </div>
      <span>${item.score}</span>
      <button class="ghost-button action-jump" data-jump-lesson="${escapeHtml(item.lesson_id)}" type="button">打开</button>
    </article>
  `;
}

function studyPlanMarkup(plan) {
  return `
    <div class="plan-shell">
      <div class="plan-rules">
        <strong>计划规则</strong>
        <p class="small-text">每周 ${plan.weekly_hours} 小时，约 ${plan.sessions_per_week} 个学习 session。</p>
        <ul>${plan.rules.map((rule) => `<li>${escapeHtml(rule)}</li>`).join("")}</ul>
      </div>
      <div class="study-plan-grid">
        ${plan.weeks
          .map(
            (week) => `
              <article class="week-card">
                <div class="score-head">
                  <strong>第 ${week.week} 周</strong>
                  <span>${week.hours}h</span>
                </div>
                <div class="session-list">
                  ${week.sessions.map((session) => studySession(session)).join("")}
                </div>
              </article>
            `,
          )
          .join("")}
      </div>
    </div>
  `;
}

function studySession(session) {
  return `
    <article class="session-card">
      <span>${escapeHtml(session.type)} · ${session.minutes} min</span>
      <strong>${escapeHtml(session.title)}</strong>
      ${session.target ? `<p>${escapeHtml(session.target)}</p>` : ""}
      <ul>${session.activities.map((activity) => `<li>${escapeHtml(activity)}</li>`).join("")}</ul>
      ${session.lesson_id ? `<button class="ghost-button action-jump" data-jump-lesson="${escapeHtml(session.lesson_id)}" type="button">打开</button>` : ""}
    </article>
  `;
}

function diagnosticPanel(items) {
  const diagnostics = state.serverState?.diagnostics || {};
  return `
    <div class="diagnostic-panel">
      <p class="small-text">0 表示完全不会，3 表示能独立解释并写出最小代码或推导。保存后会影响能力模型和学习计划。</p>
      <div class="diagnostic-grid">
        ${items
          .map((item) => {
            const current = diagnostics[item.id]?.level ?? 0;
            return `
              <label class="diagnostic-item">
                <span>${escapeHtml(item.prompt)}</span>
                <select data-diagnostic-input="${escapeHtml(item.id)}">${diagnosticOptions(current)}</select>
              </label>
            `;
          })
          .join("")}
      </div>
      <button class="secondary-button" type="button" data-save-diagnostic>保存诊断</button>
    </div>
  `;
}

function diagnosticOptions(current) {
  return [
    [0, "0 · 不会"],
    [1, "1 · 听过"],
    [2, "2 · 能跟做"],
    [3, "3 · 能独立解释"],
  ]
    .map(([value, label]) => `<option value="${value}" ${Number(current) === value ? "selected" : ""}>${escapeHtml(label)}</option>`)
    .join("");
}

function knowledgeGraphMarkup(graph, report) {
  const competencyById = new Map((report.competencies || []).map((item) => [item.id, item]));
  const lessonNodes = graph.nodes.filter((node) => node.type === "lesson");
  return `
    <div class="graph-shell">
      <div class="graph-summary">
        <div class="metric"><span>节点</span><strong>${graph.nodes.length}</strong></div>
        <div class="metric"><span>依赖边</span><strong>${graph.edges.filter((edge) => edge.type === "prerequisite").length}</strong></div>
        <div class="metric"><span>能力覆盖</span><strong>${graph.edges.filter((edge) => edge.type === "covers").length}</strong></div>
      </div>
      <div class="graph-list">
        ${lessonNodes
          .slice(0, 12)
          .map((node) => {
            const score = masteryForLesson(node.id);
            return `
              <article class="graph-node">
                <span>${escapeHtml(node.lecture)}</span>
                <strong>${escapeHtml(node.title)}</strong>
                ${scoreBar(score)}
                <div class="tag-row">
                  ${node.competencies
                    .map((compId) => `<span title="${escapeHtml(competencyById.get(compId)?.title || compId)}">${escapeHtml(compId)}</span>`)
                    .join("")}
                </div>
              </article>
            `;
          })
          .join("")}
      </div>
      <p class="small-text">知识图谱显示课程依赖顺序和能力覆盖。这里先展示前 12 个节点，完整节点和边由 /api/learning-model 提供。</p>
    </div>
  `;
}

function masteryForLesson(lessonId) {
  const row = state.masteryReport?.lessons?.find((item) => item.lesson_id === lessonId);
  return row?.score ?? 0;
}

function scoreBar(score) {
  const clamped = Math.max(0, Math.min(100, Number(score) || 0));
  return `<div class="score-bar"><div style="width:${clamped}%"></div></div>`;
}

async function refreshLearningState(render = true) {
  const [dashboard, serverState, report, plan] = await Promise.all([
    apiGet("dashboard"),
    apiGet("state"),
    apiGet("mastery-report"),
    apiGet("study-plan"),
  ]);
  state.dashboard = dashboard;
  state.serverState = serverState;
  state.masteryReport = report;
  state.studyPlan = plan;
  state.completed = completedFromServer(state.serverState);
  renderLearningConsole();
  renderAccountPanel();
  updateProgress();
  renderPhases(els.searchInput.value);
  if (render) renderLesson();
}

function completedFromServer(serverState) {
  const completed = new Set();
  const progress = serverState?.lesson_progress || {};
  Object.entries(progress).forEach(([lessonId, item]) => {
    if (item.status === "completed" || item.status === "mastered") completed.add(lessonId);
  });
  return completed;
}

async function postJson(name, payload) {
  return apiPost(name, payload);
}

async function submitEvidence() {
  const text = els.evidenceText.value.trim();
  if (!text) {
    els.evidenceText.focus();
    return;
  }
  const lesson = getCurrentLesson();
  await postJson("evidence", {
    lesson_id: lesson.id,
    gate_id: lesson.mastery_gate?.id,
    type: "self-explanation",
    text,
    confidence: Number(els.evidenceConfidence.value),
  });
  els.evidenceText.value = "";
  await refreshLearningState();
}

async function submitReview(quality) {
  await postJson("review", { lesson_id: state.currentLessonId, quality });
  await refreshLearningState();
}

function renderLab() {
  const lab = state.data.labs.find((item) => item.id === state.activeLab);
  if (!lab) return;
  if (lab.id === "bpe") renderBpeLab(lab);
  if (lab.id === "attention") renderAttentionLab(lab);
  if (lab.id === "resources") renderResourcesLab(lab);
  if (lab.id === "scaling") renderScalingLab(lab);
  if (lab.id === "data") renderDataLab(lab);
  if (lab.id === "alignment") renderAlignmentLab(lab);
}

function labRecordButton(lab) {
  return `
    <button class="ghost-button lab-record-button" type="button" data-record-lab="${escapeHtml(lab.id)}" data-lesson-id="${escapeHtml(lab.lesson)}">
      记录实验结果
    </button>
  `;
}

function renderBpeLab(lab) {
  els.labPanel.innerHTML = `
    <p class="small-text">${escapeHtml(lab.description)}</p>
    ${editorShell("bpeText", "输入文本", "plain text", "low lower newest widest", 4)}
    <button id="bpeRun" class="secondary-button" type="button">执行一次合并</button>
    <div id="bpeOutput" class="metric-grid"></div>
    ${labRecordButton(lab)}
  `;
  document.querySelector("#bpeRun").addEventListener("click", () => {
    const text = document.querySelector("#bpeText").value;
    const result = runBpeStep(text);
    document.querySelector("#bpeOutput").innerHTML = `
      <div class="metric"><span>最常见相邻对</span><strong>${escapeHtml(result.pair)}</strong></div>
      <div class="metric"><span>出现次数</span><strong>${result.count}</strong></div>
      <div class="metric" style="grid-column: 1 / -1"><span>合并后 token</span><strong>${escapeHtml(result.tokens)}</strong></div>
    `;
  });
  document.querySelector("#bpeRun").click();
}

function renderAttentionLab(lab) {
  els.labPanel.innerHTML = `
    <p class="small-text">${escapeHtml(lab.description)}</p>
    <div class="lab-row"><label>Query 角度</label><input id="attQ" type="range" min="-2" max="2" step="0.1" value="1"></div>
    <div class="lab-row"><label>Key A</label><input id="attK1" type="range" min="-2" max="2" step="0.1" value="1.4"></div>
    <div class="lab-row"><label>Key B</label><input id="attK2" type="range" min="-2" max="2" step="0.1" value="-0.2"></div>
    <canvas id="labCanvas" aria-label="attention 权重图"></canvas>
    <div id="attentionMetrics" class="metric-grid"></div>
    ${labRecordButton(lab)}
  `;
  ["#attQ", "#attK1", "#attK2"].forEach((selector) => {
    document.querySelector(selector).addEventListener("input", updateAttentionLab);
  });
  updateAttentionLab();
}

function renderResourcesLab(lab) {
  els.labPanel.innerHTML = `
    <p class="small-text">${escapeHtml(lab.description)}</p>
    ${rangeControl("batch", "Batch", 1, 32, 4)}
    ${rangeControl("seq", "Seq", 64, 4096, 512)}
    ${rangeControl("hidden", "Hidden", 128, 4096, 768)}
    ${rangeControl("layers", "Layers", 1, 48, 12)}
    <div id="resourceMetrics" class="metric-grid"></div>
    ${labRecordButton(lab)}
  `;
  ["batch", "seq", "hidden", "layers"].forEach((id) => {
    document.querySelector(`#${id}`).addEventListener("input", updateResourcesLab);
  });
  updateResourcesLab();
}

function renderScalingLab(lab) {
  els.labPanel.innerHTML = `
    <p class="small-text">${escapeHtml(lab.description)}</p>
    ${rangeControl("params", "参数量 B", 0.1, 70, 7, 0.1)}
    ${rangeControl("tokens", "训练 token B", 1, 2000, 300, 1)}
    <canvas id="labCanvas" aria-label="scaling law 曲线"></canvas>
    <div id="scalingMetrics" class="metric-grid"></div>
    ${labRecordButton(lab)}
  `;
  ["params", "tokens"].forEach((id) => document.querySelector(`#${id}`).addEventListener("input", updateScalingLab));
  updateScalingLab();
}

function renderDataLab(lab) {
  const sampleDocs = `language models learn from data
language models learn from data
buy cheap products now !!!
Transformer attention improves sequence modeling
模型需要高质量中文数据`;
  els.labPanel.innerHTML = `
    <p class="small-text">${escapeHtml(lab.description)}</p>
    ${editorShell("dataText", "网页文本样本", "one document per line", sampleDocs, 7)}
    <button id="dataRun" class="secondary-button" type="button">过滤与去重</button>
    <div id="dataOutput" class="content-grid"></div>
    ${labRecordButton(lab)}
  `;
  document.querySelector("#dataRun").addEventListener("click", updateDataLab);
  updateDataLab();
}

function renderAlignmentLab(lab) {
  els.labPanel.innerHTML = `
    <p class="small-text">${escapeHtml(lab.description)}</p>
    <div class="lab-row"><label>Chosen reward</label><input id="chosenReward" type="range" min="-1" max="2" value="1" step="0.1"></div>
    <div class="lab-row"><label>Rejected reward</label><input id="rejectedReward" type="range" min="-1" max="2" value="0" step="0.1"></div>
    <div id="alignmentMetrics" class="metric-grid"></div>
    <div class="info-band blue">
      <p><strong>SFT</strong> 学 chosen 的 token；<strong>DPO</strong> 拉大 chosen/rejected 概率差；<strong>RLVR</strong> 用可验证 reward 直接给样本打分。</p>
    </div>
    ${labRecordButton(lab)}
  `;
  ["chosenReward", "rejectedReward"].forEach((id) => document.querySelector(`#${id}`).addEventListener("input", updateAlignmentLab));
  updateAlignmentLab();
}

function renderQuiz() {
  const quiz = state.data.quizzes.find((item) => item.id === state.activeQuiz);
  state.quizSelections = {};
  els.quizPanel.innerHTML = quiz.questions
    .map(
      (question, questionIndex) => `
      <section class="quiz-question">
        <p><strong>${questionIndex + 1}. ${escapeHtml(question.prompt)}</strong></p>
        <div class="quiz-options">
          ${question.options
            .map((option, optionIndex) => `<button data-q="${questionIndex}" data-o="${optionIndex}" type="button">${escapeHtml(option)}</button>`)
            .join("")}
        </div>
        <div class="answer-note" id="answer-${questionIndex}"></div>
      </section>
    `,
    )
    .join("") + `<button id="recordQuizAttempt" class="secondary-button" type="button">记录本次自测</button>`;

  els.quizPanel.querySelectorAll("button[data-q]").forEach((button) => {
    button.addEventListener("click", () => {
      const q = Number(button.dataset.q);
      const o = Number(button.dataset.o);
      const question = quiz.questions[q];
      state.quizSelections[q] = o;
      const optionButtons = els.quizPanel.querySelectorAll(`button[data-q="${q}"]`);
      optionButtons.forEach((item) => item.classList.remove("correct", "wrong"));
      button.classList.add(o === question.answer ? "correct" : "wrong");
      optionButtons[question.answer].classList.add("correct");
      document.querySelector(`#answer-${q}`).textContent = question.explain;
    });
  });
  document.querySelector("#recordQuizAttempt").addEventListener("click", () => submitQuizAttempt(quiz));
}

async function submitQuizAttempt(quiz) {
  const answers = quiz.questions.map((question, index) => ({
    question: question.prompt,
    selected: state.quizSelections[index],
    correct: question.answer,
    is_correct: state.quizSelections[index] === question.answer,
  }));
  const score = answers.filter((answer) => answer.is_correct).length;
  await postJson("quiz-attempt", {
    quiz_id: quiz.id,
    lesson_id: state.currentLessonId,
    score,
    total: quiz.questions.length,
    answers,
  });
  await refreshLearningState();
}

async function explainTopic() {
  const topic = els.explainInput.value.trim();
  if (!topic) return;
  els.explainResult.textContent = "正在整理解释...";
  const result = await postJson("explain", { topic });
  const anchor = result.explanation.math_anchor;
  els.explainResult.innerHTML = `
    <p><strong>直觉：</strong>${escapeHtml(result.explanation.plain)}</p>
    <p><strong>作用：</strong>${escapeHtml(result.explanation.why_it_matters)}</p>
    <p><strong>数学锚点：</strong>${escapeHtml(anchor.name)} · ${formulaMarkup(anchor, "inline")}</p>
    <p><span class="math-kind">${escapeHtml(anchor.kind || "数学表达")}</span></p>
    <p><strong>下一步：</strong>${escapeHtml(result.explanation.next_step)}</p>
  `;
}

function formulaMarkup(item, mode = "block") {
  if (item.mathml) {
    return `<div class="formula formula-${mode}">${item.mathml}</div>`;
  }
  return `<div class="formula formula-${mode}"><code>${escapeHtml(item.latex || item.formula || "")}</code></div>`;
}

function formulaDetailMarkup(detail) {
  if (!detail) return "";
  return `
    <div class="explanation-card">
      <div class="explanation-card-head">
        <h4>详细讲解</h4>
        <span>formula walkthrough</span>
      </div>
      <div class="formula-read">${escapeHtml(detail.read_as)}</div>
      <div class="detail-columns">
        <section>
          <h5>符号怎么读</h5>
          <ul>${detail.symbols.map((item) => `<li>${escapeHtml(item)}</li>`).join("")}</ul>
        </section>
        <section>
          <h5>理解步骤</h5>
          <ol>${detail.steps.map((item) => `<li>${escapeHtml(item)}</li>`).join("")}</ol>
        </section>
      </div>
      <section>
        <h5>常见误区</h5>
        <ul>${detail.pitfalls.map((item) => `<li>${escapeHtml(item)}</li>`).join("")}</ul>
      </section>
    </div>
  `;
}

function codeExplanationMarkup(explanation) {
  if (!explanation) return "";
  return `
    <section class="explanation-card code-explain">
      <div class="explanation-card-head">
        <h4>代码详细讲解</h4>
        <span>line by line</span>
      </div>
      <p>${escapeHtml(explanation.purpose)}</p>
      <p class="small-text">${escapeHtml(explanation.concept_link)}</p>
      <div class="detail-columns">
        <section>
          <h5>运行顺序</h5>
          <ol>${explanation.execution_order.map((item) => `<li>${escapeHtml(item)}</li>`).join("")}</ol>
        </section>
        <section>
          <h5>阅读重点</h5>
          <ul>
            <li>先看输入和输出分别是什么。</li>
            <li>再找核心数学操作对应的代码行。</li>
            <li>最后确认中间变量的 shape、单位或语义。</li>
          </ul>
        </section>
      </div>
      <div class="line-explain-list">
        ${explanation.line_notes
          .map(
            (note) => `
              <article class="line-explain">
                <div class="line-explain-code">
                  <span>${note.line}</span>
                  <code>${escapeHtml(note.code || " ")}</code>
                </div>
                <p>${escapeHtml(note.explain)}</p>
              </article>
            `,
          )
          .join("")}
      </div>
    </section>
  `;
}

function codePanel(code, language = "text", title = "Code") {
  const copyId = registerCopyPayload(code);
  const lines = code.replace(/\n+$/, "").split("\n");
  return `
    <div class="code-panel" data-language="${escapeHtml(language)}">
      <div class="code-toolbar">
        <div>
          <span class="code-title">${escapeHtml(title)}</span>
          <span class="code-language">${escapeHtml(language)}</span>
        </div>
        <button class="copy-button" type="button" data-copy-id="${copyId}" aria-label="复制代码">
          <span aria-hidden="true">⧉</span>
          <span>复制</span>
        </button>
      </div>
      <pre class="code-window"><code>${lines
        .map(
          (line, index) => `
            <span class="code-line">
              <span class="line-number">${index + 1}</span>
              <span class="line-code">${highlightCodeLine(line, language) || "&nbsp;"}</span>
            </span>
          `,
        )
        .join("")}</code></pre>
    </div>
  `;
}

function inlineCodeSource(label, code) {
  const copyId = registerCopyPayload(code);
  return `
    <div class="latex-source">
      <div class="source-header">
        <span>${escapeHtml(label)}</span>
        <button class="copy-button compact" type="button" data-copy-id="${copyId}" aria-label="复制 ${escapeHtml(label)}">
          <span aria-hidden="true">⧉</span>
          <span>复制</span>
        </button>
      </div>
      <code>${escapeHtml(code)}</code>
    </div>
  `;
}

function editorShell(id, title, language, value, rows) {
  const lineCount = Math.max(rows, value.split("\n").length);
  return `
    <div class="editor-shell">
      <div class="editor-toolbar">
        <div>
          <span class="code-title">${escapeHtml(title)}</span>
          <span class="code-language">${escapeHtml(language)}</span>
        </div>
        <span class="editor-count">${lineCount} lines</span>
      </div>
      <textarea
        id="${escapeHtml(id)}"
        class="code-editor"
        rows="${rows}"
        spellcheck="false"
        autocomplete="off"
        autocapitalize="off"
      >${escapeHtml(value)}</textarea>
    </div>
  `;
}

function registerCopyPayload(text) {
  const id = `copy-${state.copyPayloads.size + 1}`;
  state.copyPayloads.set(id, text);
  return id;
}

async function handleCopyClick(event) {
  const cloudAction = event.target.closest("[data-cloud-action]");
  if (cloudAction) {
    if (cloudAction.dataset.cloudAction === "magic") await sendMagicLink(cloudAction);
    if (cloudAction.dataset.cloudAction === "github") await signInWithGitHub();
    if (cloudAction.dataset.cloudAction === "sync") await manualCloudSync();
    if (cloudAction.dataset.cloudAction === "signout") await signOutCloud();
    return;
  }

  const diagnosticSave = event.target.closest("[data-save-diagnostic]");
  if (diagnosticSave) {
    await submitDiagnostic();
    return;
  }

  const labRecord = event.target.closest("[data-record-lab]");
  if (labRecord) {
    await recordLabAttempt(labRecord.dataset.recordLab, labRecord.dataset.lessonId);
    return;
  }

  const jump = event.target.closest("[data-jump-lesson]");
  if (jump) {
    state.currentLessonId = jump.dataset.jumpLesson;
    state.tab = "overview";
    document.querySelectorAll(".tab").forEach((tab) => tab.classList.toggle("active", tab.dataset.tab === "overview"));
    renderPhases(els.searchInput.value);
    renderLesson();
    return;
  }
  const button = event.target.closest("[data-copy-id]");
  if (!button) return;
  const payload = state.copyPayloads.get(button.dataset.copyId);
  if (payload == null) return;
  const label = button.querySelector("span:last-child");
  const original = label?.textContent || "复制";
  try {
    if (navigator.clipboard?.writeText) {
      await navigator.clipboard.writeText(payload);
    } else {
      fallbackCopy(payload);
    }
    if (label) label.textContent = "已复制";
    window.setTimeout(() => {
      if (label) label.textContent = original;
    }, 1200);
  } catch {
    fallbackCopy(payload);
    if (label) label.textContent = "已复制";
  }
}

function fallbackCopy(text) {
  const textarea = document.createElement("textarea");
  textarea.value = text;
  textarea.setAttribute("readonly", "");
  textarea.style.position = "fixed";
  textarea.style.left = "-9999px";
  document.body.appendChild(textarea);
  textarea.select();
  document.execCommand("copy");
  document.body.removeChild(textarea);
}

async function submitDiagnostic() {
  const responses = {};
  document.querySelectorAll("[data-diagnostic-input]").forEach((input) => {
    responses[input.dataset.diagnosticInput] = Number(input.value);
  });
  await postJson("diagnostic", { responses });
  await refreshLearningState();
}

async function recordLabAttempt(labId, lessonId) {
  const summary = els.labPanel.innerText.replace(/\s+/g, " ").trim().slice(0, 1000);
  await postJson("lab-attempt", {
    lab_id: labId,
    lesson_id: lessonId,
    summary,
    metrics: { captured_from: "browser-lab", current_lesson: state.currentLessonId },
  });
  await refreshLearningState(false);
  const button = document.querySelector(`[data-record-lab="${labId}"]`);
  if (button) {
    const original = button.textContent;
    button.textContent = "已记录";
    window.setTimeout(() => {
      button.textContent = original;
    }, 1200);
  }
}

function detectLanguage(code) {
  if (/\b(def|import|for|return|assert|from)\b/.test(code)) return "python";
  return "pseudo";
}

function highlightCodeLine(line, language) {
  if (!line) return "";
  if (language !== "python" && language !== "pseudo") return escapeHtml(line);

  const hashIndex = line.indexOf("#");
  const codePart = hashIndex >= 0 ? line.slice(0, hashIndex) : line;
  const commentPart = hashIndex >= 0 ? line.slice(hashIndex) : "";
  let html = escapeHtml(codePart);
  html = html.replace(/(&quot;.*?&quot;|'.*?')/g, '<span class="token-string">$1</span>');
  html = html.replace(/\b(def|return|for|in|if|else|from|import|assert|print|class|with|as|while|try|except)\b/g, '<span class="token-keyword">$1</span>');
  html = html.replace(/\b(True|False|None|inf)\b/g, '<span class="token-constant">$1</span>');
  html = html.replace(/\b(\d+(?:\.\d+)?)\b/g, '<span class="token-number">$1</span>');
  if (commentPart) html += `<span class="token-comment">${escapeHtml(commentPart)}</span>`;
  return html;
}

function runBpeStep(text) {
  const words = text
    .trim()
    .split(/\s+/)
    .filter(Boolean)
    .map((word) => [...word, "_"]);
  const pairs = new Map();
  for (const word of words) {
    for (let i = 0; i < word.length - 1; i += 1) {
      const key = `${word[i]} ${word[i + 1]}`;
      pairs.set(key, (pairs.get(key) || 0) + 1);
    }
  }
  const [pair, count] = [...pairs.entries()].sort((a, b) => b[1] - a[1])[0] || ["无", 0];
  const [left, right] = pair.split(" ");
  const merged = words.map((word) => {
    const output = [];
    for (let i = 0; i < word.length; i += 1) {
      if (word[i] === left && word[i + 1] === right) {
        output.push(left + right);
        i += 1;
      } else {
        output.push(word[i]);
      }
    }
    return output.join(" ");
  });
  return { pair, count, tokens: merged.join(" | ") };
}

function updateAttentionLab() {
  const q = Number(document.querySelector("#attQ").value);
  const k1 = Number(document.querySelector("#attK1").value);
  const k2 = Number(document.querySelector("#attK2").value);
  const scores = [q * k1, q * k2];
  const weights = softmax(scores);
  const values = [1.0, -0.5];
  const output = weights[0] * values[0] + weights[1] * values[1];
  document.querySelector("#attentionMetrics").innerHTML = `
    <div class="metric"><span>权重 A</span><strong>${weights[0].toFixed(3)}</strong></div>
    <div class="metric"><span>权重 B</span><strong>${weights[1].toFixed(3)}</strong></div>
    <div class="metric"><span>输出</span><strong>${output.toFixed(3)}</strong></div>
    <div class="metric"><span>公式</span><strong>softmax(QKᵀ)V</strong></div>
  `;
  drawBars(document.querySelector("#labCanvas"), weights, ["A", "B"], ["#236652", "#9b6214"]);
}

function updateResourcesLab() {
  const b = valueOf("batch");
  const t = valueOf("seq");
  const d = valueOf("hidden");
  const l = valueOf("layers");
  updateRangeLabels(["batch", "seq", "hidden", "layers"]);
  const mlpFlops = 16 * b * t * d * d * l;
  const attnFlops = 4 * b * t * t * d * l;
  const activationBytes = b * t * d * l * 4;
  const kvBytes = 2 * l * t * d * 2;
  document.querySelector("#resourceMetrics").innerHTML = `
    <div class="metric"><span>MLP FLOPs</span><strong>${formatNumber(mlpFlops)}</strong></div>
    <div class="metric"><span>Attention FLOPs</span><strong>${formatNumber(attnFlops)}</strong></div>
    <div class="metric"><span>激活显存</span><strong>${formatBytes(activationBytes)}</strong></div>
    <div class="metric"><span>KV cache</span><strong>${formatBytes(kvBytes)}</strong></div>
  `;
}

function updateScalingLab() {
  const params = valueOf("params");
  const tokens = valueOf("tokens");
  updateRangeLabels(["params", "tokens"]);
  const loss = predictedLoss(params, tokens);
  const compute = 6 * params * 1e9 * tokens * 1e9;
  document.querySelector("#scalingMetrics").innerHTML = `
    <div class="metric"><span>预测 loss</span><strong>${loss.toFixed(3)}</strong></div>
    <div class="metric"><span>训练计算</span><strong>${formatNumber(compute)}</strong></div>
  `;
  drawScalingCurve(document.querySelector("#labCanvas"), tokens, params);
}

function updateDataLab() {
  const docs = document.querySelector("#dataText").value.split("\n").map((line) => line.trim()).filter(Boolean);
  const quality = docs.filter((doc) => doc.length >= 12 && !/cheap|!!!|buy/i.test(doc));
  const unique = [];
  for (const doc of quality) {
    const tooSimilar = unique.some((seen) => jaccard(tokenizeWords(seen), tokenizeWords(doc)) > 0.75);
    if (!tooSimilar) unique.push(doc);
  }
  document.querySelector("#dataOutput").innerHTML = `
    <div class="metric-grid">
      <div class="metric"><span>原始文档</span><strong>${docs.length}</strong></div>
      <div class="metric"><span>质量过滤后</span><strong>${quality.length}</strong></div>
      <div class="metric"><span>去重后</span><strong>${unique.length}</strong></div>
      <div class="metric"><span>保留率</span><strong>${docs.length ? Math.round((unique.length / docs.length) * 100) : 0}%</strong></div>
    </div>
    <ul class="practice-list">${unique.map((doc) => `<li>${escapeHtml(doc)}</li>`).join("")}</ul>
  `;
}

function updateAlignmentLab() {
  const chosen = valueOf("chosenReward");
  const rejected = valueOf("rejectedReward");
  updateRangeLabels(["chosenReward", "rejectedReward"]);
  const margin = chosen - rejected;
  const preferenceProb = 1 / (1 + Math.exp(-margin));
  document.querySelector("#alignmentMetrics").innerHTML = `
    <div class="metric"><span>Reward 差</span><strong>${margin.toFixed(2)}</strong></div>
    <div class="metric"><span>偏好概率</span><strong>${preferenceProb.toFixed(3)}</strong></div>
    <div class="metric"><span>Advantage chosen</span><strong>${(chosen - (chosen + rejected) / 2).toFixed(2)}</strong></div>
    <div class="metric"><span>训练信号</span><strong>${margin > 0 ? "增强 chosen" : "检查偏好数据"}</strong></div>
  `;
}

function rangeControl(id, label, min, max, value, step = 1) {
  return `
    <div class="lab-row">
      <label for="${id}">${label}: <span id="${id}Value">${value}</span></label>
      <input id="${id}" type="range" min="${min}" max="${max}" step="${step}" value="${value}">
    </div>
  `;
}

function updateRangeLabels(ids) {
  ids.forEach((id) => {
    const input = document.querySelector(`#${id}`);
    const label = document.querySelector(`#${id}Value`);
    if (input && label) label.textContent = input.value;
  });
}

function drawCourseMap(lesson) {
  const canvas = document.querySelector("#mapCanvas");
  if (!canvas) return;
  const ctx = setupCanvas(canvas);
  const phases = state.data.roadmap;
  const activeIndex = phases.findIndex((phase) => phase.id === lesson.phase);
  const width = canvas.clientWidth;
  const height = canvas.clientHeight;
  ctx.clearRect(0, 0, width, height);

  const x0 = 38;
  const x1 = width - 38;
  const y = height / 2;
  ctx.lineWidth = 3;
  ctx.strokeStyle = "#d9d2c7";
  ctx.beginPath();
  ctx.moveTo(x0, y);
  ctx.lineTo(x1, y);
  ctx.stroke();

  phases.forEach((phase, index) => {
    const x = x0 + (index / (phases.length - 1)) * (x1 - x0);
    const active = index === activeIndex;
    ctx.beginPath();
    ctx.fillStyle = active ? "#236652" : index < activeIndex ? "#9b6214" : "#ffffff";
    ctx.strokeStyle = active ? "#236652" : "#65717d";
    ctx.lineWidth = 2;
    ctx.arc(x, y, active ? 14 : 10, 0, Math.PI * 2);
    ctx.fill();
    ctx.stroke();
    ctx.fillStyle = "#1f2933";
    ctx.font = "12px system-ui";
    ctx.textAlign = "center";
    ctx.fillText(`阶段 ${index}`, x, y + 36);
  });
}

function drawBars(canvas, values, labels, colors) {
  const ctx = setupCanvas(canvas);
  const width = canvas.clientWidth;
  const height = canvas.clientHeight;
  ctx.clearRect(0, 0, width, height);
  const max = Math.max(...values, 1);
  const barWidth = width / values.length - 36;
  values.forEach((value, index) => {
    const x = 24 + index * (barWidth + 36);
    const h = (height - 62) * (value / max);
    ctx.fillStyle = colors[index];
    ctx.fillRect(x, height - 38 - h, barWidth, h);
    ctx.fillStyle = "#1f2933";
    ctx.font = "13px system-ui";
    ctx.textAlign = "center";
    ctx.fillText(labels[index], x + barWidth / 2, height - 14);
    ctx.fillText(value.toFixed(3), x + barWidth / 2, height - 44 - h);
  });
}

function drawScalingCurve(canvas, tokens, activeParams) {
  const ctx = setupCanvas(canvas);
  const width = canvas.clientWidth;
  const height = canvas.clientHeight;
  ctx.clearRect(0, 0, width, height);
  const pad = 34;
  const xs = [0.1, 0.3, 1, 3, 7, 13, 30, 70];
  const losses = xs.map((p) => predictedLoss(p, tokens));
  const minLoss = Math.min(...losses) - 0.05;
  const maxLoss = Math.max(...losses) + 0.05;

  ctx.strokeStyle = "#d9d2c7";
  ctx.lineWidth = 1;
  ctx.beginPath();
  ctx.moveTo(pad, pad);
  ctx.lineTo(pad, height - pad);
  ctx.lineTo(width - pad, height - pad);
  ctx.stroke();

  ctx.strokeStyle = "#236652";
  ctx.lineWidth = 3;
  ctx.beginPath();
  xs.forEach((p, index) => {
    const x = pad + (Math.log10(p) - Math.log10(0.1)) / (Math.log10(70) - Math.log10(0.1)) * (width - 2 * pad);
    const y = height - pad - ((predictedLoss(p, tokens) - minLoss) / (maxLoss - minLoss)) * (height - 2 * pad);
    if (index === 0) ctx.moveTo(x, y);
    else ctx.lineTo(x, y);
  });
  ctx.stroke();

  const activeX = pad + (Math.log10(activeParams) - Math.log10(0.1)) / (Math.log10(70) - Math.log10(0.1)) * (width - 2 * pad);
  const activeY = height - pad - ((predictedLoss(activeParams, tokens) - minLoss) / (maxLoss - minLoss)) * (height - 2 * pad);
  ctx.fillStyle = "#9b6214";
  ctx.beginPath();
  ctx.arc(activeX, activeY, 6, 0, Math.PI * 2);
  ctx.fill();
  ctx.fillStyle = "#1f2933";
  ctx.font = "12px system-ui";
  ctx.fillText("params", width - 76, height - 10);
  ctx.fillText("loss", 8, 20);
}

function setupCanvas(canvas) {
  const ratio = window.devicePixelRatio || 1;
  const width = canvas.clientWidth;
  const height = canvas.clientHeight;
  canvas.width = Math.floor(width * ratio);
  canvas.height = Math.floor(height * ratio);
  const ctx = canvas.getContext("2d");
  ctx.setTransform(ratio, 0, 0, ratio, 0, 0);
  return ctx;
}

function softmax(xs) {
  const max = Math.max(...xs);
  const exps = xs.map((x) => Math.exp(x - max));
  const total = exps.reduce((sum, x) => sum + x, 0);
  return exps.map((x) => x / total);
}

function predictedLoss(params, tokens) {
  return 1.6 + 0.8 / params ** 0.34 + 1.1 / tokens ** 0.28;
}

function tokenizeWords(text) {
  return text.toLowerCase().split(/\W+/).filter(Boolean);
}

function jaccard(a, b) {
  const left = new Set(a);
  const right = new Set(b);
  const intersection = [...left].filter((item) => right.has(item)).length;
  const union = new Set([...left, ...right]).size || 1;
  return intersection / union;
}

function getCurrentLesson() {
  return state.data.lessons.find((lesson) => lesson.id === state.currentLessonId) || state.data.lessons[0];
}

function findPhase(phaseId) {
  return state.data.roadmap.find((phase) => phase.id === phaseId) || state.data.roadmap[0];
}

function lessonSearchText(lesson) {
  return [
    lesson.id,
    lesson.lecture,
    lesson.title,
    lesson.summary,
    lesson.beginner_view,
    lesson.concepts.join(" "),
    lesson.practice.join(" "),
  ]
    .join(" ")
    .toLowerCase();
}

function saveProgress() {
  localStorage.setItem("cs336.completed", JSON.stringify([...state.completed]));
}

function updateProgress() {
  const total = state.data.lessons.length;
  const done = state.completed.size;
  els.progressText.textContent = `${done} / ${total}`;
  els.progressBar.style.width = `${total ? (done / total) * 100 : 0}%`;
}

function valueOf(id) {
  return Number(document.querySelector(`#${id}`).value);
}

function formatNumber(value) {
  if (value >= 1e18) return `${(value / 1e18).toFixed(2)} EF`;
  if (value >= 1e15) return `${(value / 1e15).toFixed(2)} PF`;
  if (value >= 1e12) return `${(value / 1e12).toFixed(2)} TF`;
  if (value >= 1e9) return `${(value / 1e9).toFixed(2)} GF`;
  if (value >= 1e6) return `${(value / 1e6).toFixed(2)} MF`;
  return String(Math.round(value));
}

function formatBytes(value) {
  if (value >= 1024 ** 4) return `${(value / 1024 ** 4).toFixed(2)} TiB`;
  if (value >= 1024 ** 3) return `${(value / 1024 ** 3).toFixed(2)} GiB`;
  if (value >= 1024 ** 2) return `${(value / 1024 ** 2).toFixed(2)} MiB`;
  if (value >= 1024) return `${(value / 1024).toFixed(2)} KiB`;
  return `${value} B`;
}

function escapeHtml(value) {
  return String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}
