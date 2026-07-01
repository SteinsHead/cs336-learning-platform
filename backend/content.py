COURSE = {
    "title": "CS336 从零理解语言模型",
    "subtitle": "一个面向初学者的 Language Modeling from Scratch 学习路径",
    "source": "Stanford CS336 Spring 2026",
    "official_url": "https://cs336.stanford.edu/",
    "philosophy": [
        "先建立直觉，再写最小代码，最后回到数学和系统代价。",
        "所有实验都使用玩具数据和可视化，不需要真的训练大模型。",
        "每个主题都要回答三个问题：它解决什么问题，它的公式是什么，它在代码里长什么样。",
    ],
    "outcomes": [
        "能从字节、token、embedding 一直讲到 Transformer 训练。",
        "能手算 attention、cross entropy、FLOPs、显存和 scaling-law 的基本量级。",
        "能读懂一个小型语言模型训练代码的核心路径。",
        "能解释数据清洗、评测、推理和后训练为什么决定模型能力。",
    ],
    "accuracy_policy": [
        "官方事实以 Stanford CS336 官网、官方 lecture materials 和 assignment handout 为准。",
        "本项目的中文解释是教学拆解，不替代官方讲义；涉及近似公式、简化实验或伪代码时必须标注为简化版。",
        "学习完成的判定不以阅读时间为准，而以每阶段 mastery gate 的可验证产出为准。",
        "如果本项目内容和官方材料冲突，应以官方材料为准，并把冲突记录进勘误。",
    ],
    "official_requirements": [
        "能从头实现语言模型关键组件，而不是只会调用现成库。",
        "能进行资源核算：FLOPs、显存、带宽和 arithmetic intensity。",
        "能理解 GPU kernel、Triton、FlashAttention 和分布式训练的系统瓶颈。",
        "能理解 scaling laws、inference、evaluation、data pipeline 和 post-training/alignment。",
        "能用 Python/PyTorch 工程方式完成自测、实验记录和结果解释。",
    ],
}


SOURCE_MAP = {
    "course_scope": {
        "source": "Stanford CS336 official site",
        "url": "https://cs336.stanford.edu/",
        "claim": "Course walks through data collection/cleaning, transformer construction, training, evaluation, and deployment preparation.",
    },
    "assignments": {
        "source": "Stanford CS336 official assignments",
        "url": "https://cs336.stanford.edu/#coursework",
        "claim": "A1 Basics, A2 Systems, A3 Scaling, A4 Data, A5 Alignment and Reasoning RL.",
    },
    "schedule": {
        "source": "Stanford CS336 Spring 2026 schedule",
        "url": "https://cs336.stanford.edu/#schedule",
        "claim": "19 lecture meetings covering tokenization, PyTorch/resource accounting, architectures, attention/MoE, GPUs/TPUs, kernels/Triton, parallelism, scaling laws, inference, evaluation, data, post-training, RLVR, alignment and guest lectures.",
    },
}


ROADMAP = [
    {
        "id": "phase-0",
        "title": "第 0 阶段：入门补课",
        "duration": "1-2 周",
        "goal": "把 Python、张量、概率、训练循环补到能读懂课程代码。",
        "deliverable": "写出一个线性分类器和一个最小 PyTorch 训练 loop。",
        "lessons": ["prep-python", "prep-tensors", "prep-training-loop"],
    },
    {
        "id": "phase-1",
        "title": "第 1 阶段：语言模型基础",
        "duration": "3 周",
        "goal": "理解 tokenizer、embedding、Transformer、optimizer 和最小 LM 训练。",
        "deliverable": "不用 GPU，跑通一个玩具字符级/词级语言模型的前向传播和 loss。",
        "lessons": ["l01", "l02", "l03", "l04", "l05", "l06"],
    },
    {
        "id": "phase-2",
        "title": "第 2 阶段：系统与效率",
        "duration": "2 周",
        "goal": "学会用 FLOPs、显存、带宽和并行策略解释训练为什么贵。",
        "deliverable": "能对一个 Transformer 配置估算计算量、显存和瓶颈。",
        "lessons": ["l07", "l08"],
    },
    {
        "id": "phase-3",
        "title": "第 3 阶段：Scaling、推理、评测",
        "duration": "2 周",
        "goal": "理解模型能力如何随参数、数据和算力变化，以及如何评测。",
        "deliverable": "完成 scaling-law、KV cache 和 benchmark 污染的解释报告。",
        "lessons": ["l09", "l10", "l11", "l12"],
    },
    {
        "id": "phase-4",
        "title": "第 4 阶段：数据",
        "duration": "2 周",
        "goal": "理解预训练数据从网页到 token 流的处理链路。",
        "deliverable": "设计一套小规模过滤、去重和数据混合方案。",
        "lessons": ["l13", "l14"],
    },
    {
        "id": "phase-5",
        "title": "第 5 阶段：后训练与对齐",
        "duration": "2-3 周",
        "goal": "理解 SFT、RLHF、RLVR、安全对齐和多模态的核心思想。",
        "deliverable": "写出一个不训练大模型的 GRPO/DPO 伪代码解释和误差分析。",
        "lessons": ["l15", "l16", "l17", "l18", "l19"],
    },
]


MASTERY_GATES = [
    {
        "id": "gate-0",
        "title": "入门门槛：能读懂课程代码",
        "phase": "phase-0",
        "required_evidence": [
            "能写出 shape 注释并解释 B、T、D、V 分别代表什么。",
            "能手算 softmax、cross entropy 和一次梯度下降更新。",
            "能写出最小训练循环，并解释 zero_grad/backward/step 的顺序。",
        ],
        "failure_signals": [
            "只能背公式，无法把公式和张量形状对应起来。",
            "看到 logits、targets、loss 不知道各自 shape。",
        ],
    },
    {
        "id": "gate-a1",
        "title": "A1 门槛：从 token 到最小 Transformer LM",
        "phase": "phase-1",
        "required_evidence": [
            "能解释并手工模拟 BPE merge，说明 tokenizer 的 encode/decode 边界。",
            "能写出 decoder-only Transformer 的前向路径：token ids -> embeddings -> blocks -> logits。",
            "能手算一个 2-token attention 例子，包括 QK^T、softmax 和加权 V。",
            "能解释 causal mask、residual、normalization、MLP 和 AdamW 分别解决什么问题。",
            "能写单测验证每个模块的 shape、数值稳定性和边界情况。",
        ],
        "failure_signals": [
            "把 attention 理解成数据库查询，但无法写出 softmax(QK^T/sqrt(d))V。",
            "能调用 PyTorch module，但无法说明 logits 如何变成 cross entropy loss。",
        ],
    },
    {
        "id": "gate-a2",
        "title": "A2 门槛：系统效率与并行训练",
        "phase": "phase-2",
        "required_evidence": [
            "给定 B、T、D、层数，能估算 MLP/attention FLOPs 和主要激活显存。",
            "能区分 compute-bound 与 memory-bound，并用 roofline 直觉解释瓶颈。",
            "能说明 FlashAttention 是 exact attention，核心收益来自 IO-aware 分块和 online softmax。",
            "能比较 data parallel、tensor parallel、pipeline parallel、FSDP/ZeRO 的拆分对象和通信成本。",
        ],
        "failure_signals": [
            "只说多卡会更快，却无法解释 all-reduce 或 pipeline bubble。",
            "认为 FlashAttention 改变了 attention 数学公式。",
        ],
    },
    {
        "id": "gate-a3",
        "title": "A3 门槛：Scaling、推理与评测",
        "phase": "phase-3",
        "required_evidence": [
            "能解释 scaling law 的 N、D、C、loss 和不可约误差项。",
            "能说明 compute-optimal training 为什么需要平衡参数量和 token 数。",
            "能区分 prefill 与 decode，并估算 KV cache 的显存量级。",
            "能设计一个评测方案并指出 contamination、overfitting benchmark 和指标单一化风险。",
        ],
        "failure_signals": [
            "把 benchmark 分数等同于真实能力。",
            "认为上下文越长只增加一点点推理成本。",
        ],
    },
    {
        "id": "gate-a4",
        "title": "A4 门槛：数据管线",
        "phase": "phase-4",
        "required_evidence": [
            "能画出 raw web dump -> extraction -> filtering -> dedup -> mixing -> tokenization 的流程。",
            "能解释 language id、质量过滤、exact/near dedup 和数据混合权重。",
            "能用 Jaccard/MinHash 直觉说明 near-duplicate 检测。",
            "能说明数据许可、隐私、污染和合成数据的主要风险。",
        ],
        "failure_signals": [
            "认为只要数据越多越好。",
            "无法区分重复数据、低质量数据和评测污染。",
        ],
    },
    {
        "id": "gate-a5",
        "title": "A5 门槛：后训练、推理 RL 与对齐",
        "phase": "phase-5",
        "required_evidence": [
            "能区分 pretraining、SFT、RLHF、DPO、RLVR 的训练信号。",
            "能写出 SFT loss、偏好对 chosen/rejected、advantage 和 KL penalty 的含义。",
            "能设计一个可验证奖励函数，并指出 reward hacking 和过程不可控风险。",
            "能解释多模态对齐为什么需要 encoder/projector/语言模型之间的表示桥接。",
        ],
        "failure_signals": [
            "把 RLHF 和 RLVR 都理解成人类打分。",
            "只关注最终答案奖励，不考虑推理过程和安全约束。",
        ],
    },
]


LESSON_SOURCE_URLS = {
    "l01": "https://cs336.stanford.edu/lectures/?trace=lecture_01",
    "l02": "https://cs336.stanford.edu/lectures/?trace=lecture_02",
    "l03": "https://github.com/stanford-cs336/lectures/blob/main/lecture_03.pdf",
    "l04": "https://github.com/stanford-cs336/lectures/blob/main/lecture_04.pdf",
    "l05": "https://github.com/stanford-cs336/lectures/blob/main/lecture_05.pdf",
    "l06": "https://cs336.stanford.edu/lectures/?trace=lecture_06",
    "l07": "https://cs336.stanford.edu/lectures/?trace=lecture_07",
    "l08": "https://github.com/stanford-cs336/lectures/blob/main/lecture_08.pdf",
    "l09": "https://github.com/stanford-cs336/lectures/blob/main/lecture_09.pdf",
    "l10": "https://cs336.stanford.edu/lectures/?trace=lecture_10",
    "l11": "https://github.com/stanford-cs336/lectures/blob/main/lecture_11.pdf",
    "l12": "https://cs336.stanford.edu/lectures/?trace=lecture_12",
    "l13": "https://cs336.stanford.edu/lectures/?trace=lecture_13",
    "l14": "https://cs336.stanford.edu/lectures/?trace=lecture_14",
    "l15": "https://github.com/stanford-cs336/lectures/blob/main/lecture_15.pdf",
    "l16": "https://github.com/stanford-cs336/lectures/blob/main/lecture_16.pdf",
    "l17": "https://cs336.stanford.edu/lectures/?trace=lecture_17",
}


def raw_github_material_url(url):
    marker = "https://github.com/stanford-cs336/lectures/blob/main/"
    if url.startswith(marker):
        return "https://raw.githubusercontent.com/stanford-cs336/lectures/main/" + url.removeprefix(marker)
    return url


def official_material_for(lesson):
    url = LESSON_SOURCE_URLS.get(lesson["id"], SOURCE_MAP["schedule"]["url"])
    material_url = raw_github_material_url(url)
    if url.endswith(".pdf"):
        kind = "slides-pdf"
        label = "官方 PDF 幻灯片"
        embed_url = material_url
    elif "trace=lecture_" in url:
        kind = "lecture-trace"
        label = "官方 lecture trace"
        embed_url = url
    else:
        kind = "schedule"
        label = "官方课程页面"
        embed_url = ""

    return {
        "kind": kind,
        "label": label,
        "url": url,
        "embed_url": embed_url,
        "download_url": material_url,
        "source_label": "Stanford CS336 official course materials",
        "usage_steps": [
            "先浏览官方材料的目录、标题和例子，不急着记住每个细节。",
            "再回到本平台的总览，确认本讲到底在解决哪个语言模型问题。",
            "打开数学标签，把讲义中的公式逐项对应到符号、shape、单位或概率含义。",
            "打开代码标签，把讲义中的实现路径对应到最小代码骨架。",
            "最后提交掌握证据：用自己的话解释一个公式、一个代码片段和一个常见误区。",
        ],
        "focus_points": [
            f"本讲主题：{lesson['summary']}",
            "优先找出和本平台数学页相同的公式或资源估算关系。",
            "优先找出和本平台代码页相同的变量名、张量 shape 或训练流程。",
            "遇到讲义细节和本平台解释不一致时，以官方材料为准，并记录到学习证据里。",
        ],
        "explanation_prompts": [
            "这份官方材料里哪一页或哪一段最能说明本讲核心问题？",
            "材料中的符号如何对应到代码变量和张量形状？",
            "如果要用玩具例子复现本讲，你会保留哪些最小组件？",
        ],
    }


FORMULA_AUDIT = {
    "X in R^(batch x seq x d_model)": {
        "latex": r"X \in \mathbb{R}^{B \times T \times d_{\mathrm{model}}}",
        "kind": "shape 约定",
        "validity": "严格。这里 B 是 batch size，T 是 sequence length，d_model 是隐藏维度。",
        "mathml": '<math display="block"><mi>X</mi><mo>&#x2208;</mo><msup><mi>&#x211D;</mi><mrow><mi>B</mi><mo>&#x00D7;</mo><mi>T</mi><mo>&#x00D7;</mo><msub><mi>d</mi><mtext>model</mtext></msub></mrow></msup></math>',
    },
    "softmax(z_i) = exp(z_i) / sum_j exp(z_j)": {
        "latex": r"\operatorname{softmax}(z)_i = \frac{e^{z_i}}{\sum_{j=1}^{V} e^{z_j}}",
        "kind": "严格定义",
        "validity": "严格。实际代码应使用减去 max(z) 的数值稳定写法；数学结果不变。",
        "mathml": '<math display="block"><msub><mrow><mi>softmax</mi><mo>(</mo><mi>z</mi><mo>)</mo></mrow><mi>i</mi></msub><mo>=</mo><mfrac><msup><mi>e</mi><msub><mi>z</mi><mi>i</mi></msub></msup><mrow><msubsup><mo>&#x2211;</mo><mrow><mi>j</mi><mo>=</mo><mn>1</mn></mrow><mi>V</mi></msubsup><msup><mi>e</mi><msub><mi>z</mi><mi>j</mi></msub></msup></mrow></mfrac></math>',
    },
    "CE = -log p(target)": {
        "latex": r"\mathrm{CE}(y,p) = -\log p_y",
        "kind": "严格定义",
        "validity": "严格，适用于 one-hot target 的单样本交叉熵。batch/sequence loss 通常再对 token 求和或平均。",
        "mathml": '<math display="block"><mi>CE</mi><mo>(</mo><mi>y</mi><mo>,</mo><mi>p</mi><mo>)</mo><mo>=</mo><mo>-</mo><mi>log</mi><msub><mi>p</mi><mi>y</mi></msub></math>',
    },
    "theta <- theta - lr * grad_theta L": {
        "latex": r"\theta \leftarrow \theta - \eta \nabla_{\theta} L(\theta)",
        "kind": "优化更新",
        "validity": "严格表达 vanilla gradient descent。AdamW 等优化器会使用动量、方差估计和 decoupled weight decay。",
        "mathml": '<math display="block"><mi>&#x03B8;</mi><mo>&#x2190;</mo><mi>&#x03B8;</mi><mo>-</mo><mi>&#x03B7;</mi><msub><mo>&#x2207;</mo><mi>&#x03B8;</mi></msub><mi>L</mi><mo>(</mo><mi>&#x03B8;</mi><mo>)</mo></math>',
    },
    "p(x_1,...,x_T)=prod_t p(x_t | x_<t)": {
        "latex": r"p(x_{1:T}) = \prod_{t=1}^{T} p(x_t \mid x_{<t})",
        "kind": "链式法则",
        "validity": "严格。自回归语言模型用这个分解建模整段序列概率。",
        "mathml": '<math display="block"><mi>p</mi><mo>(</mo><msub><mi>x</mi><mrow><mn>1</mn><mo>:</mo><mi>T</mi></mrow></msub><mo>)</mo><mo>=</mo><msubsup><mo>&#x220F;</mo><mrow><mi>t</mi><mo>=</mo><mn>1</mn></mrow><mi>T</mi></msubsup><mi>p</mi><mo>(</mo><msub><mi>x</mi><mi>t</mi></msub><mo>|</mo><msub><mi>x</mi><mrow><mo>&lt;</mo><mi>t</mi></mrow></msub><mo>)</mo></math>',
    },
    "L = -sum_t log p(x_t | x_<t)": {
        "latex": r"L = -\sum_{t=1}^{T} \log p_{\theta}(x_t \mid x_{<t})",
        "kind": "训练目标",
        "validity": "严格。实现中常对非 padding token 求平均；有些代码还会按 batch 维度聚合。",
        "mathml": '<math display="block"><mi>L</mi><mo>=</mo><mo>-</mo><msubsup><mo>&#x2211;</mo><mrow><mi>t</mi><mo>=</mo><mn>1</mn></mrow><mi>T</mi></msubsup><mi>log</mi><msub><mi>p</mi><mi>&#x03B8;</mi></msub><mo>(</mo><msub><mi>x</mi><mi>t</mi></msub><mo>|</mo><msub><mi>x</mi><mrow><mo>&lt;</mo><mi>t</mi></mrow></msub><mo>)</mo></math>',
    },
    "(m x k) @ (k x n) costs about 2*m*k*n FLOPs": {
        "latex": r"(m \times k)(k \times n)\ \mathrm{matmul} \approx 2mkn\ \mathrm{FLOPs}",
        "kind": "资源估算",
        "validity": "近似。按一次乘法加一次加法计 2 FLOPs；不同硬件/库可能有不同计数口径。",
        "mathml": '<math display="block"><mrow><mo>(</mo><mi>m</mi><mo>&#x00D7;</mo><mi>k</mi><mo>)</mo><mo>(</mo><mi>k</mi><mo>&#x00D7;</mo><mi>n</mi><mo>)</mo></mrow><mo>&#x2248;</mo><mn>2</mn><mi>m</mi><mi>k</mi><mi>n</mi><mtext> FLOPs</mtext></math>',
    },
    "AI = FLOPs / bytes_moved": {
        "latex": r"\mathrm{AI} = \frac{\mathrm{FLOPs}}{\mathrm{bytes\ moved}}",
        "kind": "严格定义",
        "validity": "严格。关键在于 bytes moved 的边界要说清楚，是 HBM 流量、cache 流量还是理论最小 IO。",
        "mathml": '<math display="block"><mi>AI</mi><mo>=</mo><mfrac><mtext>FLOPs</mtext><mtext>bytes moved</mtext></mfrac></math>',
    },
    "Attention(Q,K,V)=softmax(QK^T/sqrt(d_k))V": {
        "latex": r"\mathrm{Attention}(Q,K,V)=\operatorname{softmax}\!\left(\frac{QK^{\top}}{\sqrt{d_k}}\right)V",
        "kind": "严格定义",
        "validity": "严格对应 scaled dot-product attention。decoder-only LM 还需要 causal mask；实际常写成 softmax((QK^T + M)/sqrt(d_k))V 或等价形式。",
        "mathml": '<math display="block"><mi>Attention</mi><mo>(</mo><mi>Q</mi><mo>,</mo><mi>K</mi><mo>,</mo><mi>V</mi><mo>)</mo><mo>=</mo><mi>softmax</mi><mo>(</mo><mfrac><mrow><mi>Q</mi><msup><mi>K</mi><mi>T</mi></msup></mrow><msqrt><msub><mi>d</mi><mi>k</mi></msub></msqrt></mfrac><mo>)</mo><mi>V</mi></math>',
    },
    "x <- x + f(norm(x))": {
        "latex": r"x \leftarrow x + f(\operatorname{norm}(x))",
        "kind": "架构模式",
        "validity": "严格描述 pre-norm residual block 的抽象形式。具体实现中 f 可以是 attention 或 MLP。",
        "mathml": '<math display="block"><mi>x</mi><mo>&#x2190;</mo><mi>x</mi><mo>+</mo><mi>f</mi><mo>(</mo><mi>norm</mi><mo>(</mo><mi>x</mi><mo>)</mo><mo>)</mo></math>',
    },
    "O(T^2 * d)": {
        "latex": r"O(T^2 d)",
        "kind": "复杂度",
        "validity": "近似阶复杂度，指标准 full attention 的主要序列长度项；完整层还包括投影和 MLP 成本。",
        "mathml": '<math display="block"><mi>O</mi><mo>(</mo><msup><mi>T</mi><mn>2</mn></msup><mi>d</mi><mo>)</mo></math>',
    },
    "active_params << total_params": {
        "latex": r"N_{\mathrm{active}} \ll N_{\mathrm{total}}",
        "kind": "MoE 关系",
        "validity": "定性关系，不是精确公式。MoE 的每 token 激活参数远少于总参数。",
        "mathml": '<math display="block"><msub><mi>N</mi><mtext>active</mtext></msub><mo>&#x226A;</mo><msub><mi>N</mi><mtext>total</mtext></msub></math>',
    },
    "performance <= min(peak_flops, bandwidth * arithmetic_intensity)": {
        "latex": r"P \le \min(P_{\mathrm{peak}},\ B_{\mathrm{mem}}\cdot \mathrm{AI})",
        "kind": "Roofline 上界",
        "validity": "近似性能上界。真实性能还受 kernel 实现、并行度、cache、通信等因素影响。",
        "mathml": '<math display="block"><mi>P</mi><mo>&#x2264;</mo><mi>min</mi><mo>(</mo><msub><mi>P</mi><mtext>peak</mtext></msub><mo>,</mo><msub><mi>B</mi><mtext>mem</mtext></msub><mo>&#x22C5;</mo><mi>AI</mi><mo>)</mo></math>',
    },
    "softmax can be updated block by block with running max and running sum": {
        "latex": r"m=\max_i s_i,\quad \ell=\sum_i e^{s_i-m},\quad \operatorname{softmax}(s)_i=\frac{e^{s_i-m}}{\ell}",
        "kind": "数值稳定 softmax",
        "validity": "严格。FlashAttention 的 online softmax 使用可分块更新的 running max 和 running sum 来得到同样的 exact attention 结果。",
        "mathml": '<math display="block"><mi>m</mi><mo>=</mo><msub><mi>max</mi><mi>i</mi></msub><msub><mi>s</mi><mi>i</mi></msub><mo>,</mo><mi>&#x2113;</mi><mo>=</mo><msub><mo>&#x2211;</mo><mi>i</mi></msub><msup><mi>e</mi><mrow><msub><mi>s</mi><mi>i</mi></msub><mo>-</mo><mi>m</mi></mrow></msup><mo>,</mo><msub><mi>softmax</mi><mi>i</mi></msub><mo>=</mo><mfrac><msup><mi>e</mi><mrow><msub><mi>s</mi><mi>i</mi></msub><mo>-</mo><mi>m</mi></mrow></msup><mi>&#x2113;</mi></mfrac></math>',
    },
    "grad = (grad_1 + ... + grad_n) / n": {
        "latex": r"g=\frac{1}{n}\sum_{i=1}^{n} g_i",
        "kind": "数据并行梯度聚合",
        "validity": "严格，前提是每个 worker 的 loss 归一化方式一致；实际系统用 all-reduce 实现求和或平均。",
        "mathml": '<math display="block"><mi>g</mi><mo>=</mo><mfrac><mn>1</mn><mi>n</mi></mfrac><msubsup><mo>&#x2211;</mo><mrow><mi>i</mi><mo>=</mo><mn>1</mn></mrow><mi>n</mi></msubsup><msub><mi>g</mi><mi>i</mi></msub></math>',
    },
    "idle_fraction roughly = (stages - 1) / (micro_batches + stages - 1)": {
        "latex": r"\mathrm{idle\ fraction}\approx \frac{p-1}{m+p-1}",
        "kind": "流水线近似",
        "validity": "近似。p 是 pipeline stages，m 是 micro-batches；具体 bubble 取决于调度策略，如 GPipe 或 1F1B。",
        "mathml": '<math display="block"><mtext>idle fraction</mtext><mo>&#x2248;</mo><mfrac><mrow><mi>p</mi><mo>-</mo><mn>1</mn></mrow><mrow><mi>m</mi><mo>+</mo><mi>p</mi><mo>-</mo><mn>1</mn></mrow></mfrac></math>',
    },
    "L(N,D)=L_inf + A/N^alpha + B/D^beta": {
        "latex": r"L(N,D)=L_{\infty}+\frac{A}{N^{\alpha}}+\frac{B}{D^{\beta}}",
        "kind": "教学用 scaling law",
        "validity": "简化经验式。用于理解参数量 N 和训练 token D 的收益递减；真实作业应按官方 handout 的实验设定拟合。",
        "mathml": '<math display="block"><mi>L</mi><mo>(</mo><mi>N</mi><mo>,</mo><mi>D</mi><mo>)</mo><mo>=</mo><msub><mi>L</mi><mi>&#x221E;</mi></msub><mo>+</mo><mfrac><mi>A</mi><msup><mi>N</mi><mi>&#x03B1;</mi></msup></mfrac><mo>+</mo><mfrac><mi>B</mi><msup><mi>D</mi><mi>&#x03B2;</mi></msup></mfrac></math>',
    },
    "bytes ~= 2 * layers * heads * seq * head_dim * bytes_per_value": {
        "latex": r"\mathrm{bytes}_{KV}\approx 2LH T d_{\mathrm{head}}\,b",
        "kind": "显存估算",
        "validity": "近似。2 表示 K 和 V；L 是层数，H 是头数，T 是缓存长度，d_head 是每头维度，b 是每个数的字节数。batch size 需要额外相乘。",
        "mathml": '<math display="block"><msub><mtext>bytes</mtext><mtext>KV</mtext></msub><mo>&#x2248;</mo><mn>2</mn><mi>L</mi><mi>H</mi><mi>T</mi><msub><mi>d</mi><mtext>head</mtext></msub><mi>b</mi></math>',
    },
    "log(L-L_inf) ~= log A - alpha log N": {
        "latex": r"\log(L-L_{\infty}) \approx \log A - \alpha \log N",
        "kind": "log-log 线性化",
        "validity": "近似，来自单变量 power-law 项。仅在其他变量受控且 L_inf 估计合理时成立。",
        "mathml": '<math display="block"><mi>log</mi><mo>(</mo><mi>L</mi><mo>-</mo><msub><mi>L</mi><mi>&#x221E;</mi></msub><mo>)</mo><mo>&#x2248;</mo><mi>log</mi><mi>A</mi><mo>-</mo><mi>&#x03B1;</mi><mi>log</mi><mi>N</mi></math>',
    },
    "PPL = exp(cross_entropy)": {
        "latex": r"\mathrm{PPL}=\exp\!\left(\frac{1}{T}\sum_{t=1}^{T}-\log p_{\theta}(x_t\mid x_{<t})\right)",
        "kind": "严格定义",
        "validity": "严格，前提是 cross entropy 是按 token 平均的负对数似然。若 loss 是求和，需先除以 token 数。",
        "mathml": '<math display="block"><mi>PPL</mi><mo>=</mo><mi>exp</mi><mo>(</mo><mfrac><mn>1</mn><mi>T</mi></mfrac><msubsup><mo>&#x2211;</mo><mrow><mi>t</mi><mo>=</mo><mn>1</mn></mrow><mi>T</mi></msubsup><mo>-</mo><mi>log</mi><msub><mi>p</mi><mi>&#x03B8;</mi></msub><mo>(</mo><msub><mi>x</mi><mi>t</mi></msub><mo>|</mo><msub><mi>x</mi><mrow><mo>&lt;</mo><mi>t</mi></mrow></msub><mo>)</mo><mo>)</mo></math>',
    },
    "D = sum_i w_i D_i,  sum_i w_i = 1": {
        "latex": r"D_{\mathrm{mix}}=\sum_i w_iD_i,\qquad \sum_i w_i=1,\quad w_i\ge 0",
        "kind": "数据混合抽象",
        "validity": "抽象表达。D_i 可理解为数据源分布或采样池；真实训练中还涉及去重、温度采样和 epoch 配置。",
        "mathml": '<math display="block"><msub><mi>D</mi><mtext>mix</mtext></msub><mo>=</mo><msub><mo>&#x2211;</mo><mi>i</mi></msub><msub><mi>w</mi><mi>i</mi></msub><msub><mi>D</mi><mi>i</mi></msub><mo>,</mo><msub><mo>&#x2211;</mo><mi>i</mi></msub><msub><mi>w</mi><mi>i</mi></msub><mo>=</mo><mn>1</mn><mo>,</mo><msub><mi>w</mi><mi>i</mi></msub><mo>&#x2265;</mo><mn>0</mn></math>',
    },
    "J(A,B)=|A intersect B| / |A union B|": {
        "latex": r"J(A,B)=\frac{|A\cap B|}{|A\cup B|}",
        "kind": "严格定义",
        "validity": "严格。用于集合相似度；文档去重时 A、B 常是 shingles 集合。",
        "mathml": '<math display="block"><mi>J</mi><mo>(</mo><mi>A</mi><mo>,</mo><mi>B</mi><mo>)</mo><mo>=</mo><mfrac><mrow><mo>|</mo><mi>A</mi><mo>&#x2229;</mo><mi>B</mi><mo>|</mo></mrow><mrow><mo>|</mo><mi>A</mi><mo>&#x222A;</mo><mi>B</mi><mo>|</mo></mrow></mfrac></math>',
    },
    "L_SFT = -sum_t log pi_theta(y_t | x, y_<t)": {
        "latex": r"L_{\mathrm{SFT}}=-\sum_{t=1}^{T}\log \pi_{\theta}(y_t\mid x,y_{<t})",
        "kind": "SFT 目标",
        "validity": "严格。实现中通常只对 assistant answer token 计 loss，并按 token 或样本平均。",
        "mathml": '<math display="block"><msub><mi>L</mi><mtext>SFT</mtext></msub><mo>=</mo><mo>-</mo><msubsup><mo>&#x2211;</mo><mrow><mi>t</mi><mo>=</mo><mn>1</mn></mrow><mi>T</mi></msubsup><mi>log</mi><msub><mi>&#x03C0;</mi><mi>&#x03B8;</mi></msub><mo>(</mo><msub><mi>y</mi><mi>t</mi></msub><mo>|</mo><mi>x</mi><mo>,</mo><msub><mi>y</mi><mrow><mo>&lt;</mo><mi>t</mi></mrow></msub><mo>)</mo></math>',
    },
    "chosen should score higher than rejected": {
        "latex": r"r_{\theta}(x,y_{\mathrm{chosen}}) > r_{\theta}(x,y_{\mathrm{rejected}})",
        "kind": "偏好约束",
        "validity": "偏好学习的目标关系，不是完整 loss。DPO/RLHF 会把这个关系转成具体优化目标。",
        "mathml": '<math display="block"><msub><mi>r</mi><mi>&#x03B8;</mi></msub><mo>(</mo><mi>x</mi><mo>,</mo><msub><mi>y</mi><mtext>chosen</mtext></msub><mo>)</mo><mo>&gt;</mo><msub><mi>r</mi><mi>&#x03B8;</mi></msub><mo>(</mo><mi>x</mi><mo>,</mo><msub><mi>y</mi><mtext>rejected</mtext></msub><mo>)</mo></math>',
    },
    "A = reward - baseline": {
        "latex": r"A = R - b",
        "kind": "advantage 简化",
        "validity": "简化。真实 RL 中 advantage 可来自 value function、group baseline 或更复杂估计。",
        "mathml": '<math display="block"><mi>A</mi><mo>=</mo><mi>R</mi><mo>-</mo><mi>b</mi></math>',
    },
    "penalty = beta * KL(pi_new || pi_ref)": {
        "latex": r"\mathrm{penalty}=\beta\,\mathrm{KL}(\pi_{\mathrm{new}}\Vert \pi_{\mathrm{ref}})",
        "kind": "KL 正则",
        "validity": "常见约束项。具体方向、token 级估计和系数使用取决于算法实现。",
        "mathml": '<math display="block"><mtext>penalty</mtext><mo>=</mo><mi>&#x03B2;</mi><mi>KL</mi><mo>(</mo><msub><mi>&#x03C0;</mi><mtext>new</mtext></msub><mo>||</mo><msub><mi>&#x03C0;</mi><mtext>ref</mtext></msub><mo>)</mo></math>',
    },
    "similar(image, matching_text) > similar(image, wrong_text)": {
        "latex": r"s(I,T^+) > s(I,T^-)",
        "kind": "对比学习目标关系",
        "validity": "定性关系。完整对比学习通常使用 InfoNCE/softmax loss，而不是只优化一个不等式。",
        "mathml": '<math display="block"><mi>s</mi><mo>(</mo><mi>I</mi><mo>,</mo><msup><mi>T</mi><mo>+</mo></msup><mo>)</mo><mo>&gt;</mo><mi>s</mi><mo>(</mo><mi>I</mi><mo>,</mo><msup><mi>T</mi><mo>-</mo></msup><mo>)</mo></math>',
    },
    "effect(component)=metric(full)-metric(without_component)": {
        "latex": r"\Delta = M_{\mathrm{full}} - M_{\mathrm{ablated}}",
        "kind": "消融度量",
        "validity": "实验记账公式，不是因果证明。需要控制变量和重复实验才能支持结论。",
        "mathml": '<math display="block"><mi>&#x0394;</mi><mo>=</mo><msub><mi>M</mi><mtext>full</mtext></msub><mo>-</mo><msub><mi>M</mi><mtext>ablated</mtext></msub></math>',
    },
    "useful_model = data + architecture + optimization + evaluation + alignment": {
        "latex": r"\mathrm{useful\ model}\Leftarrow \{\mathrm{data},\mathrm{architecture},\mathrm{optimization},\mathrm{evaluation},\mathrm{alignment}\}",
        "kind": "课程主线",
        "validity": "教学概念图，不是数学公式。用于提醒一个可用模型依赖多环节共同成立。",
        "mathml": '<math display="block"><mtext>useful model</mtext><mo>&#x21D0;</mo><mo>{</mo><mtext>data</mtext><mo>,</mo><mtext>architecture</mtext><mo>,</mo><mtext>optimization</mtext><mo>,</mo><mtext>evaluation</mtext><mo>,</mo><mtext>alignment</mtext><mo>}</mo></math>',
    },
}


LESSONS = [
    {
        "id": "prep-python",
        "phase": "phase-0",
        "lecture": "Prep",
        "title": "Python 与工程习惯",
        "summary": "CS336 的作业非常工程化。入门阶段先学会写清楚的函数、测试和命令行脚本。",
        "beginner_view": "把模型看成一个普通程序：输入 token，输出下一个 token 的概率。所有复杂内容最后都会落成数组运算和函数调用。",
        "concepts": ["函数边界", "类型和 shape 注释", "单元测试", "可复现实验", "配置管理"],
        "math": [
            {
                "name": "为什么 shape 是数学的一部分",
                "formula": "X in R^(batch x seq x d_model)",
                "explain": "深度学习代码里的 bug 很多都来自维度错配。先写 shape，再写代码，是理解 Transformer 的最低成本方式。",
            }
        ],
        "code": """def check_shape(name, tensor, expected):
    assert tuple(tensor.shape) == tuple(expected), f"{name}: {tensor.shape} != {expected}"

# 语言模型常见形状：
# input_ids: [batch, seq]
# logits:    [batch, seq, vocab]
# loss:      scalar""",
        "practice": [
            "给任意一段 Transformer 代码补充 shape 注释。",
            "写 3 个最小单元测试：正常输入、空输入、维度错误输入。",
        ],
        "checkpoint": "看到 `B, T, C = x.shape` 时能立刻说出 batch、sequence、channels/hidden size。",
    },
    {
        "id": "prep-tensors",
        "phase": "phase-0",
        "lecture": "Prep",
        "title": "张量、线代和概率",
        "summary": "语言模型的核心是把离散文本变成向量，再用矩阵乘法堆出概率分布。",
        "beginner_view": "你不需要先成为数学家，但必须知道矩阵乘法、softmax、log probability 和梯度在做什么。",
        "concepts": ["向量", "矩阵乘法", "广播", "softmax", "log probability", "梯度"],
        "math": [
            {
                "name": "softmax",
                "formula": "softmax(z_i) = exp(z_i) / sum_j exp(z_j)",
                "explain": "logits 是未归一化分数。softmax 把分数变成概率，分数越大概率越高。",
            },
            {
                "name": "交叉熵",
                "formula": "CE = -log p(target)",
                "explain": "如果模型给正确答案的概率高，loss 小；如果概率低，loss 大。",
            },
        ],
        "code": """import math

def softmax(xs):
    m = max(xs)
    exps = [math.exp(x - m) for x in xs]
    total = sum(exps)
    return [x / total for x in exps]

def cross_entropy(probs, target_index):
    return -math.log(probs[target_index])""",
        "practice": [
            "手算 logits=[1,2,3] 的 softmax 近似值。",
            "如果正确 token 概率从 0.1 提高到 0.5，交叉熵如何变化？",
        ],
        "checkpoint": "能解释为什么语言模型训练是在最大化正确下一个 token 的概率。",
    },
    {
        "id": "prep-training-loop",
        "phase": "phase-0",
        "lecture": "Prep",
        "title": "最小训练循环",
        "summary": "训练循环永远是：取 batch、前向传播、算 loss、反向传播、更新参数、记录指标。",
        "beginner_view": "不要把训练想成魔法。optimizer 只是根据梯度把参数往 loss 下降的方向挪一点。",
        "concepts": ["batch", "forward", "loss", "backward", "optimizer step", "validation"],
        "math": [
            {
                "name": "梯度下降",
                "formula": "theta <- theta - lr * grad_theta L",
                "explain": "theta 是参数，L 是 loss。学习率 lr 决定每次移动多大。",
            }
        ],
        "code": """for step, batch in enumerate(loader):
    logits = model(batch["input_ids"])
    loss = cross_entropy(logits, batch["targets"])
    optimizer.zero_grad()
    loss.backward()
    optimizer.step()
    print(step, float(loss))""",
        "practice": [
            "把训练循环拆成 6 行伪代码并逐行解释。",
            "解释 train loss 和 validation loss 同时下降/分叉分别意味着什么。",
        ],
        "checkpoint": "能不看资料写出训练 loop 的顺序。",
    },
    {
        "id": "l01",
        "phase": "phase-1",
        "lecture": "Lecture 1",
        "title": "课程总览与 Tokenization",
        "summary": "语言模型从文本开始，但神经网络只吃数字。tokenizer 决定文本如何被切成整数序列。",
        "beginner_view": "把 tokenizer 想成输入法的反方向：它把字符串切成模型认识的小块，并给每个小块一个编号。",
        "concepts": ["language model", "token", "vocabulary", "byte-level BPE", "merge rule", "OOV"],
        "math": [
            {
                "name": "语言模型目标",
                "formula": "p(x_1,...,x_T)=prod_t p(x_t | x_<t)",
                "explain": "整段文本的概率被拆成每一步预测下一个 token 的条件概率乘积。",
            },
            {
                "name": "负对数似然",
                "formula": "L = -sum_t log p(x_t | x_<t)",
                "explain": "训练时希望真实下一个 token 的概率越大越好，所以最小化负 log 概率。",
            },
        ],
        "code": """from collections import Counter

def most_common_pair(words):
    counts = Counter()
    for word in words:
        for a, b in zip(word, word[1:]):
            counts[(a, b)] += 1
    return counts.most_common(1)[0]

words = [list("low_"), list("lower_"), list("newest_")]
print(most_common_pair(words))""",
        "practice": [
            "用纸笔对 `low lower newest` 做 2 次 BPE merge。",
            "比较字符级、词级、BPE tokenizer 的词表大小和序列长度。",
        ],
        "checkpoint": "能解释为什么现代 LM 通常不用纯词级 tokenizer。",
    },
    {
        "id": "l02",
        "phase": "phase-1",
        "lecture": "Lecture 2",
        "title": "PyTorch、einops 与资源核算",
        "summary": "写模型前先学会看张量形状，并估算一个操作要花多少计算和显存。",
        "beginner_view": "训练慢不是抽象问题。每一层都在消耗 FLOPs、显存和带宽，系统课的第一步就是把它们数清楚。",
        "concepts": ["tensor shape", "einsum/einops", "FLOPs", "memory", "arithmetic intensity", "bandwidth"],
        "math": [
            {
                "name": "矩阵乘 FLOPs",
                "formula": "(m x k) @ (k x n) costs about 2*m*k*n FLOPs",
                "explain": "每个输出元素需要 k 次乘加，乘法和加法都算浮点操作。",
            },
            {
                "name": "算术强度",
                "formula": "AI = FLOPs / bytes_moved",
                "explain": "AI 高通常更受计算峰值限制；AI 低通常更受内存带宽限制。",
            },
        ],
        "code": """# 一个线性层：x [B,T,D] @ W [D,H] -> y [B,T,H]
B, T, D, H = 4, 128, 512, 2048
flops = 2 * B * T * D * H
activation_bytes = B * T * H * 4
print(flops, activation_bytes / 1024**2, "MiB")""",
        "practice": [
            "估算 B=8,T=1024,D=768,H=3072 的 MLP FLOPs。",
            "解释为什么 attention 的 T^2 项会让长上下文变贵。",
        ],
        "checkpoint": "给定一个 matmul 形状，能估算 FLOPs 和输出显存。",
    },
    {
        "id": "l03",
        "phase": "phase-1",
        "lecture": "Lecture 3",
        "title": "Transformer 架构与超参数",
        "summary": "Transformer 是语言模型的主体：embedding、attention、MLP、norm 和 residual 不断堆叠。",
        "beginner_view": "每层 Transformer 都做两件事：让 token 彼此交换信息，用 MLP 独立加工每个 token 的表示。",
        "concepts": ["embedding", "residual", "normalization", "self-attention", "MLP", "depth", "width", "context length"],
        "math": [
            {
                "name": "Self-attention",
                "formula": "Attention(Q,K,V)=softmax(QK^T/sqrt(d_k))V",
                "explain": "QK^T 算每个 token 看其他 token 的相关性，softmax 变权重，再对 V 做加权平均。",
            },
            {
                "name": "Residual block",
                "formula": "x <- x + f(norm(x))",
                "explain": "残差让深层网络更容易训练，也让每层学习对表示的增量修改。",
            },
        ],
        "code": """def transformer_block(x):
    x = x + self_attention(layer_norm(x))
    x = x + mlp(layer_norm(x))
    return x""",
        "practice": [
            "画出一个 decoder-only Transformer block 的数据流。",
            "解释 n_layers、d_model、n_heads、context_length 各自影响什么。",
        ],
        "checkpoint": "能从输入 token ids 讲到最终 logits 的完整路径。",
    },
    {
        "id": "l04",
        "phase": "phase-1",
        "lecture": "Lecture 4",
        "title": "Attention 变体与 MoE",
        "summary": "标准 attention 很强但昂贵，因此需要稀疏 attention、线性 attention、滑窗 attention 和 MoE 等结构。",
        "beginner_view": "不是所有 token 都必须和所有 token 交流。结构设计的核心是在能力、速度和显存之间做取舍。",
        "concepts": ["quadratic attention", "sliding window", "linear attention", "Mixture of Experts", "router", "capacity"],
        "math": [
            {
                "name": "标准 attention 复杂度",
                "formula": "O(T^2 * d)",
                "explain": "T 个 token 两两比较，所以序列长度翻倍，attention 分数矩阵大约变 4 倍。",
            },
            {
                "name": "MoE 激活参数",
                "formula": "active_params << total_params",
                "explain": "MoE 有很多 expert，但每个 token 只路由到少数 expert，因此总参数大而每步激活参数少。",
            },
        ],
        "code": """def route_to_experts(hidden, router_logits, top_k=2):
    # hidden: [tokens, d_model], router_logits: [tokens, n_experts]
    expert_ids = router_logits.argsort(axis=-1)[:, -top_k:]
    return expert_ids""",
        "practice": [
            "比较 full attention 和 sliding window attention 的信息流差别。",
            "解释 MoE 为什么会带来负载均衡问题。",
        ],
        "checkpoint": "能说清 MoE 是扩大总参数量，不是让每个 token 都经过所有参数。",
    },
    {
        "id": "l05",
        "phase": "phase-1",
        "lecture": "Lecture 5",
        "title": "GPU、TPU 与硬件直觉",
        "summary": "大模型训练依赖硬件并行。理解显存层级、带宽和矩阵乘，是优化的基础。",
        "beginner_view": "GPU 快不是因为每个核心聪明，而是因为它能同时做海量简单运算。模型要写成硬件喜欢的形状。",
        "concepts": ["SM", "HBM", "SRAM", "register", "tensor core", "memory hierarchy", "throughput"],
        "math": [
            {
                "name": "Roofline 思想",
                "formula": "performance <= min(peak_flops, bandwidth * arithmetic_intensity)",
                "explain": "程序速度受两个上限约束：算力峰值和内存带宽能喂给计算单元的数据速度。",
            }
        ],
        "code": """# 同样的数学操作，硬件效率可能完全不同：
# 小矩阵、频繁 Python 循环 -> GPU 利用率低
# 大批量矩阵乘、连续内存 -> GPU 利用率高""",
        "practice": [
            "解释为什么逐元素 Python for-loop 在 GPU 上也可能很慢。",
            "把一次 attention 拆成读写 HBM 和矩阵乘两类成本。",
        ],
        "checkpoint": "能区分 compute-bound 和 memory-bound。",
    },
    {
        "id": "l06",
        "phase": "phase-1",
        "lecture": "Lecture 6",
        "title": "Kernel、Triton 与 FlashAttention",
        "summary": "Kernel 是实际在 GPU 上跑的函数。FlashAttention 的关键是少写显存，而不是改变 attention 数学。",
        "beginner_view": "标准 attention 会显式保存 T x T 分数矩阵。FlashAttention 分块计算，边算边归一化，减少显存读写。",
        "concepts": ["kernel", "tiling", "Triton", "online softmax", "FlashAttention", "memory-efficient attention"],
        "math": [
            {
                "name": "online softmax",
                "formula": "softmax can be updated block by block with running max and running sum",
                "explain": "为了数值稳定和节省内存，可以分块维护最大值和指数和，不必一次性存完整矩阵。",
            }
        ],
        "code": """# FlashAttention 伪代码
for q_block in Q_blocks:
    running_max = -inf
    running_sum = 0
    output = 0
    for k_block, v_block in KV_blocks:
        scores = q_block @ k_block.T / sqrt(d)
        output = update_online_softmax(output, scores, v_block)
    write(output)""",
        "practice": [
            "说明 FlashAttention 和普通 attention 得到的数学结果是否相同。",
            "解释为什么少写一个 T x T attention matrix 会明显更快。",
        ],
        "checkpoint": "能用一句话说出 FlashAttention 的核心：IO-aware exact attention。",
    },
    {
        "id": "l07",
        "phase": "phase-2",
        "lecture": "Lecture 7",
        "title": "并行训练 I",
        "summary": "单卡不够时，需要把数据、参数、激活或层拆到多张卡上。",
        "beginner_view": "并行不是免费午餐。拆开计算以后，GPU 之间要通信，通信会吃掉一部分收益。",
        "concepts": ["data parallel", "gradient all-reduce", "model parallel", "FSDP", "ZeRO", "activation checkpointing"],
        "math": [
            {
                "name": "数据并行梯度平均",
                "formula": "grad = (grad_1 + ... + grad_n) / n",
                "explain": "每张卡看不同 batch，反向传播后把梯度平均，相当于更大的 global batch。",
            }
        ],
        "code": """# DDP 的概念伪代码
for gpu in gpus:
    loss_gpu = model_gpu(batch_gpu)
    grad_gpu = backward(loss_gpu)
grad = all_reduce_mean([grad_gpu for gpu in gpus])
optimizer.step(grad)""",
        "practice": [
            "解释 batch size、micro batch、gradient accumulation 的区别。",
            "比较 DDP 和 FSDP 分别主要节省/增加什么。",
        ],
        "checkpoint": "能解释为什么多卡训练可能被通信瓶颈限制。",
    },
    {
        "id": "l08",
        "phase": "phase-2",
        "lecture": "Lecture 8",
        "title": "并行训练 II",
        "summary": "更大模型需要 tensor parallel、pipeline parallel、sequence parallel 等组合策略。",
        "beginner_view": "当一层或一个矩阵都放不进单卡时，就要把模型内部也切开。",
        "concepts": ["tensor parallel", "pipeline parallel", "sequence parallel", "bubble", "communication overlap", "3D parallelism"],
        "math": [
            {
                "name": "Pipeline bubble",
                "formula": "idle_fraction roughly = (stages - 1) / (micro_batches + stages - 1)",
                "explain": "流水线开始和结束阶段有空转。micro batch 越多，空转比例越低。",
            }
        ],
        "code": """# Pipeline parallel 直觉：
stage0: embedding + blocks 0-5
stage1: blocks 6-11
stage2: blocks 12-17
stage3: blocks 18-23 + lm_head""",
        "practice": [
            "画出 4 个 pipeline stage、8 个 micro batch 的执行时间线。",
            "解释 tensor parallel 为什么需要在矩阵乘后通信。",
        ],
        "checkpoint": "能把 data/tensor/pipeline parallel 的拆分对象讲清楚。",
    },
    {
        "id": "l09",
        "phase": "phase-3",
        "lecture": "Lecture 9",
        "title": "Scaling Laws I",
        "summary": "Scaling law 研究 loss 如何随参数量、数据量、计算量变化，帮助决定训练预算怎么花。",
        "beginner_view": "不是模型越大越好，也不是数据越多越好。给定预算，参数和 token 要按比例配。",
        "concepts": ["power law", "irreducible loss", "compute-optimal", "undertrained", "overtrained", "Chinchilla"],
        "math": [
            {
                "name": "简化 scaling law",
                "formula": "L(N,D)=L_inf + A/N^alpha + B/D^beta",
                "explain": "N 是参数量，D 是训练 token 数。两者增大通常让 loss 降低，但收益递减。",
            }
        ],
        "code": """def predicted_loss(params_billion, tokens_billion):
    l_inf, a, b, alpha, beta = 1.6, 0.8, 1.1, 0.34, 0.28
    return l_inf + a / params_billion**alpha + b / tokens_billion**beta""",
        "practice": [
            "用交互实验调参数量和 token 数，看 loss 如何递减。",
            "解释为什么固定算力下只增大模型可能不划算。",
        ],
        "checkpoint": "能解释 compute-optimal training 的含义。",
    },
    {
        "id": "l10",
        "phase": "phase-3",
        "lecture": "Lecture 10",
        "title": "Inference 与 KV Cache",
        "summary": "训练关注吞吐，推理同时关注延迟、吞吐、显存和服务稳定性。",
        "beginner_view": "生成文本是一个 token 一个 token 往外吐。KV cache 避免每次都重算所有历史 token。",
        "concepts": ["prefill", "decode", "KV cache", "batching", "sampling", "temperature", "top-k", "top-p"],
        "math": [
            {
                "name": "KV cache 显存",
                "formula": "bytes ~= 2 * layers * heads * seq * head_dim * bytes_per_value",
                "explain": "2 来自 key 和 value。上下文越长、层数越多，推理 cache 显存越大。",
            }
        ],
        "code": """def sample_next(logits, temperature=1.0):
    scaled = logits / temperature
    probs = softmax(scaled)
    return categorical_sample(probs)""",
        "practice": [
            "解释 prefill 和 decode 阶段的计算模式差别。",
            "比较 greedy、temperature、top-p 采样的输出特点。",
        ],
        "checkpoint": "能说明 KV cache 为什么让自回归生成更快。",
    },
    {
        "id": "l11",
        "phase": "phase-3",
        "lecture": "Lecture 11",
        "title": "Scaling Laws II",
        "summary": "更深入地用实验拟合 scaling law，并讨论外推、噪声和数据质量。",
        "beginner_view": "scaling law 不是玄学曲线拟合。它要求实验设计干净、变量控制清楚、外推谨慎。",
        "concepts": ["curve fitting", "extrapolation", "isoFLOP", "data quality", "token budget", "model family"],
        "math": [
            {
                "name": "log-log 拟合",
                "formula": "log(L-L_inf) ~= log A - alpha log N",
                "explain": "power law 在 log-log 坐标下接近直线，因此常用对数空间拟合斜率。",
            }
        ],
        "code": """# 用多组小实验拟合趋势，而不是只看一个模型点
experiments = [
    {"params": 0.1, "tokens": 1, "loss": 3.2},
    {"params": 0.3, "tokens": 3, "loss": 2.7},
    {"params": 1.0, "tokens": 10, "loss": 2.3},
]""",
        "practice": [
            "解释为什么同一个参数量在不同数据质量下 loss 不能直接比较。",
            "写出一个最小 isoFLOP 实验表格。",
        ],
        "checkpoint": "能说清 scaling law 预测的前提和风险。",
    },
    {
        "id": "l12",
        "phase": "phase-3",
        "lecture": "Lecture 12",
        "title": "Evaluation",
        "summary": "评测决定你是否真的知道模型会什么。单一 benchmark 很容易误导。",
        "beginner_view": "perplexity 低不等于万事大吉。你还要检查能力、鲁棒性、污染、偏见和真实使用场景。",
        "concepts": ["perplexity", "benchmark", "contamination", "calibration", "robustness", "human eval"],
        "math": [
            {
                "name": "Perplexity",
                "formula": "PPL = exp(cross_entropy)",
                "explain": "PPL 可以理解为模型平均每步在多少个候选之间困惑。越低通常越好。",
            }
        ],
        "code": """def exact_match(prediction, answer):
    return prediction.strip().lower() == answer.strip().lower()

def accuracy(rows):
    return sum(exact_match(r["pred"], r["gold"]) for r in rows) / len(rows)""",
        "practice": [
            "设计一个数学推理评测，并说明如何避免答案泄漏。",
            "比较 perplexity、accuracy 和 human preference 的适用场景。",
        ],
        "checkpoint": "能解释 benchmark contamination 是什么，以及为什么危险。",
    },
    {
        "id": "l13",
        "phase": "phase-4",
        "lecture": "Lecture 13",
        "title": "数据来源与数据集",
        "summary": "预训练数据常来自网页、代码、书籍、论文和对话。数据来源决定模型的知识和偏差。",
        "beginner_view": "模型不是凭空聪明。它学到什么，很大程度取决于它看过什么。",
        "concepts": ["Common Crawl", "WET/WARC", "dataset mixture", "license", "domain", "quality"],
        "math": [
            {
                "name": "数据混合比例",
                "formula": "D = sum_i w_i D_i,  sum_i w_i = 1",
                "explain": "不同来源按权重混合。提高代码数据比例会影响代码能力，也可能改变自然语言能力。",
            }
        ],
        "code": """mixture = {
    "web": 0.55,
    "code": 0.20,
    "books": 0.15,
    "math": 0.10,
}
assert abs(sum(mixture.values()) - 1.0) < 1e-6""",
        "practice": [
            "列出一个中文模型预训练语料可能需要的 5 类来源。",
            "说明数据许可和隐私为什么是训练前必须处理的问题。",
        ],
        "checkpoint": "能把网页原始数据到训练 token 的流水线讲出来。",
    },
    {
        "id": "l14",
        "phase": "phase-4",
        "lecture": "Lecture 14",
        "title": "过滤、去重、混合与合成数据",
        "summary": "原始网页数据噪声很大，需要语言识别、质量过滤、去重、安全过滤和配比控制。",
        "beginner_view": "数据清洗不是杂活。高质量数据能让同样算力训练出更强模型。",
        "concepts": ["language identification", "quality filter", "deduplication", "MinHash", "synthetic data", "curriculum"],
        "math": [
            {
                "name": "Jaccard 相似度",
                "formula": "J(A,B)=|A intersect B| / |A union B|",
                "explain": "去重常比较文档 shingles 的集合相似度。相似度太高就认为近重复。",
            }
        ],
        "code": """def jaccard(a, b):
    a, b = set(a), set(b)
    return len(a & b) / max(1, len(a | b))

doc1 = "language models learn from data".split()
doc2 = "models learn from huge data".split()
print(jaccard(doc1, doc2))""",
        "practice": [
            "设计一个 5 步网页数据过滤 pipeline。",
            "解释为什么完全去重和过度去重都可能有问题。",
        ],
        "checkpoint": "能区分 exact duplicate、near duplicate 和 semantic duplicate。",
    },
    {
        "id": "l15",
        "phase": "phase-5",
        "lecture": "Lecture 15",
        "title": "SFT、RLHF 与后训练",
        "summary": "预训练让模型会续写，后训练让模型更会按人类意图完成任务。",
        "beginner_view": "SFT 像示范教学，RLHF 像根据偏好打分后调整行为。",
        "concepts": ["instruction tuning", "SFT", "reward model", "preference data", "PPO", "DPO"],
        "math": [
            {
                "name": "SFT loss",
                "formula": "L_SFT = -sum_t log pi_theta(y_t | x, y_<t)",
                "explain": "给定指令 x 和标准回答 y，训练模型提高标准回答每个 token 的概率。",
            },
            {
                "name": "Preference learning",
                "formula": "chosen should score higher than rejected",
                "explain": "偏好数据通常是一对回答：人更喜欢 chosen，不喜欢 rejected。",
            },
        ],
        "code": """sample = {
    "prompt": "解释什么是 attention",
    "chosen": "attention 是让 token 根据相关性聚合上下文信息的机制。",
    "rejected": "attention 是一个数据库。",
}""",
        "practice": [
            "把一个普通问答样本改写成 SFT 格式。",
            "解释 reward hacking 是什么。",
        ],
        "checkpoint": "能区分预训练、SFT、RLHF 各自改变模型的什么行为。",
    },
    {
        "id": "l16",
        "phase": "phase-5",
        "lecture": "Lecture 16",
        "title": "RLVR 与推理强化学习",
        "summary": "RLVR 使用可验证奖励训练模型解决数学、代码等可自动判题任务。",
        "beginner_view": "如果答案能被程序检查，就不一定需要人类逐条打偏好分。模型可以通过奖励学习更好的推理过程。",
        "concepts": ["verifiable reward", "reasoning trace", "GRPO", "advantage", "KL penalty", "pass@k"],
        "math": [
            {
                "name": "Advantage",
                "formula": "A = reward - baseline",
                "explain": "如果某个回答比同组平均好，它的 advantage 为正，训练会提高它的概率。",
            },
            {
                "name": "KL penalty",
                "formula": "penalty = beta * KL(pi_new || pi_ref)",
                "explain": "限制新策略不要偏离参考模型太远，避免训练发散或行为劣化。",
            },
        ],
        "code": """def reward_math_answer(pred, gold):
    return 1.0 if extract_final_answer(pred) == gold else 0.0

def advantage(reward, group_rewards):
    return reward - sum(group_rewards) / len(group_rewards)""",
        "practice": [
            "设计一个可以自动验证的数学题奖励函数。",
            "解释为什么只奖励最终答案可能导致过程不可控。",
        ],
        "checkpoint": "能说明 RLVR 和 RLHF 的奖励来源差别。",
    },
    {
        "id": "l17",
        "phase": "phase-5",
        "lecture": "Lecture 17",
        "title": "对齐与多模态",
        "summary": "对齐不只发生在文本，也延伸到图像、音频、视频和工具调用等多模态系统。",
        "beginner_view": "多模态模型把不同类型输入映射到可以共同推理的表示空间。",
        "concepts": ["multimodal encoder", "vision-language model", "contrastive learning", "safety alignment", "tool use"],
        "math": [
            {
                "name": "对比学习直觉",
                "formula": "similar(image, matching_text) > similar(image, wrong_text)",
                "explain": "让匹配的图文表示更接近，不匹配的更远。",
            }
        ],
        "code": """# 多模态模型的概念路径
image_features = vision_encoder(image)
text_features = text_encoder(tokens)
joint_features = projector(image_features, text_features)
answer = language_model(joint_features)""",
        "practice": [
            "解释图像 encoder 和语言模型之间为什么需要 projector。",
            "列出多模态安全评测要覆盖的 3 类风险。",
        ],
        "checkpoint": "能讲清多模态不是简单把图片转成文字，而是表示空间对齐。",
    },
    {
        "id": "l18",
        "phase": "phase-5",
        "lecture": "Lecture 18",
        "title": "Guest Lecture：研究视角 I",
        "summary": "客座讲座通常强调课程知识如何进入真实研究和工程系统。",
        "beginner_view": "这类课不用追每个细节，重点是识别：它解决的瓶颈属于数据、模型、系统、评测还是对齐。",
        "concepts": ["research framing", "ablation", "baseline", "failure mode", "deployment constraint"],
        "math": [
            {
                "name": "消融实验",
                "formula": "effect(component)=metric(full)-metric(without_component)",
                "explain": "用移除组件前后的指标差异判断组件是否真的有贡献。",
            }
        ],
        "code": """ablation_table = [
    {"setting": "full", "accuracy": 0.72},
    {"setting": "no_data_filter", "accuracy": 0.66},
    {"setting": "no_rl", "accuracy": 0.61},
]""",
        "practice": [
            "听完一场研究讲座后，用数据/模型/系统/评测/对齐五类给它归因。",
            "写出一个你认为最关键的 baseline。",
        ],
        "checkpoint": "能把前沿工作拆解成问题、方法、证据和局限。",
    },
    {
        "id": "l19",
        "phase": "phase-5",
        "lecture": "Lecture 19",
        "title": "Guest Lecture：研究视角 II 与总复盘",
        "summary": "课程最后要把所有模块串起来：数据进入 tokenizer，模型训练出能力，系统决定成本，评测暴露问题，后训练塑造行为。",
        "beginner_view": "你最终要能从一个模型产品倒推：它需要什么数据、模型结构、训练预算、推理系统、评测和对齐策略。",
        "concepts": ["end-to-end pipeline", "tradeoff", "risk", "iteration loop", "model card"],
        "math": [
            {
                "name": "端到端目标",
                "formula": "useful_model = data + architecture + optimization + evaluation + alignment",
                "explain": "这不是严格数学公式，而是课程主线。缺任何一环，模型都可能不可用。",
            }
        ],
        "code": """def language_model_project():
    collect_and_clean_data()
    train_tokenizer()
    build_transformer()
    train_and_profile()
    evaluate()
    post_train_and_align()
    deploy_with_monitoring()""",
        "practice": [
            "写一页 CS336 总结：每个模块解决什么问题。",
            "选择一个小模型项目，设计端到端技术方案。",
        ],
        "checkpoint": "能完整讲出从原始文本到可用助手模型的生命周期。",
    },
]


ASSIGNMENTS = [
    {
        "id": "a1",
        "title": "Assignment 1：Basics",
        "goal": "实现 tokenizer、Transformer 组件、optimizer，并训练最小语言模型。",
        "study_version": [
            "只使用玩具语料。",
            "不追求训练质量，只验证每个组件的输入输出形状和 loss 计算。",
            "把所有模块写成可单测函数。",
        ],
        "maps_to": ["l01", "l02", "l03", "l06"],
    },
    {
        "id": "a2",
        "title": "Assignment 2：Systems",
        "goal": "profile 模型，理解 GPU kernel、FlashAttention 和分布式训练。",
        "study_version": [
            "用模拟参数估算 FLOPs/显存。",
            "用伪代码理解 Triton kernel 和 online softmax。",
            "不需要真的多卡训练。",
        ],
        "maps_to": ["l05", "l06", "l07", "l08"],
    },
    {
        "id": "a3",
        "title": "Assignment 3：Scaling",
        "goal": "理解 Transformer 组件贡献，并拟合 scaling law。",
        "study_version": [
            "用内置交互曲线替代远程训练 API。",
            "练习 log-log 拟合和预算分配解释。",
        ],
        "maps_to": ["l09", "l10", "l11", "l12"],
    },
    {
        "id": "a4",
        "title": "Assignment 4：Data",
        "goal": "把网页数据处理成可训练数据，并比较过滤/去重对模型的影响。",
        "study_version": [
            "用几十行文本模拟网页语料。",
            "实现语言过滤、质量过滤、Jaccard 去重和混合权重。",
        ],
        "maps_to": ["l13", "l14"],
    },
    {
        "id": "a5",
        "title": "Assignment 5：Alignment and Reasoning RL",
        "goal": "使用 SFT 和 RL 训练数学推理模型，选做安全对齐。",
        "study_version": [
            "不用真实模型，手工构造 prompt/chosen/rejected/reward 样本。",
            "实现 reward、advantage、DPO/GRPO 的最小公式演示。",
        ],
        "maps_to": ["l15", "l16", "l17"],
    },
]


LABS = [
    {
        "id": "bpe",
        "title": "BPE Tokenizer 实验",
        "description": "输入一小段文本，观察最常见相邻符号对如何被合并。",
        "lesson": "l01",
    },
    {
        "id": "attention",
        "title": "Attention 手算实验",
        "description": "修改 Q/K/V 数值，观察 attention 权重和输出如何变化。",
        "lesson": "l03",
    },
    {
        "id": "resources",
        "title": "FLOPs 与显存估算器",
        "description": "调整 batch、sequence、hidden size 和层数，估算训练量级。",
        "lesson": "l02",
    },
    {
        "id": "scaling",
        "title": "Scaling Law 模拟器",
        "description": "用简化公式观察参数量和训练 token 对 loss 的影响。",
        "lesson": "l09",
    },
    {
        "id": "data",
        "title": "数据过滤与去重实验",
        "description": "对玩具网页文本执行长度过滤、质量过滤和 Jaccard 去重。",
        "lesson": "l14",
    },
    {
        "id": "alignment",
        "title": "偏好与奖励实验",
        "description": "比较 SFT、DPO、RLVR 的样本格式和奖励信号。",
        "lesson": "l15",
    },
]


QUIZZES = [
    {
        "id": "q-basics",
        "title": "基础自测",
        "questions": [
            {
                "prompt": "语言模型训练时最直接优化的目标是什么？",
                "options": ["提高真实下一个 token 的概率", "让词表越大越好", "让模型输出越长越好", "让所有 token 概率相等"],
                "answer": 0,
                "explain": "自回归 LM 最大化 p(x_t | x_<t)，等价于最小化负对数似然。",
            },
            {
                "prompt": "为什么 BPE 比纯词级 tokenizer 更稳健？",
                "options": ["可以用子词组合处理没见过的词", "完全不需要词表", "让序列一定更长", "会自动理解语义"],
                "answer": 0,
                "explain": "BPE 在字符/字节和词之间折中，能用已有子词表示罕见词。",
            },
        ],
    },
    {
        "id": "q-systems",
        "title": "系统自测",
        "questions": [
            {
                "prompt": "FlashAttention 的核心收益主要来自哪里？",
                "options": ["减少 HBM 读写和中间矩阵存储", "改变 attention 公式", "减少模型层数", "删除 softmax"],
                "answer": 0,
                "explain": "FlashAttention 是 exact attention，主要通过分块和 online softmax 降低 IO 成本。",
            },
            {
                "prompt": "数据并行训练为什么需要 all-reduce？",
                "options": ["同步不同 GPU 上的梯度", "复制训练数据到硬盘", "把 token 重新分词", "改变优化器公式"],
                "answer": 0,
                "explain": "每张卡计算局部梯度，all-reduce 后得到全局 batch 的平均梯度。",
            },
        ],
    },
    {
        "id": "q-data-align",
        "title": "数据与对齐自测",
        "questions": [
            {
                "prompt": "数据去重的主要目的是什么？",
                "options": ["降低重复样本导致的记忆和评测污染", "让所有文本变短", "替代 tokenizer", "让模型不需要训练"],
                "answer": 0,
                "explain": "重复数据会造成记忆、浪费算力，并可能污染评测集。",
            },
            {
                "prompt": "SFT 与 RLVR 的主要区别是什么？",
                "options": ["SFT 学示范答案，RLVR 用可验证奖励优化行为", "SFT 不用文本", "RLVR 只能训练 tokenizer", "两者没有区别"],
                "answer": 0,
                "explain": "SFT 是监督学习；RLVR 依赖自动可验证的奖励信号。",
            },
        ],
    },
]


GLOSSARY = [
    {"term": "Token", "definition": "模型处理文本的基本离散单位，可以是字节、字符、子词或词。"},
    {"term": "Logits", "definition": "softmax 之前的未归一化分数。"},
    {"term": "Embedding", "definition": "把 token id 映射成连续向量的表。"},
    {"term": "Attention", "definition": "根据相关性对上下文 value 做加权平均的机制。"},
    {"term": "FLOPs", "definition": "浮点操作次数，用来估算计算量。"},
    {"term": "Activation", "definition": "前向传播中间结果，反向传播通常需要保存或重算。"},
    {"term": "KV Cache", "definition": "推理时缓存历史 token 的 key/value，避免重复计算。"},
    {"term": "Scaling Law", "definition": "描述模型 loss 随参数、数据、算力变化的经验规律。"},
    {"term": "SFT", "definition": "Supervised Fine-Tuning，用高质量示范数据继续训练模型。"},
    {"term": "RLHF", "definition": "Reinforcement Learning from Human Feedback，用人类偏好训练模型行为。"},
    {"term": "RLVR", "definition": "Reinforcement Learning with Verifiable Rewards，用可自动验证奖励训练推理能力。"},
    {"term": "DPO", "definition": "Direct Preference Optimization，直接用偏好对优化模型而不显式训练 reward model。"},
]


def curriculum():
    return {
        "course": COURSE,
        "source_map": SOURCE_MAP,
        "roadmap": ROADMAP,
        "lessons": enriched_lessons(),
        "assignments": ASSIGNMENTS,
        "mastery_gates": MASTERY_GATES,
        "labs": LABS,
        "quizzes": QUIZZES,
        "glossary": GLOSSARY,
    }


def lesson_by_id(lesson_id):
    return next((lesson for lesson in enriched_lessons() if lesson["id"] == lesson_id), None)


def quiz_by_id(quiz_id):
    return next((quiz for quiz in QUIZZES if quiz["id"] == quiz_id), None)


def mastery_gate_by_phase(phase_id):
    return next((gate for gate in MASTERY_GATES if gate["phase"] == phase_id), None)


def enriched_lessons():
    lessons = []
    for lesson in LESSONS:
        enriched = dict(lesson)
        enriched["math"] = [enrich_math_item(item) for item in lesson.get("math", [])]
        enriched["code_explanation"] = code_explanation_for(lesson)
        enriched["official_source"] = LESSON_SOURCE_URLS.get(lesson["id"], SOURCE_MAP["schedule"]["url"])
        enriched["official_material"] = official_material_for(enriched)
        enriched["mastery_gate"] = mastery_gate_by_phase(lesson["phase"])
        enriched["precision_note"] = precision_note_for(lesson["id"])
        lessons.append(enriched)
    return lessons


def enrich_math_item(item):
    enriched = dict(item)
    audit = FORMULA_AUDIT.get(item.get("formula", ""))
    if audit:
        enriched.update(audit)
        enriched["detail"] = formula_detail_for(item, audit)
    else:
        enriched.update(
            {
                "latex": item.get("formula", ""),
                "kind": "待审核表达",
                "validity": "这条公式尚未进入审核表，应回到官方材料确认。",
                "mathml": "",
                "detail": formula_detail_for(item, {}),
            }
        )
    return enriched


def formula_detail_for(item, audit):
    formula = item.get("formula", "")
    common = {
        "read_as": f"把它读作：{item.get('name', '这个表达式')} 用来说明 {item.get('explain', '本讲中的一个关键关系')}",
        "symbols": [
            "先定位等号或不等号左边：它通常是要定义、估算或优化的对象。",
            "再逐项看右边：每一项都应该能对应到张量形状、概率、资源量或训练信号。",
            "最后检查单位和维度：概率应无量纲，FLOPs 是操作数，bytes 是存储量，loss 通常是标量。",
        ],
        "steps": [
            "先用一句中文说出公式解决的问题。",
            "把每个符号替换成一个极小例子，例如 B=2、T=3、d=4。",
            "检查输出对象的形状或单位是否和左边一致。",
            "再回到代码，找出公式中每一项对应的变量名。",
        ],
        "pitfalls": [audit.get("validity", "细节以官方材料为准。")],
    }

    overrides = {
        "X in R^(batch x seq x d_model)": {
            "read_as": "X 是一个三维张量，第一维是 batch，第二维是 token 位置，第三维是每个 token 的隐藏向量。",
            "symbols": ["B 表示一次并行处理多少条序列。", "T 表示每条序列有多少个 token。", "d_model 表示每个 token 被表示成多少维向量。"],
            "steps": ["先确认输入 token ids 是 [B,T]。", "embedding 后每个 id 变成 d_model 维向量。", "因此隐藏状态 X 的 shape 变成 [B,T,d_model]。"],
            "pitfalls": ["不要把 T 和 d_model 混淆：T 是位置数量，d_model 是每个位置的特征数量。"],
        },
        "softmax(z_i) = exp(z_i) / sum_j exp(z_j)": {
            "read_as": "第 i 个类别的概率等于它的指数分数除以所有类别指数分数之和。",
            "symbols": ["z_i 是第 i 个 token 的 logit。", "V 是候选 token 数，也就是 vocabulary size。", "分母保证所有概率加起来等于 1。"],
            "steps": ["先对每个 logit 取指数，让更大的分数变得更突出。", "把所有指数值求和。", "每个指数值除以总和，得到概率分布。"],
            "pitfalls": ["代码中通常先减 max(z) 防止溢出；这不会改变 softmax 的结果。"],
        },
        "CE = -log p(target)": {
            "read_as": "交叉熵就是正确类别概率的负对数。",
            "symbols": ["target 是真实 token 的索引。", "p_y 是模型给真实 token 的概率。", "log 使用自然对数时单位是 nats。"],
            "steps": ["先用 softmax 得到所有 token 的概率。", "取出真实 token 的概率 p_y。", "对 p_y 取负 log，概率越高 loss 越小。"],
            "pitfalls": ["不要对已经是 log-probability 的值再次取 log；也不要忘记 batch/token 平均方式会影响数值大小。"],
        },
        "theta <- theta - lr * grad_theta L": {
            "read_as": "参数沿着 loss 梯度的反方向移动一小步。",
            "symbols": ["theta 是模型参数。", "eta 或 lr 是学习率。", "grad_theta L 是 loss 对参数的梯度。"],
            "steps": ["前向传播得到 loss。", "反向传播计算每个参数的梯度。", "用学习率缩放梯度。", "从参数中减去这个更新量。"],
            "pitfalls": ["这是最基础的梯度下降；AdamW 会加入动量、二阶矩估计和权重衰减。"],
        },
        "p(x_1,...,x_T)=prod_t p(x_t | x_<t)": {
            "read_as": "整段文本的概率被拆成每一步预测下一个 token 的概率连乘。",
            "symbols": ["x_t 是第 t 个 token。", "x_<t 是当前位置之前的所有 token。", "乘积从 t=1 到 T。"],
            "steps": ["先预测第一个 token。", "再在已有前缀条件下预测第二个 token。", "持续到第 T 个 token。", "把每一步条件概率相乘得到序列概率。"],
            "pitfalls": ["训练时通常使用 teacher forcing：条件前缀来自真实文本，不是模型自己生成的历史。"],
        },
        "L = -sum_t log p(x_t | x_<t)": {
            "read_as": "训练 loss 是每个真实下一个 token 负 log 概率的总和。",
            "symbols": ["p_theta 表示由参数 theta 定义的模型概率。", "x_t 是真实下一个 token。", "求和覆盖序列中的预测位置。"],
            "steps": ["对每个位置拿到模型 logits。", "用 softmax/log-softmax 得到真实 token 的 log 概率。", "取负号后累加或平均。"],
            "pitfalls": ["padding token、prompt token 或非 assistant token 是否计入 loss，需要看具体训练设置。"],
        },
        "(m x k) @ (k x n) costs about 2*m*k*n FLOPs": {
            "read_as": "一个 m by k 矩阵乘以 k by n 矩阵，大约需要 2mkn 次浮点操作。",
            "symbols": ["m 是输出矩阵行数。", "n 是输出矩阵列数。", "k 是每个输出元素点积的长度。"],
            "steps": ["输出矩阵有 m*n 个元素。", "每个元素需要 k 次乘法和约 k 次加法。", "所以总量约为 2*m*k*n FLOPs。"],
            "pitfalls": ["这是计数口径，不等于实际运行时间；运行时间还取决于硬件利用率和内存访问。"],
        },
        "AI = FLOPs / bytes_moved": {
            "read_as": "算术强度等于每搬运一个字节能做多少浮点操作。",
            "symbols": ["FLOPs 是计算量。", "bytes_moved 是数据搬运量。", "AI 越高越可能接近计算峰值。"],
            "steps": ["先估算某个 kernel 做了多少 FLOPs。", "再估算它从显存或缓存搬了多少字节。", "两者相除判断是更像 compute-bound 还是 memory-bound。"],
            "pitfalls": ["必须说明 bytes_moved 指哪一层存储；HBM、SRAM、cache 的结论可能不同。"],
        },
        "Attention(Q,K,V)=softmax(QK^T/sqrt(d_k))V": {
            "read_as": "用 Q 和 K 计算相关性权重，再用权重对 V 做加权平均。",
            "symbols": ["Q 是 query，表示当前位置想找什么信息。", "K 是 key，表示每个位置提供什么索引。", "V 是 value，表示真正被聚合的信息。", "d_k 是 key/query 的维度，用来缩放点积。"],
            "steps": ["计算 QK^T 得到每个 token 对其他 token 的打分。", "除以 sqrt(d_k) 避免维度变大导致 softmax 过尖。", "softmax 得到每行 attention 权重。", "权重乘 V 得到上下文混合表示。"],
            "pitfalls": ["decoder-only 模型还要加 causal mask，防止当前位置看到未来 token。"],
        },
        "x <- x + f(norm(x))": {
            "read_as": "先归一化 x，把它送进子层 f，再把结果加回原来的 x。",
            "symbols": ["x 是残差流中的隐藏状态。", "norm 通常是 LayerNorm 或 RMSNorm。", "f 可以是 attention 或 MLP。"],
            "steps": ["保留原始 x 作为捷径。", "对 x 做归一化稳定训练。", "子层计算增量信息。", "把增量加回残差流。"],
            "pitfalls": ["这是 pre-norm 写法；post-norm 的顺序不同，训练稳定性也不同。"],
        },
        "O(T^2 * d)": {
            "read_as": "标准 full attention 的主要成本随序列长度平方增长。",
            "symbols": ["T 是序列长度。", "d 是隐藏或 head 相关维度。", "O 表示只看主导增长阶。"],
            "steps": ["每个 token 要和 T 个 token 比较。", "T 个 token 一共形成 T*T 个分数。", "每个分数或聚合还涉及 d 维运算。"],
            "pitfalls": ["这只描述 attention 主项；完整 Transformer 层还包含 QKV 投影和 MLP。"],
        },
        "active_params << total_params": {
            "read_as": "MoE 每个 token 实际激活的参数远小于模型总参数。",
            "symbols": ["N_active 是被当前 token 使用的 expert 参数。", "N_total 是所有 expert 加起来的总参数。", "<< 表示远小于。"],
            "steps": ["模型有多个 expert。", "router 为每个 token 选择少数 expert。", "只有被选中的 expert 参与当前 token 计算。"],
            "pitfalls": ["总参数大不等于每个 token 计算量同样大；但通信和负载均衡会变复杂。"],
        },
        "performance <= min(peak_flops, bandwidth * arithmetic_intensity)": {
            "read_as": "实际性能不能超过计算峰值，也不能超过带宽能喂出来的计算速度。",
            "symbols": ["P_peak 是硬件理论计算峰值。", "B_mem 是内存带宽。", "AI 是算术强度。"],
            "steps": ["先看硬件最多每秒做多少 FLOPs。", "再看内存带宽乘以每字节可做的 FLOPs。", "取两个上界中更小的一个。"],
            "pitfalls": ["Roofline 是上界，不保证程序一定达到；kernel 实现差会更低。"],
        },
        "softmax can be updated block by block with running max and running sum": {
            "read_as": "softmax 可以分块维护最大值和指数和，最后得到和一次性计算相同的结果。",
            "symbols": ["m 是当前看到分数的最大值。", "ell 是按 m 缩放后的指数和。", "s_i 是 attention score。"],
            "steps": ["每次读入一个 score block。", "更新全局 running max。", "按新的 max 修正旧的指数和。", "用 running sum 归一化输出。"],
            "pitfalls": ["FlashAttention 是 exact attention；它节省 IO，不是近似 attention。"],
        },
        "grad = (grad_1 + ... + grad_n) / n": {
            "read_as": "多张卡各自算局部梯度，然后求平均得到全局梯度。",
            "symbols": ["g_i 是第 i 个 worker 的梯度。", "n 是 worker 数量。", "g 是 optimizer 用的平均梯度。"],
            "steps": ["每张卡处理不同 micro-batch。", "各自反向传播得到局部梯度。", "all-reduce 把梯度求和或平均。", "每张卡用同一个全局梯度更新参数。"],
            "pitfalls": ["如果 loss reduction 设置不一致，平均梯度的尺度会错。"],
        },
        "idle_fraction roughly = (stages - 1) / (micro_batches + stages - 1)": {
            "read_as": "流水线空转比例大约等于填充/排空阶段占总阶段的比例。",
            "symbols": ["p 是 pipeline stage 数。", "m 是 micro-batch 数。", "idle fraction 是设备没活干的时间比例。"],
            "steps": ["流水线开始时后面的 stage 还没输入。", "流水线结束时前面的 stage 已经没新任务。", "micro-batch 越多，中间满载时间越长，空转比例越低。"],
            "pitfalls": ["不同调度策略会改变精确数值；这是帮助建立直觉的近似式。"],
        },
        "L(N,D)=L_inf + A/N^alpha + B/D^beta": {
            "read_as": "loss 由不可约项、参数不足项和数据不足项组成。",
            "symbols": ["N 是参数量。", "D 是训练 token 数。", "L_inf 是理论下界或不可约损失。", "alpha、beta 控制收益递减速度。"],
            "steps": ["固定 D 增大 N，参数项下降。", "固定 N 增大 D，数据项下降。", "两项都是幂律下降，所以收益递减。"],
            "pitfalls": ["这是教学简化式；真实 scaling 实验要控制模型族、数据质量和训练 compute。"],
        },
        "bytes ~= 2 * layers * heads * seq * head_dim * bytes_per_value": {
            "read_as": "KV cache 显存约等于每层每头每个历史 token 的 K 和 V 数值存储量。",
            "symbols": ["2 表示 key 和 value 两份缓存。", "layers 是层数。", "heads 是 attention heads。", "seq 是缓存长度。", "head_dim 是每个 head 的维度。"],
            "steps": ["每个历史 token 在每层保存 K。", "同时保存 V。", "对所有层、所有头、所有位置累加。", "乘以每个数的字节数。"],
            "pitfalls": ["batch size 也要相乘；实际系统还会有分页、对齐和额外元数据开销。"],
        },
        "log(L-L_inf) ~= log A - alpha log N": {
            "read_as": "幂律关系在 log-log 坐标下近似变成直线。",
            "symbols": ["L 是观测 loss。", "L_inf 是不可约损失估计。", "A 是尺度常数。", "alpha 是斜率的相反数。"],
            "steps": ["从 L-L_inf = A/N^alpha 开始。", "两边取 log。", "得到 log A - alpha log N。", "拟合直线斜率就能估计 alpha。"],
            "pitfalls": ["L_inf 估错会严重影响拟合；不要在数据太少时过度外推。"],
        },
        "PPL = exp(cross_entropy)": {
            "read_as": "困惑度是平均交叉熵的指数。",
            "symbols": ["PPL 是 perplexity。", "cross_entropy 是按 token 平均的负 log likelihood。", "exp 把 log 空间量转回等效候选数直觉。"],
            "steps": ["先计算每个 token 的负 log 概率。", "对 token 求平均得到 cross entropy。", "取指数得到 PPL。"],
            "pitfalls": ["如果 loss 是总和而不是平均，直接 exp 会得到荒谬的大数。"],
        },
        "D = sum_i w_i D_i,  sum_i w_i = 1": {
            "read_as": "混合数据集是多个数据源按权重采样得到的分布。",
            "symbols": ["D_i 是第 i 个数据源。", "w_i 是该数据源采样权重。", "所有权重加起来为 1。"],
            "steps": ["列出数据源，例如 web、code、books、math。", "为每个来源分配非负权重。", "训练时按权重采样或构造 token 配比。"],
            "pitfalls": ["权重不是唯一因素；质量过滤、去重和重复采样也会改变有效数据分布。"],
        },
        "J(A,B)=|A intersect B| / |A union B|": {
            "read_as": "Jaccard 相似度等于两个集合交集大小除以并集大小。",
            "symbols": ["A、B 是两个文档的 shingle 集合。", "交集表示共同片段。", "并集表示总的不同片段。"],
            "steps": ["把文档切成 shingles。", "把 shingles 变成集合。", "计算共同元素数和总元素数。", "相除得到 0 到 1 之间的相似度。"],
            "pitfalls": ["Jaccard 看集合重叠，不直接理解语义；语义相似但词不同的文档可能分数低。"],
        },
        "L_SFT = -sum_t log pi_theta(y_t | x, y_<t)": {
            "read_as": "SFT 训练模型在给定指令和已生成前缀时，提高标准回答 token 的概率。",
            "symbols": ["x 是用户指令。", "y_t 是标准回答第 t 个 token。", "pi_theta 是模型策略。"],
            "steps": ["把 prompt 和示范回答拼成训练样本。", "模型逐位置预测回答 token。", "对回答 token 的负 log 概率求和或平均。"],
            "pitfalls": ["实际训练常只对 assistant answer 部分计 loss，而不是对整个 prompt 都计 loss。"],
        },
        "chosen should score higher than rejected": {
            "read_as": "偏好学习希望被人类偏好的回答得分高于被拒绝的回答。",
            "symbols": ["chosen 是偏好样本中的好回答。", "rejected 是较差回答。", "r_theta 是奖励模型或隐含偏好分数。"],
            "steps": ["给同一个 prompt 准备两条回答。", "标注哪条更好。", "训练目标推动 chosen 的相对得分更高。"],
            "pitfalls": ["这只是偏好关系；DPO、PPO/RLHF 会用不同方式把关系转成 loss。"],
        },
        "A = reward - baseline": {
            "read_as": "advantage 衡量某个回答比基准水平好多少。",
            "symbols": ["R 是该回答的奖励。", "b 是 baseline，例如组内平均奖励。", "A 为正表示比基准好。"],
            "steps": ["计算当前样本 reward。", "计算同组或价值函数 baseline。", "reward 减 baseline 得到 advantage。"],
            "pitfalls": ["advantage 的估计方式影响训练稳定性；不是所有 RL 算法都用同一个 baseline。"],
        },
        "penalty = beta * KL(pi_new || pi_ref)": {
            "read_as": "KL 惩罚限制新模型不要偏离参考模型太远。",
            "symbols": ["beta 是惩罚强度。", "pi_new 是正在训练的模型。", "pi_ref 是参考模型。", "KL 衡量两个分布差异。"],
            "steps": ["计算新模型对 token 的概率。", "计算参考模型概率。", "用 KL 衡量偏移。", "乘 beta 后作为惩罚加入目标。"],
            "pitfalls": ["KL 方向和 token 级估计方式依算法而定；beta 太大可能学不动，太小可能跑偏。"],
        },
        "similar(image, matching_text) > similar(image, wrong_text)": {
            "read_as": "匹配图文的相似度应该高于不匹配图文。",
            "symbols": ["I 是图像表示。", "T+ 是正确文本。", "T- 是错误文本。", "s 是相似度函数。"],
            "steps": ["用图像 encoder 得到图像向量。", "用文本 encoder 得到文本向量。", "提高匹配对相似度。", "降低不匹配对相似度。"],
            "pitfalls": ["完整对比学习通常是多样本 softmax loss，不只是一个不等式。"],
        },
        "effect(component)=metric(full)-metric(without_component)": {
            "read_as": "组件效果用完整系统指标减去移除该组件后的指标来估计。",
            "symbols": ["M_full 是完整系统指标。", "M_ablated 是移除组件后的指标。", "Delta 是观察到的差值。"],
            "steps": ["固定其他条件训练或评测完整系统。", "只移除一个组件。", "比较同一指标差异。"],
            "pitfalls": ["消融差异不是自动的因果证明；要控制随机种子、数据和训练预算。"],
        },
        "useful_model = data + architecture + optimization + evaluation + alignment": {
            "read_as": "一个可用语言模型来自数据、架构、优化、评测和对齐的共同作用。",
            "symbols": ["data 决定模型能学到什么。", "architecture 决定表达和计算结构。", "optimization 决定能否训练好。", "evaluation 暴露能力和风险。", "alignment 塑造可用行为。"],
            "steps": ["先保证数据管线可靠。", "再选择合适架构和训练方法。", "用系统优化控制成本。", "用评测和后训练迭代行为。"],
            "pitfalls": ["这不是数学等式，而是课程全链路总结。"],
        },
    }

    detail = overrides.get(formula, common)
    return {
        "read_as": detail.get("read_as", common["read_as"]),
        "symbols": detail.get("symbols", common["symbols"]),
        "steps": detail.get("steps", common["steps"]),
        "pitfalls": detail.get("pitfalls", common["pitfalls"]),
    }


CODE_PURPOSES = {
    "prep-python": "这段代码训练你养成 shape-first 的工程习惯：函数一开始就检查张量形状，错误尽早暴露。",
    "prep-tensors": "这段代码用纯 Python 写 softmax 和 cross entropy，帮助你先理解概率计算，再看 PyTorch 实现。",
    "prep-training-loop": "这段代码展示训练循环的固定骨架：forward、loss、backward、optimizer step。",
    "l01": "这段代码展示 BPE 训练中最核心的一步：统计语料里最常见的相邻符号对。",
    "l02": "这段代码把一个线性层的形状转成 FLOPs 和激活显存估算。",
    "l03": "这段代码是 pre-norm Transformer block 的最小结构：attention 子层加残差，MLP 子层再加残差。",
    "l04": "这段代码抽象展示 MoE router 如何为每个 token 选择 top-k experts。",
    "l05": "这段代码是硬件效率的注释型对比：同样数学操作，不同实现形态会产生完全不同的 GPU 利用率。",
    "l06": "这段伪代码展示 FlashAttention 的分块思想：按 Q block 和 KV block 流式计算，减少完整 attention matrix 的显存写入。",
    "l07": "这段伪代码展示数据并行的核心：各卡算局部梯度，再 all-reduce 得到全局梯度。",
    "l08": "这段代码展示 pipeline parallel 的切层方式：把不同 Transformer blocks 放到不同 stage。",
    "l09": "这段代码用简化 scaling law 计算预测 loss，帮助理解参数量和训练 token 都有递减收益。",
    "l10": "这段代码展示温度采样的核心：先缩放 logits，再 softmax，再随机采样。",
    "l11": "这段代码展示 scaling 实验记录应该是多点表格，而不是只看单个模型结果。",
    "l12": "这段代码展示最基础的 exact match 和 accuracy 评测实现。",
    "l13": "这段代码展示数据混合权重必须归一化，所有来源权重和应为 1。",
    "l14": "这段代码实现 Jaccard 相似度，用于理解近重复文档检测。",
    "l15": "这段代码展示偏好数据的基本结构：同一个 prompt 下有 chosen 和 rejected 两个回答。",
    "l16": "这段代码展示 RLVR 的奖励和 advantage 直觉：答案可验证，奖励相对 baseline 形成训练信号。",
    "l17": "这段代码展示多模态系统的数据流：视觉特征和文本特征需要投影到语言模型能使用的表示。",
    "l18": "这段代码展示消融实验表格，用来比较移除组件后的指标变化。",
    "l19": "这段代码把整门课的端到端流程写成项目 pipeline。",
}


def code_explanation_for(lesson):
    code = lesson.get("code", "")
    lines = code.splitlines()
    return {
        "purpose": CODE_PURPOSES.get(lesson["id"], f"这段代码用于把 {lesson['title']} 的核心概念落到最小可读实现。"),
        "concept_link": f"它对应本讲主题：{lesson['summary']}",
        "execution_order": execution_order_for(code),
        "line_notes": [
            {"line": index + 1, "code": line, "explain": explain_code_line(line, lesson)}
            for index, line in enumerate(lines)
        ],
    }


def execution_order_for(code):
    if "loss.backward()" in code and "optimizer.step()" in code:
        return ["取一个 batch。", "模型前向传播得到 logits。", "用 targets 计算 loss。", "清空旧梯度。", "反向传播计算新梯度。", "优化器更新参数。"]
    if "softmax" in code and "cross_entropy" in code:
        return ["先把 logits 变成概率。", "再取出正确类别概率。", "最后取负 log 得到 loss。"]
    if "Counter" in code or "most_common_pair" in code:
        return ["把词拆成符号序列。", "遍历每个相邻符号对。", "统计出现次数。", "选择出现最多的 pair 作为下一次 merge 候选。"]
    if "flops" in code or "activation_bytes" in code:
        return ["写清楚张量维度。", "用矩阵乘公式估算 FLOPs。", "用元素个数乘字节数估算显存。", "把结果转成容易读的单位。"]
    if "transformer_block" in code:
        return ["输入隐藏状态 x。", "attention 子层读取归一化后的 x 并产生上下文增量。", "把增量加回残差流。", "MLP 子层再加工每个位置。", "再次加回残差流并返回。"]
    if "for q_block" in code:
        return ["按 Q block 处理查询。", "初始化 online softmax 的 running state。", "逐个读取 KV block。", "计算当前 block 的 scores。", "更新 softmax 和输出。", "写回最终 output。"]
    return ["从上到下读变量定义。", "看每个中间变量保存什么。", "找到核心计算行。", "确认返回值或最终数据结构。"]


def explain_code_line(line, lesson):
    stripped = line.strip()
    if not stripped:
        return "空行用于分隔逻辑块，让代码阅读时能看出不同步骤。"
    if stripped.startswith("#"):
        return "注释行说明这一段代码的意图或张量形状，不参与运行，但对理解实现非常关键。"
    if stripped.startswith("import ") or stripped.startswith("from "):
        return "导入依赖。这里先把后面要用的数据结构或数学函数引入当前文件。"
    if stripped.startswith("def "):
        name = stripped.split("(", 1)[0].replace("def ", "")
        return f"定义函数 `{name}`。函数把一个概念封装成可重复调用的最小单元，便于测试和复用。"
    if stripped.startswith("return "):
        return "返回函数结果。读这一行时要检查返回值的类型、shape 或含义是否和函数目标一致。"
    if stripped.startswith("assert "):
        return "断言用于强制检查条件。条件不满足时立即报错，避免错误继续传到更深的模型逻辑里。"
    if stripped.startswith("for "):
        return "循环逐个处理集合里的元素。CS336 里要特别注意循环维度：是按 batch、token、layer，还是按 block 遍历。"
    if stripped.startswith("if "):
        return "条件分支处理特殊情况或判断奖励/匹配是否成立。理解时要看 true 和 false 分别代表什么语义。"
    if stripped.startswith("else"):
        return "else 分支覆盖条件不成立的情况，保证逻辑有完整返回路径。"
    if "optimizer.zero_grad()" in stripped:
        return "清空上一轮残留梯度。PyTorch 默认会累积梯度，所以每次普通训练 step 前都要清零。"
    if "loss.backward()" in stripped:
        return "反向传播。根据当前 loss 自动计算每个可训练参数的梯度。"
    if "optimizer.step()" in stripped:
        return "参数更新。优化器读取梯度，并按学习率、动量等规则修改模型参数。"
    if "softmax" in stripped:
        return "调用 softmax，把未归一化分数转换成概率分布。概率和应为 1。"
    if "math.exp" in stripped:
        return "对分数取指数。减去最大值是数值稳定技巧，防止指数溢出。"
    if "math.log" in stripped:
        return "取对数。交叉熵中使用负 log 概率，正确类别概率越高，loss 越低。"
    if "Counter" in stripped:
        return "Counter 用来统计出现次数，非常适合 BPE 中统计相邻 pair 的频率。"
    if "zip(" in stripped:
        return "zip(word, word[1:]) 会生成相邻符号对，例如 l-o、o-w。"
    if "most_common" in stripped:
        return "取出现次数最多的 pair。BPE 每一步通常合并当前最常见的相邻符号对。"
    if "flops" in stripped:
        return "计算 FLOPs 估算值。这里把张量形状代入矩阵乘成本公式。"
    if "activation_bytes" in stripped or "kvBytes" in stripped:
        return "估算显存字节数。核心方法是元素个数乘以每个元素的字节数。"
    if "layer_norm" in stripped or "norm(" in stripped:
        return "归一化隐藏状态，让不同维度的数值尺度更稳定，帮助深层 Transformer 训练。"
    if "self_attention" in stripped:
        return "attention 子层让当前位置聚合上下文信息，是 Transformer 中 token 交互的主要机制。"
    if "mlp" in stripped:
        return "MLP 子层对每个 token 的表示做非线性变换，不直接在不同 token 之间交换信息。"
    if "argsort" in stripped or "expert_ids" in stripped:
        return "router 根据分数选择 top-k experts。这里返回的是每个 token 应该送到哪些 expert。"
    if "running_max" in stripped or "running_sum" in stripped:
        return "这是 online softmax 的状态变量，用来分块计算时保持数值稳定和正确归一化。"
    if "scores" in stripped:
        return "scores 是 attention 打分，来自 query 和 key 的点积并按维度缩放。"
    if "all_reduce" in stripped:
        return "all-reduce 是多卡通信操作，把各卡梯度聚合成一致的全局梯度。"
    if "predicted_loss" in stripped:
        return "定义一个教学版 scaling law 函数，用参数量和 token 数预测 loss 趋势。"
    if "l_inf" in stripped:
        return "这些是 scaling law 的常数项和指数。真实实验中要用数据拟合，而不是随意指定。"
    if "temperature" in stripped:
        return "temperature 控制采样随机性。温度越高分布越平，输出越随机。"
    if "exact_match" in stripped or "accuracy" in stripped:
        return "这是评测函数。它把模型输出和标准答案转成一个可计算的指标。"
    if "jaccard" in stripped or "len(a & b)" in stripped or "len(a | b)" in stripped:
        return "这里计算集合交集和并集，用于衡量两个文档片段集合的重叠程度。"
    if "chosen" in stripped or "rejected" in stripped:
        return "偏好数据字段。chosen 表示更好的回答，rejected 表示较差回答。"
    if "reward" in stripped or "advantage" in stripped:
        return "奖励或 advantage 是强化学习训练信号，用来决定提高还是降低某个回答的概率。"
    if "encoder" in stripped or "projector" in stripped:
        return "多模态组件把不同模态编码成向量，并投影到语言模型可处理的表示空间。"
    if "=" in stripped:
        left = stripped.split("=", 1)[0].strip()
        return f"赋值语句。左边 `{left}` 保存右边计算结果，后续代码会继续使用这个中间量。"
    return "这一行是当前示例的结构性代码。读它时要问：输入是什么，输出是什么，它服务于本讲哪个概念。"


def precision_note_for(lesson_id):
    if lesson_id.startswith("prep-"):
        return "这是本项目为初学者补充的预备内容，不是 CS336 正式 lecture，但对应官网 prerequisite 要求。"
    if lesson_id in {"l09", "l11"}:
        return "本项目中的 scaling law 公式用于教学演示；真实作业需要按官方 handout 的实验设置和数据拟合。"
    if lesson_id in {"l06"}:
        return "本项目只解释 FlashAttention/Triton 的核心机制，不等价于完成官方 Triton kernel 实现。"
    if lesson_id in {"l15", "l16"}:
        return "本项目展示后训练/RL 的最小数学信号，不会替代官方作业中的真实实现和测试。"
    return "本讲内容按官方 lecture 主题组织；中文解释是教学拆解，细节以官方材料为准。"
