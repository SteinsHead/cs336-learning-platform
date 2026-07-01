# CS336 从零学习平台

这是一个本地全栈学习项目，用来从零理解 Stanford CS336: Language Modeling from Scratch 的完整知识链路。项目不训练真实模型，不需要 GPU，重点是理论、数学直觉、基础代码和交互实验。

## 启动

```bash
python3 backend/app.py
```

打开：

```text
http://127.0.0.1:8765
```

如果端口被占用：

```bash
python3 backend/app.py --port 8766
```

## GitHub Pages 部署

GitHub Pages 只能托管静态 HTML/CSS/JavaScript。这个项目因此支持两种运行模式：

- 本地开发：`backend/app.py` 提供 API，学习状态写入 `data/learning_state.json`。
- GitHub Pages：前端加载 `data/curriculum.json`，学习状态写入浏览器 `localStorage`。
- GitHub Pages + Supabase：前端仍由 Pages 托管，账号和学习状态写入 Supabase。

生成静态站点：

```bash
python3 -B scripts/export_static.py
```

构建产物会输出到：

```text
dist/
```

推送到 `main` 后，`.github/workflows/pages.yml` 会自动：

1. 检查 Python 模块语法。
2. 检查前端 JavaScript 语法。
3. 导出静态课程数据。
4. 校验课程单元和公式数量。
5. 上传 `dist/` 到 GitHub Pages。
6. 部署到 `https://<owner>.github.io/<repo>/`。

如果仓库名是 `<owner>.github.io`，则地址是 `https://<owner>.github.io/`。

## 账号与云同步

纯 GitHub Pages 不提供后端账号系统。本项目使用 Supabase 作为可选云端状态源：

```text
GitHub Pages 静态前端
  -> Supabase Auth 登录
  -> Supabase Postgres 保存学习状态
  -> Row Level Security 限制每个用户只能读写自己的数据
```

未配置 Supabase 时，系统会自动保持本机模式，学习状态保存在浏览器 `localStorage`。配置 Supabase 后：

- 未登录：继续本机保存。
- 登录后：本机状态与云端状态自动合并。
- 每次完成课程、测验、诊断、提交证据、复习和记录实验后自动同步。
- 支持邮箱 magic link 和 GitHub OAuth。

页面顶部始终显示“账号 / 登录”入口。未配置 Supabase 时，入口会明确显示“登录待配置”和本机保存状态；配置 Supabase 后，同一入口会切换成邮箱登录、GitHub 登录、立即同步和退出操作。

### Supabase 数据库

在 Supabase SQL Editor 执行：

```sql
-- 也可以直接复制 supabase/schema.sql
create table if not exists public.learning_states (
  user_id uuid primary key references auth.users(id) on delete cascade,
  state jsonb not null,
  updated_at timestamptz not null default now()
);

alter table public.learning_states enable row level security;

create policy "Users can read their own learning state"
on public.learning_states for select to authenticated
using (auth.uid() = user_id);

create policy "Users can insert their own learning state"
on public.learning_states for insert to authenticated
with check (auth.uid() = user_id);

create policy "Users can update their own learning state"
on public.learning_states for update to authenticated
using (auth.uid() = user_id)
with check (auth.uid() = user_id);
```

### GitHub 仓库 Variables

在 GitHub 仓库里设置：

```text
Settings -> Secrets and variables -> Actions -> Variables
```

新增：

```text
SUPABASE_URL=https://<project-ref>.supabase.co
SUPABASE_ANON_KEY=<anon public key>
SUPABASE_AUTH_REDIRECT_URL=https://steinshead.github.io/cs336-learning-platform/
```

`SUPABASE_ANON_KEY` 是浏览器端公开 key，不要使用 service role key。真正的数据隔离依赖 `supabase/schema.sql` 中的 RLS 策略。

### Supabase Auth Redirect

在 Supabase Dashboard 设置：

```text
Authentication -> URL Configuration
```

添加：

```text
Site URL: https://steinshead.github.io/cs336-learning-platform/
Redirect URLs:
https://steinshead.github.io/cs336-learning-platform/
```

## 项目结构

```text
backend/
  app.py        # Python 标准库 HTTP API 和静态文件服务
  content.py    # 课程路径、19 讲内容、作业映射、测验和术语表
  state.py      # 本地学习状态、能力模型、掌握度评分和学习计划
scripts/
  export_static.py # 导出 GitHub Pages 静态站点
frontend/
  index.html    # 单页学习工作台
  config.js      # 运行时配置；CI 可用 GitHub Variables 注入 Supabase 配置
  styles.css    # 响应式界面样式
  app.js        # 课程渲染、进度、交互实验和测验逻辑
supabase/
  schema.sql     # 云端学习状态表和 RLS 策略
.github/workflows/
  pages.yml     # GitHub Pages CI/CD
```

## 后端 API

```text
GET  /api/health
GET  /api/curriculum
GET  /api/lessons
GET  /api/lessons/{id}
GET  /api/roadmap
GET  /api/assignments
GET  /api/labs
GET  /api/glossary
GET  /api/quizzes/{id}
GET  /api/state
GET  /api/dashboard
GET  /api/learning-model
GET  /api/mastery-report
GET  /api/study-plan
GET  /api/next-actions
GET  /api/review-queue
POST /api/explain
POST /api/profile
POST /api/progress
POST /api/quiz-attempt
POST /api/evidence
POST /api/diagnostic
POST /api/lab-attempt
POST /api/review
POST /api/notes
POST /api/reset-state
```

## 学习内容覆盖

- 第 0 阶段：Python、张量、训练循环
- 第 1 阶段：tokenizer、资源核算、Transformer、attention、GPU、Triton
- 第 2 阶段：数据并行、张量并行、流水线并行
- 第 3 阶段：scaling law、推理、KV cache、评测
- 第 4 阶段：数据来源、过滤、去重、混合、合成数据
- 第 5 阶段：SFT、RLHF、RLVR、安全对齐、多模态、研究复盘

## 学习闭环平台设计

这个项目现在按“本地学习操作系统”设计，而不是静态课程页：

```text
诊断 -> 学习 -> 实验 -> 自测 -> 掌握证据 -> 间隔复习 -> 学习计划更新
```

核心模块：

- 能力模型：foundations、modeling、math、systems、evaluation、data、alignment。
- 入门诊断：7 个自评项，每项 0-3 分，影响掌握度和学习计划。
- 知识图谱：课程单元、能力覆盖和先修顺序都由 `/api/learning-model` 输出。
- 掌握度报告：每个 lesson 按进度 35、测验 20、证据 20、复习 15、诊断 10 加权评分。
- 个性化学习计划：优先安排低于 75 分的单元，并把到期复习放到每周前面。
- 学习事件流：诊断、实验、测验、证据、复习都写入 xAPI 风格事件。

后端会把个人学习行为保存到 `data/learning_state.json`，该文件已被 `data/.gitignore` 排除。

## 交互实验

- BPE tokenizer 单步合并
- Attention 权重手算
- FLOPs 与显存估算
- Scaling law 曲线模拟
- 数据过滤与 Jaccard 去重
- 偏好数据、reward 与 advantage 对比

每个实验都有“记录实验结果”按钮，记录后会进入学习事件流和实验统计。

## 建议用法

每次只学一个 lesson：先看总览，再打开“讲义”对照 Stanford 官方 PDF 或 lecture trace，接着看数学公式和代码骨架，完成互动实验和自测，最后提交掌握证据。闭环页会根据你的诊断、测验、证据和复习记录生成下一步计划。

## 官方讲义与课程材料

每个 lesson 都带有结构化的官方材料元数据：

- PDF 幻灯片会嵌入官方 GitHub raw 文件，并保留官方 GitHub 页面链接。
- lecture trace 会嵌入 Stanford CS336 官方 trace 页面。
- 预备课或无单独材料的客座课会回退到官方 schedule。
- “讲义”标签页会给出原始材料阅读顺序、本平台讲解对应点、公式回读、代码回读和掌握证据要求。

本项目不复制官方 PDF 或讲义正文，只做官方链接嵌入、跳转和中文学习拆解。

## 正确性与掌握标准

这个项目采用“官方材料对齐 + 掌握证据”的方式设计：

- 官方事实以 Stanford CS336 官网、官方 lecture materials 和 assignment handout 为准。
- 本项目的中文解释用于初学者拆解；如果和官方材料冲突，应以官方材料为准。
- 交互实验使用玩具数据和简化公式，不代表真实大模型训练。
- 每个阶段都有 mastery gate。只有能完成对应证据，才算达到这一阶段要求。

五个核心 mastery gate：

```text
入门：shape、softmax、cross entropy、训练循环
A1：tokenizer、Transformer forward、attention、optimizer、单测
A2：FLOPs、显存、FlashAttention、并行训练
A3：scaling law、KV cache、推理与评测
A4：数据过滤、去重、混合和污染风险
A5：SFT、RLHF、DPO、RLVR、多模态与安全对齐
```

## 数学公式渲染与审核

数学内容不使用远程 CDN 或图片。后端为每条公式提供：

- 原始公式文本
- 审核后的 LaTeX
- 原生 MathML
- 公式类型：严格定义、资源估算、教学简化、架构模式等
- 适用范围和常见误读边界

前端优先用浏览器原生 MathML 渲染公式，并显示 LaTeX 源，便于你对照官方讲义检查。

## 代码与编辑器呈现

代码和可编辑输入同样使用本地前端实现，不依赖远程高亮库：

- 课程代码块带语言标签、行号、轻量语法高亮和复制按钮。
- 实验输入区使用统一编辑器外壳、等宽字体、深色代码背景和稳定滚动。
- LaTeX 源码也提供复制按钮，便于和官方材料核对。

## 公式与代码讲解覆盖

每条公式都包含：

- 公式读法
- 符号解释
- 理解步骤
- 常见误区
- 适用范围

每段课程代码都包含：

- 代码目的
- 和本讲概念的关系
- 运行顺序
- 每一行代码的解释

项目内有覆盖率检查：22 个学习单元都必须有代码解释，29 条公式都必须有详细讲解。

前端新增：

- “闭环”主标签：显示能力模型、诊断、掌握报告、学习计划、知识图谱、阶段进度、复习队列和最近学习记录。
- 右侧学习控制台：提交掌握证据、记录复习结果、刷新推荐。
- 自测结果记录：完成测验后写入后端，用于判断薄弱点。
- 实验结果记录：完成互动实验后写入后端，纳入事件流。
- 间隔复习调度：根据 again/hard/good/easy 设置下一次复习时间。
