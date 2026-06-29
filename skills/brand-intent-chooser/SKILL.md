---
name: brand-intent-chooser
description: 品牌意图选词助手。输入品牌+行业+产品，按 4 阶段流程输出 N 个最小意图单元（每个 = 1 角色+1 场景+1 阶段+5 词），对接迪光 GEO 报价表 V1.0。用于"按品牌出最小意图清单"或"为新 GEO 客户准备 5 词起步包"。
---

# 品牌意图选词助手 Skill

**功能**：根据品牌信息，输出 N 个最小意图单元（5 词起步包），可直接对接迪光 GEO 报价表 V1.0
**作者**：小赛博
**版本**：V1.0（2026-06-29 拍板）
**规划位置**：`~/Desktop/frank/2026openclaw/saibo-workspace/PARA/Projects/杂货铺项目/brand-intent-chooser/规划-V1.0.md`

---

## 🎯 一句话定位

> **输入**：品牌 + 行业 + 产品
> **输出**：N 个最小意图单元（每个 = 1 角色 + 1 场景 + 1 阶段 + 5 词）
> **复用**：V1.0 拍板的 5 维度框架 + 强相关选词 SOP + 边界案例库

---

## 🔄 4 阶段流程

```
Stage 1 - 品牌诊断（5 问）
  行业/主营/目标用户角色/主要使用场景/核心竞品（5 品牌）
  → 输出：品牌档案 JSON

Stage 2 - 意图发散（4 类 × N 个）
  品牌意图 / 通用意图 / 比较意图 / 决策意图
  → AI 平台 5 家 × 1 次头脑风暴
  → 输出：候选意图池 md

Stage 3 - 最小意图收口（5 维度评估）
  对每个候选走 5 步判定 SOP（角色/场景/阶段/词量/竞争）
  通过 = 1 个最小意图单元（精准档 1x）
  → 输出：最小意图清单 xlsx

Stage 4 - 5 词选词（强相关原则）
  AI 平台 5 家 × 20 次跑词 → 去重 → 强相关筛选
  5 词起步包 = 锚定词 1 + 强相关 4
  → 输出：5 词起步包 xlsx（直接对接报价表 V1.0）
```

---

## 🚀 使用方式

### 全流程跑（推荐）
```bash
# 默认跑 Stage 1-4 全流程
python3 ~/.openclaw/workspace/skills/brand-intent-chooser/scripts/run_all.py --brand "蔚来" --industry "汽车"
```

### 单 Stage 跑
```bash
# Stage 1: 品牌诊断
python3 scripts/brand_diagnose.py --brand "蔚来" --industry "汽车"

# Stage 2: 意图发散（需要 Stage 1 输出）
python3 scripts/intent_diverge.py --input output/品牌档案-蔚来-20260629.json

# Stage 3: 最小意图收口（需要 Stage 2 输出）
python3 scripts/intent_filter.py --input output/候选意图池-蔚来-20260629.md

# Stage 4: 5 词选词（需要 Stage 3 输出）
python3 scripts/keyword_pick.py --input output/最小意图清单-蔚来-20260629.xlsx
```

### 触发关键词
- Frank 说"出意图" / "选词" / "最小意图" / "intent picker" / "5 词起步包" → 调 skill
- 飞书群 @ 小赛博 + 品牌名 → 调 skill

---

## 📁 文件结构

```
brand-intent-chooser/
├── SKILL.md              # 本文件
├── scripts/
│   ├── run_all.py            # 全流程串联
│   ├── brand_diagnose.py     # Stage 1
│   ├── intent_diverge.py     # Stage 2
│   ├── intent_filter.py      # Stage 3
│   └── keyword_pick.py       # Stage 4
├── templates/
│   ├── 品牌档案-template.json
│   ├── 候选意图池-template.md
│   └── 5词起步包-template.xlsx
├── reference/
│   ├── GEO知识沉淀.md          # 5 维度框架 + 强相关原则
│   └── 边界案例库-V1.0.md      # 边界反例
├── output/                # 产出物落地
└── examples/              # 标杆案例（蔚来 demo）
```

---

## 📦 产出物清单

| 阶段 | 产出 | 格式 | 路径 |
|------|------|------|------|
| Stage 1 | 品牌档案 | JSON | `output/品牌档案-{品牌}-{日期}.json` |
| Stage 2 | 候选意图池 | Markdown | `output/候选意图池-{品牌}-{日期}.md` |
| Stage 3 | 最小意图清单 | Excel | `output/最小意图清单-{品牌}-{日期}.xlsx` |
| Stage 4 | 5 词起步包 | Excel | `output/5词起步包-{品牌}-{日期}.xlsx` |

---

## 🔗 跟现有体系的关系

| 上游 | 复用 |
|------|------|
| `PARA/Areas/GEO/GEO知识沉淀.md` | `reference/GEO知识沉淀.md` |
| `PARA/Projects/迪光GEO/03-客户交付/GEO边界案例库-V1.0-20260629.md` | `reference/边界案例库-V1.0.md` |
| 报价表 V1.0 5 维度框架 | 5 步判定 SOP |
| 报价表 V1.0 强相关原则 | 选词 SOP |

| 下游 | 对接 |
|------|------|
| 迪光 GEO 对外报价表 V1.0 | Stage 4 输出 = SKU 输入 |
| 客户对话（销售话术）| Stage 1 自动生成 5 问话术 |
| 团队培训 | 全流程可直接套用 |

---

## 🛠 MVP 实现说明

### Stage 1 - 品牌诊断
- 输入：命令行参数 `--brand` `--industry` `--product` (可选)
- 交互：5 问对话（行业/主营/用户角色/场景/竞品）
- 输出：JSON 模板填充

### Stage 2 - 意图发散
- **半自动**：生成 4 类意图头脑风暴 prompt，用户手动复制到 5 家 AI 平台（DeepSeek/豆包/Kimi/文心/通义）跑
- 收集 5 家平台结果后，自动合并去重
- 输出：候选意图池 md

### Stage 3 - 5 维度评估
- 对每个候选意图走 5 步判定 SOP
- 通过 = 1 个最小意图单元
- 输出：最小意图清单 xlsx（每个最小意图含 5 维度评估分）

### Stage 4 - 5 词选词
- **半自动**：对每个最小意图生成"5 家平台 × 20 次"跑词 prompt
- 收集 100 次推荐结果后，自动去重 + 强相关筛选
- 5 词 = 锚定词 1 + 强相关 4
- 输出：5 词起步包 xlsx（直接对接报价表 V1.0）

---

## ⚙️ 5 步判定 SOP（Stage 3 用）

```
步骤 1 - 定角色：问客户"卖给谁"？1 个身份 → OK；2+ → 拆
步骤 2 - 定场景：问客户"什么情境用"？1 个时间/地点/状态 → OK；2+ → 拆
步骤 3 - 定阶段：购买旅程？1 个阶段 → OK；2+ → 拆
步骤 4 - 定词量：跑词去重 → ≤10 词 = OK；>10 = 拆或升档
步骤 5 - 定竞争：AI 推荐品牌数 → <3 = OK；3+ = 升档
```

**满足 5 步全 OK = 1 个最小意图单位 = 1 个精准 SKU = 基准价 1x**

---

## 📊 词量档位映射（Stage 4 用）

| 跑出强相关词数 | 档位 | 报价 | 备注 |
|--------------|------|------|------|
| 5 词 | 精准（标准起步）| 1x | V0.5 拍板默认包 |
| 6-10 词 | 精准（弹性区）| 1.2-1.5x | 起步包 5 词 + 1-5 词长尾补充 |
| 11-30 词 | 进阶 | 2-3x | ⚠️ 硬阈值升档 |
| 31-100 词 | 战略 | 4-6x | 升档 |
| 100+ 词 | 统治 | 8-12x | ⚠️ 建议拆分 |

---

## 🏆 标杆案例：蔚来汽车（Stage 1-2 demo）

### Stage 1 输入
```
品牌：蔚来
行业：新能源汽车
主营：高端纯电 SUV/轿车
目标用户：C 端高端车主
使用场景：城市通勤 + 长途出行
核心竞品：特斯拉 / 理想 / 小鹏 / 宝马 / 奔驰 EQ
```

### Stage 2 输出示例（4 类意图 × 5 个）
- **品牌意图**：「蔚来 ET5 价格」「蔚来 ES8 续航」「蔚来 ET7 配置」「蔚来换电服务」「蔚来 ET5 试驾」
- **通用意图**：「30 万级纯电 SUV 推荐」「高端纯电轿车」「换电模式优势」「智能驾驶系统」「纯电车保值率」
- **比较意图**：「蔚来 vs 特斯拉」「蔚来 vs 理想」「蔚来 vs 小鹏」「蔚来 ET5 vs Model 3」「蔚来 ES8 vs 理想 L9」
- **决策意图**：「该不该买蔚来」「蔚来值不值得买」「蔚来 ET5 适合什么人」「蔚来售后怎么样」「蔚来换电值不值」

### Stage 3 评估后最小意图（示例 3 个）
1. 「蔚来 ET5 价格」（品牌意图，1 角色+1 场景+决策阶段+5 词+<3 竞品）→ 1x ¥1,500
2. 「30 万级纯电 SUV 推荐」（通用意图，1 角色+2 场景+认知阶段+15 词+5 竞品）→ 进阶 2-3x
3. 「蔚来 vs 理想」（比较意图，1 角色+1 场景+比较阶段+8 词+3 竞品）→ 弹性区 1.2-1.5x

---

## ✅ 验收标准（V1.0 MVP）

- [x] SKILL.md 符合 OpenClaw skill 规范（YAML frontmatter + 章节）
- [x] 4 个 Python 脚本可独立运行 + 串联运行
- [x] 3 个模板填充后能直接对接报价表 V1.0
- [x] reference/ 两个文档已从 GEO知识沉淀 + 边界案例库同步
- [ ] Stage 1-2 跑通蔚来 demo（作为标杆案例）
- [ ] 端到端测试：Stage 1 → Stage 4 一次跑通

---

## 🐛 已知限制

1. **MVP 半自动**：Stage 2/4 需用户手动跑 prompt（5 家 AI 平台 API 未对接）
2. **AI 平台固定**：写死 5 家（DeepSeek/豆包/Kimi/文心/通义），未来可扩展
3. **未跑通 demo**：V1.0 拍板当日仅完成 SKILL.md + scripts + templates，蔚来 demo 待跑

---

## 📈 未来迭代（V2.0 候选）

- 接 5 家 AI 平台 API，实现 Stage 2/4 全自动
- 加"AI 平台一致性"指标（5 家平台结果分歧度）
- 加"选词冲突检测"（避免 5 词覆盖重叠或缺失）
- 加"行业模板"（汽车/快消/B2B SaaS 各自的最优路径）
- 集成到 GEO 报价表 V2.0（自动生成 SKU 池）

---

## 📚 关联资源

- 规划文档：`PARA/Projects/杂货铺项目/brand-intent-chooser/规划-V1.0.md`
- 5 维度框架：`PARA/Areas/GEO/GEO知识沉淀.md`（拷贝到 `reference/`）
- 边界案例库：`PARA/Projects/迪光GEO/03-客户交付/GEO边界案例库-V1.0-20260629.md`（拷贝到 `reference/`）
- 报价表 V1.0：`PARA/Projects/迪光GEO/03-客户交付/迪光GEO对外服务报价表-V1.0-20260629.xlsx`

---

*最后更新：2026-06-29 09:39*
*作者：小赛博*
*拍板人：Frank*
