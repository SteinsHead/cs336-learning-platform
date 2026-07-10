"""Lesson-scoped assessments and CPU-only implementation studios.

The tasks intentionally use tiny deterministic inputs. They assess the same
reasoning and implementation boundaries as CS336 without requiring a GPU or
training a useful language model.
"""


def question(prompt, options, answer, explain):
    return {"prompt": prompt, "options": options, "answer": answer, "explain": explain}


LESSON_QUESTION_BANK = {
    "prep-python": [
        question("张量 x 的 shape 是 [B,T,D]。哪一维表示序列位置？", ["B", "T", "D", "三者都不是"], 1, "T 是 sequence length；B 是 batch，D 是隐藏维度。"),
        question("单元测试最重要的作用是什么？", ["让代码更长", "替代类型和 shape", "自动验证行为和边界条件", "提高 GPU 峰值算力"], 2, "单元测试把期望行为变成可重复检查的契约。"),
        question("发现输入 shape 不符合函数契约时，最合理的做法是？", ["尽早抛出明确错误", "静默 reshape", "返回随机结果", "忽略 batch 维"], 0, "越早暴露 shape 错误，越容易定位真实原因。"),
    ],
    "prep-tensors": [
        question("softmax 输出必须满足什么性质？", ["每项都大于 1", "所有项之和为 1", "最大项一定等于 1", "允许负概率"], 1, "softmax 把 logits 归一化为概率分布。"),
        question("计算稳定 softmax 时先减去 max(logits) 的原因是？", ["改变概率排序", "让梯度恒为零", "避免指数溢出且不改变结果", "减少词表大小"], 2, "softmax 对整体平移不变，减最大值能改善数值稳定性。"),
        question("正确类别概率从 0.1 提升到 0.5 时，-log(p) 会怎样？", ["降低", "升高", "保持不变", "变成负数"], 0, "正确类别概率越高，负对数似然越低。"),
    ],
    "prep-training-loop": [
        question("采用每步开头清梯度的普通 PyTorch 训练循环，标准顺序是？", ["step→forward→backward", "zero_grad→forward→loss→backward→step", "backward→zero_grad→forward", "loss→step→forward"], 1, "先清除上一步梯度，再前向计算 loss、反向传播并更新参数。"),
        question("为什么每个普通训练 step 前要 zero_grad？", ["PyTorch 默认会累积梯度", "模型没有参数", "softmax 需要归一化", "验证集必须清空"], 0, "PyTorch 默认把新梯度累加到已有梯度。"),
        question("训练 loss 持续下降但验证 loss 上升，最可能说明？", ["欠拟合", "数据完全正确", "过拟合", "学习率一定为零"], 2, "训练集继续改善而泛化变差是典型过拟合信号。"),
    ],
    "l01": [
        question("BPE 每一步选择什么进行合并？", ["最少见单词", "最长句子", "当前最常见的相邻符号对", "随机两个 token"], 2, "经典 BPE 迭代合并当前语料中频率最高的相邻符号对。"),
        question("字节级 tokenizer 的重要优点是？", ["任何输入都能表示，不需要 OOV token", "序列永远最短", "自动理解语义", "词表无限大"], 0, "任意字符串都可编码为字节，因此不存在无法表示的字符。"),
        question("自回归 LM 的联合概率如何分解？", ["各 token 边缘概率相加", "每步条件概率相乘", "只计算最后一个 token", "对 logits 取最大值"], 1, "链式法则把序列概率分解为逐 token 条件概率的乘积。"),
    ],
    "l02": [
        question("(m×k)@(k×n) 的主要 FLOPs 约为？", ["m+k+n", "mkn", "2mkn", "m²n²"], 2, "每个输出元素约有 k 次乘法和 k 次加法，因此约 2mkn。"),
        question("算术强度的定义是？", ["FLOPs / bytes moved", "bytes / 参数量", "带宽 / 延迟", "峰值算力 / batch"], 0, "算术强度衡量每移动一个字节完成多少计算。"),
        question("低算术强度 kernel 通常首先受什么限制？", ["词表大小", "内存带宽", "模型精度", "随机种子"], 1, "每字节计算很少时，搬运数据通常比计算更早成为瓶颈。"),
    ],
    "l03": [
        question("attention 中除以 sqrt(d_k) 的主要原因是？", ["减少 token 数", "避免点积随维度增大导致 softmax 过度饱和", "删除 causal mask", "共享 Q/K 参数"], 1, "缩放控制点积方差，使 softmax 和梯度保持在合理范围。"),
        question("decoder-only 模型的 causal mask 阻止什么？", ["当前位置读取未来 token", "不同 head 并行", "MLP 处理 token", "embedding 查表"], 0, "自回归预测不能使用尚未生成的未来信息。"),
        question("Transformer MLP 子层主要在哪个维度独立工作？", ["不同 batch 之间", "不同 token 位置上共享参数并逐位置处理", "不同训练任务之间", "只在词表维"], 1, "MLP 对每个位置独立应用同一组参数，token 间交互主要来自 attention。"),
    ],
    "l04": [
        question("full attention 的序列长度主项复杂度是？", ["O(T)", "O(log T)", "O(T²)", "O(1)"], 2, "T 个 query 与 T 个 key 两两比较形成 T×T 分数矩阵。"),
        question("MoE 中 top-k routing 表示？", ["每个 token 只进入得分最高的少数 expert", "每个 token 进入所有 expert", "删除 router", "只训练一个 expert"], 0, "稀疏激活让总参数量大于每 token 实际使用的参数量。"),
        question("MoE 为什么需要负载均衡约束？", ["避免所有 token 挤到少数 expert", "让词表变大", "替代 attention mask", "消除通信"], 0, "路由塌缩会造成 expert 过载、容量溢出和训练效率下降。"),
    ],
    "l05": [
        question("Roofline 模型中的性能上界由什么共同决定？", ["峰值算力与带宽×算术强度", "参数量与词表", "batch 与随机种子", "验证集与 tokenizer"], 0, "程序受计算峰值和内存带宽两条屋顶线共同限制。"),
        question("相较寄存器/SRAM，HBM 的典型特征是？", ["容量更小且更快", "容量更大但访问更慢", "不保存张量", "只能存整数"], 1, "GPU 内存层级通过容量与速度的权衡组织。"),
        question("大量很小的 kernel 为什么可能很慢？", ["启动开销和并行度不足", "FLOPs 一定太多", "数据一定正确", "会增大模型精度"], 0, "小 kernel 难以摊薄启动开销，也可能无法占满硬件。"),
    ],
    "l06": [
        question("FlashAttention 是否改变 attention 的数学结果？", ["是近似 attention", "不改变，它是 IO-aware exact attention", "删除 softmax", "只适用于 CPU"], 1, "在数值误差范围内它计算同一个 attention，只改变分块与内存访问。"),
        question("online softmax 合并新 block 时必须维护什么？", ["running max 与归一化和", "词表与 tokenizer", "optimizer state", "训练标签"], 0, "running max 和指数和允许稳定地合并分块结果。"),
        question("FlashAttention 的主要节省来自？", ["不再保存完整 T×T 中间矩阵到 HBM", "减少模型层数", "降低词表", "跳过 V"], 0, "分块复用片上存储，减少昂贵的 HBM 读写。"),
    ],
    "l07": [
        question("数据并行中每张卡通常持有什么？", ["完整模型和不同数据分片", "模型的一层且相同数据", "只有 tokenizer", "不同词表"], 0, "数据并行复制模型、切分 batch，并在反向后同步梯度。"),
        question("all-reduce 的主要用途是？", ["聚合各 worker 梯度", "下载数据", "生成 token", "保存 checkpoint"], 0, "各卡需要一致的聚合梯度才能保持参数同步。"),
        question("activation checkpointing 用什么换显存？", ["重算带来的额外计算", "更大的词表", "更少训练数据", "更低网络带宽"], 0, "它少存中间激活，在反向传播时重新计算。"),
    ],
    "l08": [
        question("tensor parallel 主要切分什么？", ["单层内部的张量/矩阵运算", "训练日期", "验证集标签", "文件系统"], 0, "tensor parallel 把单层的大矩阵计算分布到多设备。"),
        question("pipeline parallel 主要切分什么？", ["不同模型层/阶段", "一个标量", "tokenizer 词表", "loss 函数"], 0, "不同 stage 持有不同连续层，micro-batch 流过流水线。"),
        question("增加 micro-batch 数通常如何影响 pipeline bubble？", ["降低 bubble 占比", "必然增大到 100%", "没有任何关系", "删除通信"], 0, "更多 micro-batch 延长稳态区间，摊薄填充和排空开销。"),
    ],
    "l09": [
        question("scaling law 中幂指数通常表达什么？", ["收益递减速度", "随机种子", "GPU 数量上限", "tokenizer 类型"], 0, "幂律指数控制参数或数据增加时 loss 下降的速率。"),
        question("compute-optimal training 的核心是？", ["在给定计算预算下平衡参数量和训练 token", "只增大参数", "只增大 batch", "忽略数据质量"], 0, "模型过大数据不足或模型过小数据过多都可能浪费预算。"),
        question("L_inf 在简化 scaling law 中表示？", ["不可约损失下界项", "学习率", "层数", "显存"], 0, "它表示在该模型族和数据分布假设下无法靠简单扩展消除的项。"),
    ],
    "l10": [
        question("prefill 与 decode 的主要区别是？", ["prefill 并行处理已有 prompt，decode 逐 token 生成", "两者完全相同", "decode 不用模型", "prefill 不计算 attention"], 0, "prefill 可并行处理 prompt；decode 有自回归依赖。"),
        question("KV cache 保存什么？", ["历史 token 每层的 key/value", "所有训练梯度", "完整数据集", "optimizer 动量"], 0, "缓存历史 K/V 避免每次 decode 重算过去 token。"),
        question("其他条件不变时，KV cache 显存随上下文长度如何变化？", ["近似线性增长", "近似平方增长", "保持不变", "指数下降"], 0, "每多一个历史 token，需要在每层增加一份 K 和 V。"),
    ],
    "l11": [
        question("幂律为什么常在 log-log 坐标拟合？", ["幂律关系可近似线性化", "自动消除所有噪声", "不需要控制变量", "让 loss 恒为零"], 0, "取对数把乘法和指数关系转成截距与斜率。"),
        question("外推 scaling law 最大的风险是？", ["训练分布、模型族或规模区间变化使规律失效", "图表颜色变化", "token id 从 0 开始", "batch 是整数"], 0, "经验规律只在受控实验和观察范围附近更可信。"),
        question("拟合参数 scaling 时应尽量固定什么？", ["数据、训练配置和模型族等其他变量", "所有观测点的 loss", "随机数输出", "模型名称"], 0, "控制变量是解释斜率和比较实验的前提。"),
    ],
    "l12": [
        question("perplexity 与平均交叉熵的关系是？", ["PPL=exp(CE)", "PPL=CE²", "PPL=1/CE", "没有关系"], 0, "使用自然对数时，困惑度是平均 token 交叉熵的指数。"),
        question("benchmark contamination 指什么？", ["训练数据包含评测题或近重复内容", "评测运行太慢", "模型参数太少", "GPU 温度过高"], 0, "污染会让评测分数不能代表真正泛化能力。"),
        question("为什么不能只看单一 accuracy？", ["不同能力、校准和失败模式可能被掩盖", "accuracy 永远错误", "模型没有输出", "会改变 tokenizer"], 0, "可靠评测需要多指标、分层样本和误差分析。"),
    ],
    "l13": [
        question("数据混合权重之和通常应为？", ["0", "1", "词表大小", "batch size"], 1, "把权重解释为采样概率时应非负且和为 1。"),
        question("为什么数据许可需要在训练前处理？", ["决定数据能否被合法使用和分发", "提高 tensor core 频率", "替代去重", "生成 causal mask"], 0, "数据来源、版权、隐私和使用条款是数据管线的一部分。"),
        question("Common Crawl 原始数据通常还需要什么才能用于预训练？", ["提取、过滤、去重、混合和 tokenization", "直接复制到模型权重", "只改文件名", "删除所有非英文"], 0, "原始网页包含模板、垃圾、重复和风险内容，需要完整处理链。"),
    ],
    "l14": [
        question("Jaccard 相似度使用什么比值？", ["交集大小/并集大小", "并集/交集", "长度之和", "向量点积"], 0, "J(A,B)=|A∩B|/|A∪B|。"),
        question("MinHash 的主要用途是？", ["近似估计集合 Jaccard 相似度", "训练 optimizer", "计算 attention", "压缩权重"], 0, "MinHash 用紧凑签名减少大规模近重复比较成本。"),
        question("合成数据反复自举的风险是？", ["错误和分布偏差被放大", "一定提升所有能力", "完全没有许可问题", "消除评测需求"], 0, "合成数据必须配合质量控制、来源追踪和真实数据锚点。"),
    ],
    "l15": [
        question("SFT 的训练信号来自？", ["示范回答 token 的监督似然", "仅最终 reward", "GPU 带宽", "随机路由"], 0, "SFT 对高质量示范回答做 teacher-forced 最大似然训练。"),
        question("reward model 通常学习什么？", ["给定 prompt 时回答的相对偏好分数", "tokenizer merge", "显存分配", "KV cache"], 0, "偏好对让奖励模型学习 chosen 应高于 rejected。"),
        question("DPO 的特点是？", ["直接从偏好对优化策略相对参考模型的概率", "必须显式训练 PPO value model", "只训练 tokenizer", "不需要偏好数据"], 0, "DPO 把偏好关系转成闭式分类式目标，不需要在线 RL rollout。"),
    ],
    "l16": [
        question("RLVR 的奖励与传统 RLHF 偏好奖励有何不同？", ["RLVR 使用可程序验证的结果信号", "RLVR 没有奖励", "RLHF 只看 GPU", "两者都只靠人工逐 token 标注"], 0, "数学答案、代码测试等可以提供自动验证奖励。"),
        question("group-relative advantage 的作用是？", ["比较同组回答相对基准的好坏", "增大词表", "删除 reference model", "固定所有概率"], 0, "相对基准能降低不同 prompt 奖励尺度差异。"),
        question("只奖励最终答案可能导致什么？", ["过程不可解释或 reward hacking", "必然得到最短证明", "消除探索", "让 KL 恒为零"], 0, "模型可能找到投机路径，正确结果不保证可靠过程。"),
    ],
    "l17": [
        question("视觉 encoder 与语言模型之间的 projector 用于？", ["对齐表示维度和空间", "下载图片", "替代所有文本 token", "计算 optimizer state"], 0, "projector 把视觉表示转换成语言模型可消费的表示。"),
        question("对比学习希望匹配图文相对于不匹配图文怎样？", ["相似度更高", "相似度更低", "完全相等", "不计算表示"], 0, "匹配对被拉近，不匹配对被推远。"),
        question("多模态安全评测为什么不能只测文本？", ["图像、OCR、跨模态组合会产生新的攻击面", "文本没有 token", "视觉模型没有参数", "图片一定安全"], 0, "风险可能来自单一模态或跨模态组合。"),
    ],
    "l18": [
        question("可靠消融实验最重要的原则是？", ["只改变目标组件并控制其他条件", "同时修改所有变量", "只报告最好一次", "不保留 baseline"], 0, "控制变量和重复实验是解释差异的基础。"),
        question("研究报告中的 baseline 用于？", ["提供可比较参照", "替代问题定义", "隐藏失败案例", "保证因果结论"], 0, "没有合理 baseline，很难判断方法是否真正改进。"),
        question("从客座研究讲座中最应提取什么？", ["问题、方法、证据、限制与资源约束", "只记模型名称", "只记作者单位", "只看最终数字"], 0, "研究阅读要把主张与证据链对应起来。"),
    ],
    "l19": [
        question("端到端语言模型系统中，评测的作用是？", ["暴露能力、回归和风险并驱动迭代", "替代训练数据", "只用于发布宣传", "删除监控"], 0, "评测连接研发决策、上线门槛和持续监控。"),
        question("固定算力下提高系统价值通常需要？", ["联合权衡数据、模型、系统、评测和对齐", "只增大参数", "只延长输出", "忽略推理成本"], 0, "课程主线是跨模块资源权衡，而不是单点最优。"),
        question("模型卡应至少记录什么？", ["能力边界、评测、数据与风险", "只有模型名字", "只有参数量", "只有 GPU 型号"], 0, "可审计交付需要记录适用范围、限制和证据。"),
    ],
}


LESSON_QUIZZES = [
    {
        "id": f"quiz-{lesson_id}",
        "lesson_id": lesson_id,
        "title": f"本讲形成性自测 · {lesson_id}",
        "questions": questions,
    }
    for lesson_id, questions in LESSON_QUESTION_BANK.items()
]


def studio(task_id, assignment_id, lesson_ids, title, objective, starter_code, test_code, hints):
    return {
        "id": task_id,
        "assignment_id": assignment_id,
        "lesson_ids": lesson_ids,
        "title": title,
        "objective": objective,
        "starter_code": starter_code,
        "test_code": test_code,
        "hints": hints,
    }


PRACTICE_STUDIOS = [
    studio("shape-contract", "prep", ["prep-python"], "Shape 契约", "实现一个返回三维 shape 语义的函数，并拒绝非三维输入。", """def describe_shape(shape):
    # 返回 {\"batch\": B, \"sequence\": T, \"hidden\": D}
    raise NotImplementedError
""", """_expect("正常 shape", describe_shape((2, 3, 4)), {"batch": 2, "sequence": 3, "hidden": 4})
_expect_raises("拒绝二维输入", lambda: describe_shape((2, 3)))
""", ["先检查 len(shape) == 3。", "错误输入应抛出 ValueError。"]),
    studio("stable-softmax", "prep", ["prep-tensors"], "稳定 Softmax", "只用 Python 标准库实现数值稳定 softmax。", """import math

def stable_softmax(values):
    raise NotImplementedError
""", """_expect_close("概率和", sum(stable_softmax([1.0, 2.0, 3.0])), 1.0)
_expect("排序不变", stable_softmax([1.0, 2.0])[1] > stable_softmax([1.0, 2.0])[0], True)
_expect_close("大数稳定", sum(stable_softmax([1000.0, 1001.0])), 1.0)
""", ["先减去最大值。", "空输入应明确报错，不要静默返回。"]),
    studio("training-order", "prep", ["prep-training-loop"], "训练步骤排序", "把训练循环的依赖顺序编码成可测试函数。", """def training_step_order():
    # 返回六个步骤名称组成的列表
    raise NotImplementedError
""", """_expect("完整顺序", training_step_order(), ["zero_grad", "forward", "loss", "backward", "step", "metrics"])
""", ["每步开头先清除上一步累积的梯度。", "梯度来自当前 loss；metrics 放在 step 后记录更新结果。"]),
    studio("bpe-pairs", "a1", ["l01"], "BPE Pair 统计", "统计词内相邻符号对，不跨单词边界。", """from collections import Counter

def pair_counts(words):
    # words: list[list[str]]
    raise NotImplementedError
""", """_expect("基本计数", pair_counts([list("low"), list("lower")])[("l", "o")], 2)
_expect("不跨词", ("w", "l") in pair_counts([list("low"), list("lower")]), False)
""", ["对每个 word 单独 zip(word, word[1:])。"]),
    studio("resource-accounting", "a1", ["l02"], "矩阵乘资源核算", "根据矩阵形状计算 FLOPs 和 fp32 输出字节数。", """def matmul_resources(m, k, n):
    # 返回 {\"flops\": ..., \"output_bytes\": ...}
    raise NotImplementedError
""", """_expect("FLOPs", matmul_resources(2, 3, 4)["flops"], 48)
_expect("输出字节", matmul_resources(2, 3, 4)["output_bytes"], 32)
""", ["FLOPs 约为 2*m*k*n。", "输出有 m*n 个 fp32 元素。"]),
    studio("attention-reference", "a1", ["l03", "l04"], "Attention 参考实现", "实现单 query、多个标量 key/value 的 scaled attention。", """import math

def scalar_attention(query, keys, values):
    # 返回 (weights, output)
    raise NotImplementedError
""", """w, out = scalar_attention(1.0, [1.0, 0.0], [10.0, 0.0])
_expect_close("权重和", sum(w), 1.0)
_expect("偏向匹配 key", w[0] > w[1], True)
_expect_close("输出", out, w[0] * 10.0)
""", ["标量 head 的 d_k=1。", "先稳定 softmax，再对 value 加权。"]),
    studio("online-softmax", "a2", ["l05", "l06"], "分块 Online Softmax", "合并两个 score block，结果应与一次性 softmax 一致。", """import math

def online_softmax(blocks):
    # blocks 是多个 score list；返回拼接后的概率
    raise NotImplementedError
""", """p = online_softmax([[1.0, 2.0], [3.0]])
e = [math.exp(x - 3.0) for x in [1.0, 2.0, 3.0]]
expected = [x / sum(e) for x in e]
_expect_sequence_close("exact softmax", p, expected)
_expect_close("概率和", sum(p), 1.0)
""", ["维护全局 running max。", "旧 block 的指数和在 max 更新后要重新缩放。"]),
    studio("parallel-costs", "a2", ["l07", "l08"], "并行代价", "实现梯度平均和 GPipe bubble 近似。", """def average_gradients(worker_grads):
    raise NotImplementedError

def pipeline_idle_fraction(stages, micro_batches):
    raise NotImplementedError
""", """_expect_sequence_close("梯度平均", average_gradients([[1.0, 3.0], [3.0, 5.0]]), [2.0, 4.0])
_expect_close("bubble", pipeline_idle_fraction(4, 8), 3 / 11)
""", ["逐参数位置平均。", "bubble≈(p-1)/(m+p-1)。"]),
    studio("scaling-fit", "a3", ["l09", "l11"], "Log-log 斜率", "不用第三方库实现一元线性回归斜率。", """import math

def loglog_slope(xs, ys):
    raise NotImplementedError
""", """_expect_close("幂律斜率", loglog_slope([1, 2, 4, 8], [8, 4, 2, 1]), -1.0)
_expect_raises("长度不匹配", lambda: loglog_slope([1], [1, 2]))
""", ["先对 x、y 取 log。", "斜率=cov(x,y)/var(x)。"]),
    studio("kv-cache", "a2", ["l10"], "KV Cache 显存", "计算包含 batch 的 KV cache 字节数。", """def kv_cache_bytes(batch, layers, heads, sequence, head_dim, bytes_per_value=2):
    raise NotImplementedError
""", """_expect("基础计算", kv_cache_bytes(2, 4, 8, 16, 32, 2), 2 * 2 * 4 * 8 * 16 * 32 * 2)
_expect("序列线性", kv_cache_bytes(1, 2, 2, 20, 4), 2 * kv_cache_bytes(1, 2, 2, 10, 4))
""", ["最前面的 2 表示 K 和 V。", "不要漏掉 batch。"]),
    studio("evaluation-metrics", "a4", ["l12"], "评测指标", "实现按 token 平均 NLL 的 perplexity。", """import math

def perplexity(token_probabilities):
    raise NotImplementedError
""", """_expect_close("确定分布", perplexity([1.0, 1.0]), 1.0)
_expect_close("均匀二选一", perplexity([0.5, 0.5]), 2.0)
_expect_raises("拒绝零概率", lambda: perplexity([0.0]))
""", ["先平均 -log(p)。", "最后取 exp。"]),
    studio("data-dedup", "a4", ["l13", "l14"], "Shingle Jaccard", "将文本切成 word shingles 并计算 Jaccard。", """def shingles(text, size=2):
    raise NotImplementedError

def jaccard(left, right):
    raise NotImplementedError
""", """a = shingles("language models learn from data")
b = shingles("models learn from clean data")
_expect("二元 shingle", ("language", "models") in a, True)
_expect_close("完全相同", jaccard(a, a), 1.0)
_expect_close("空集合", jaccard(set(), set()), 1.0)
""", ["shingle 使用 tuple，集合会自动去重。", "约定两个空集合相似度为 1。"]),
    studio("sft-loss", "a5", ["l15"], "SFT Token Loss", "根据 assistant token 概率计算平均负对数似然。", """import math

def sft_loss(answer_token_probabilities):
    raise NotImplementedError
""", """_expect_close("完美预测", sft_loss([1.0, 1.0]), 0.0)
_expect_close("二选一", sft_loss([0.5, 0.5]), math.log(2.0))
""", ["只对 answer token 计 loss。", "使用平均值便于跨长度比较。"]),
    studio("group-advantage", "a5", ["l16"], "组内 Advantage", "计算每个 reward 相对组平均的 advantage。", """def group_advantages(rewards):
    raise NotImplementedError
""", """_expect_sequence_close("中心化", group_advantages([1.0, 0.0, 2.0]), [0.0, -1.0, 1.0])
_expect_close("和为零", sum(group_advantages([1.0, 0.0, 2.0])), 0.0)
""", ["baseline 是组内平均 reward。"]),
    studio("contrastive-margin", "a5", ["l17"], "图文对比 Margin", "计算匹配相似度相对最强负样本的 margin。", """def contrastive_margin(positive_similarity, negative_similarities):
    raise NotImplementedError
""", """_expect_close("margin", contrastive_margin(0.8, [0.1, 0.5, 0.3]), 0.3)
_expect_raises("需要负样本", lambda: contrastive_margin(0.8, []))
""", ["使用 hardest negative，也就是最大负样本相似度。"]),
    studio("ablation-report", "capstone", ["l18", "l19"], "消融结论", "从重复实验结果计算均值差，并返回保守结论。", """def ablation_effect(full_scores, ablated_scores):
    # 返回 {\"delta\": ..., \"supported\": bool}
    raise NotImplementedError
""", """result = ablation_effect([0.72, 0.71, 0.73], [0.65, 0.66, 0.64])
_expect_close("均值差", result["delta"], 0.07)
_expect("支持改进", result["supported"], True)
""", ["比较两组均值。", "只有 delta>0 才能说当前重复实验支持改进，但仍不是自动因果证明。"]),
]


def quiz_for_lesson(lesson_id):
    return next((quiz for quiz in LESSON_QUIZZES if quiz["lesson_id"] == lesson_id), None)


def studio_by_id(task_id):
    return next((task for task in PRACTICE_STUDIOS if task["id"] == task_id), None)
