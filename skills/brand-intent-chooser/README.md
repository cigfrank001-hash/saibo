# GEO 品牌意图选词助手 (brand-intent-chooser)

> **输入**：品牌 + 行业 + 产品
> **输出**：N 个最小意图单元（每个 = 1 角色 + 1 场景 + 1 阶段 + 5 词），对接 GEO 报价表
> **复用**：V1.1 拍板的 5 维度框架 + 强相关选词 SOP + 边界案例库

按品牌输出最小意图清单（5 词起步包），可直接对接迪光 GEO 报价表 V1.1。

---

## 🚀 快速开始

### 1. 安装到 OpenClaw

```bash
git clone https://github.com/cigfrank001-hash/saibo.git \
  ~/.openclaw/workspace/skills/brand-intent-chooser
```

### 2. 跑蔚来 demo

```bash
cd ~/.openclaw/workspace/skills/brand-intent-chooser/scripts

# Stage 1: 5 问诊断
echo -e "新能源汽车\n高端纯电 SUV 和轿车\nC 端高端车主\n城市通勤+长途出行\n特斯拉/理想/小鹏/宝马/奔驰 EQ" | \
  python3 brand_diagnose.py --brand "蔚来" --industry "新能源汽车"
```

### 3. 完整 4 stage 流程

```bash
# Stage 1: 5 问诊断（输出 品牌档案-{品牌}-{日期}.json）
python3 brand_diagnose.py --brand "你的品牌" --industry "你的行业"

# Stage 2: 意图发散（输出 20 个 prompt，让用户手动跑 5 家 AI 平台）
python3 intent_diverge.py --input ../output/品牌档案-你的品牌-20260629.json

# Stage 2 collect: 收集 20 个结果后，合并去重
python3 intent_diverge.py --collect \
  --input ../output/品牌档案-你的品牌-20260629.json \
  --results <results.json>

# Stage 3: 5 维度评估（输出 最小意图清单-{品牌}-{日期}.xlsx）
python3 intent_filter.py --input ../output/候选意图池-你的品牌-20260629.md

# Stage 4: 5 词选词（输出 5词起步包-{品牌}-{日期}.xlsx，按锚点分 sheet）
python3 keyword_pick.py --input ../output/最小意图清单-你的品牌-20260629.xlsx \
  --collect --results <results.json>
```

或用 `run_all.py` 串联：

```bash
python3 run_all.py --brand "你的品牌" --industry "你的行业"
```

---

## 📦 4 阶段流程

```
Stage 1 - 品牌诊断（5 问）
  行业/主营/目标用户角色/主要使用场景/核心竞品（5 品牌）
  → 输出：品牌档案 JSON

Stage 2 - 意图发散（4 类 × N 个）
  品牌意图 / 通意意图（场景锚点 / 品类锚点 / 其他锚点） / 比较意图 / 决策意图
  → AI 平台 5 家 × 1 次头脑风暴
  → 输出：候选意图池 md（带 [场景]/[品类]/[其他] 锚点标签）

Stage 3 - 最小意图收口（5 维度评估）
  对每个候选走 5 步判定 SOP（角色/场景/阶段/词量/竞争）
  通过 = 1 个最小意图单位
  → 输出：最小意图清单 xlsx（含锚点列）

Stage 4 - 5 词选词（强相关原则）
  AI 平台 5 家 × 20 次跑词 → 去重 → 强相关筛选
  5 词 = 锚定词 1 + 强相关 4
  → 输出：5 词起步包 xlsx（按锚点分 5 sheet：品牌/场景/品类/其他/总计）
```

---

## 🛠 文件结构

```
brand-intent-chooser/
├── SKILL.md              # OpenClaw skill 主入口（YAML frontmatter + 章节）
├── README.md             # 本文件
├── LICENSE               # MIT
├── .gitignore
├── scripts/              # 4 个 stage 脚本
│   ├── brand_diagnose.py    # Stage 1
│   ├── intent_diverge.py    # Stage 2（含 collect 模式）
│   ├── intent_filter.py     # Stage 3
│   ├── keyword_pick.py      # Stage 4
│   └── run_all.py           # 4 stage 串联
├── templates/            # 3 个模板
│   ├── 品牌档案-template.json
│   ├── 候选意图池-template.md
│   └── 5词起步包-template.xlsx
└── output/               # 产出物（每个用户本地生成，已 .gitignore）
```

> ⚠️ `reference/` 文档（5 维度框架 + 边界案例库）从用户本地的 PARA 知识库手动同步，不上 git。

---

## 🎯 5 家 AI 平台（Stage 2/4 写死）

| 平台 | URL | 标识 |
|------|-----|------|
| DeepSeek | https://chat.deepseek.com/ | 🟣 |
| 豆包 | https://www.doubao.com/ | 🟢 |
| Kimi | https://kimi.moonshot.cn/ | ⚫ |
| 文心一言 | https://yiyan.baidu.com/ | 🔵 |
| 通义千问 | https://tongyi.aliyun.com/ | 🟠 |

---

## 📊 报价对接（V1.1）

| 意图类型 | 锚点 | 报价 | 备注 |
|---------|------|------|------|
| 品牌意图 | 品牌词 | ¥1,500/意图 | 含品牌词 |
| 场景意图 | 场景锚点 | ¥3,000/意图 | V1.1 新增，通意意图子集 |
| 品类意图 | 品类锚点 | ¥3,000/意图 | 通意意图子集 |
| 其他意图 | 其他锚点 | ¥3,000/意图 | 通意意图子集 |

5 词起步包 = 1 个最小意图单位 = 1 个 SKU。词量 6-10 词按 1.2-1.5x 加价，11+ 词硬阈值升档到进阶（2-3x）。

---

## 📋 版本

- **V1.0**（2026-06-29）MVP，4 stage 半自动
- **V1.1**（2026-06-29）加场景意图（通意意图子集）+ 按锚点分组（5 sheet）

---

## 🐛 已知限制（V1.1）

1. **MVP 半自动**：Stage 2/4 需用户手动跑 prompt（5 家 AI 平台 API 未对接）
2. **AI 平台固定**：写死 5 家，未来可扩展
3. **`reference/` 文档不上 git**：用户从本地 PARA 知识库手动同步

---

## 🤝 贡献

提交 issue / PR 到 GitHub 仓库。

## 📄 License

MIT

---

*作者：小赛博 · 拍板人：Frank · 归档：PARA/Projects/杂货铺项目/brand-intent-chooser/*
