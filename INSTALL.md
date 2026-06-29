# 安装指南（面向其他 Agent）

> 其他智能体如何拉取 saibo 仓库并安装 skill 到自己的 OpenClaw workspace
> 适用：所有运行 OpenClaw 平台的智能体

---

## 一、5 分钟快速安装

### 步骤 1：克隆 saibo 仓库

```bash
# SSH 协议（推荐，国内用 SSH 比 HTTPS 稳）
git clone git@github.com:cigfrank001-hash/saibo.git

# 或 HTTPS 协议（如已配置代理）
git clone https://github.com/cigfrank001-hash/saibo.git
```

### 步骤 2：安装某个 skill 到你的 OpenClaw workspace

**方法 A：直接复制（最简单）**
```bash
# 假设你的 OpenClaw workspace 在 ~/.openclaw/workspace/
cp -r saibo/skills/brand-intent-chooser ~/.openclaw/workspace/skills/
```

**方法 B：软链接（推荐，避免重复存储）**
```bash
ln -s $(pwd)/saibo/skills/brand-intent-chooser ~/.openclaw/workspace/skills/brand-intent-chooser
```

### 步骤 3：同步 reference 文档（可选）

`reference/` 文档不上 git（避免仓库过大），需要从你自己本地的 PARA 知识库手动同步：

```bash
# 假设你的 PARA 知识库在 ~/Desktop/.../PARA/
cp ~/Desktop/.../PARA/Areas/GEO/GEO知识沉淀.md \
   ~/.openclaw/workspace/skills/brand-intent-chooser/reference/
```

### 步骤 4：验证安装

```bash
# 1. 检查 skill 目录
ls ~/.openclaw/workspace/skills/brand-intent-chooser/

# 应该看到：
# - SKILL.md
# - scripts/  (5 个 Python 脚本)
# - templates/ (3 个模板)
# - .gitignore
# - README.md
# - LICENSE

# 2. 跑 Stage 1 测试
cd ~/.openclaw/workspace/skills/brand-intent-chooser/scripts
echo -e "新能源汽车\n高端纯电 SUV 和轿车\nC 端高端车主\n城市通勤+长途出行\n特斯拉/理想/小鹏/宝马/奔驰 EQ" | \
  python3 brand_diagnose.py --brand "蔚来" --industry "新能源汽车"

# 应该看到：
# - 🎯 Stage 1: 品牌诊断（5 问）输出
# - ✅ 品牌档案已保存：~/.openclaw/workspace/skills/brand-intent-chooser/output/品牌档案-蔚来-YYYYMMDD.json
```

---

## 二、完整 4 stage 流程

```bash
cd ~/.openclaw/workspace/skills/brand-intent-chooser/scripts

# Stage 1: 5 问诊断
python3 brand_diagnose.py --brand "你的品牌" --industry "你的行业"
# 输出: 品牌档案 JSON

# Stage 2: 意图发散（生成 20 个 prompt）
python3 intent_diverge.py --input ../output/品牌档案-你的品牌-YYYYMMDD.json
# 手动跑 5 家 AI 平台（DeepSeek/豆包/Kimi/文心/通义）收集结果

# Stage 2 collect: 合并 20 个结果
python3 intent_diverge.py --collect \
  --input ../output/品牌档案-你的品牌-YYYYMMDD.json \
  --results <results.json>
# 输出: 候选意图池 md

# Stage 3: 5 维度评估
python3 intent_filter.py --input ../output/候选意图池-你的品牌-YYYYMMDD.md
# 输出: 最小意图清单 xlsx

# Stage 4: 5 词选词（生成 prompt + collect 模式）
python3 keyword_pick.py --input ../output/最小意图清单-你的品牌-YYYYMMDD.xlsx
python3 keyword_pick.py --input ../output/最小意图清单-你的品牌-YYYYMMDD.xlsx \
  --collect --results <results.json>
# 输出: 5 词起步包 xlsx（5 sheet：品牌/场景/品类/其他/总计）
```

或用 `run_all.py` 串联（半自动，Stage 2/4 仍需手动跑 prompt）：
```bash
python3 run_all.py --brand "你的品牌" --industry "你的行业"
```

---

## 三、品牌标杆 demo（蔚来）

克隆后可以立即跑蔚来 demo 验证 skill 完整性：

```bash
cd ~/.openclaw/workspace/skills/brand-intent-chooser/scripts

# Stage 1
echo -e "新能源汽车\n高端纯电 SUV 和轿车\nC 端高端车主\n城市通勤+长途出行\n特斯拉/理想/小鹏/宝马/奔驰 EQ" | \
  python3 brand_diagnose.py --brand "蔚来" --industry "新能源汽车"

# Stage 2: 用提供的 V1.1 stage2 results
python3 intent_diverge.py --collect \
  --input ../output/品牌档案-蔚来-20260629.json \
  --results ../output/蔚来-stage2-results-v1.1.json
# 注：output/ 在 .gitignore 里，V1.1 results 文件需要从 Frank 索取

# Stage 3
python3 intent_filter.py --input ../output/候选意图池-蔚来-20260629.md

# Stage 4: 用提供的 V1.1 stage4 results
python3 keyword_pick.py --input ../output/最小意图清单-蔚来-20260629.xlsx \
  --collect --results ../output/蔚来-stage4-results-v1.1.json
```

预期结果：
- 86 最小意图（46 品牌 + 20 场景 + 9 品类 + 11 其他）
- 总报价 ¥189,000

---

## 四、与其他平台（非 OpenClaw）的集成

如果你的智能体平台不是 OpenClaw，可以参考以下集成方式：

### 方式 1：直接调用 Python 脚本

```python
import subprocess
result = subprocess.run(
    ['python3', '/path/to/saibo/skills/brand-intent-chooser/scripts/brand_diagnose.py',
     '--brand', '你的品牌', '--industry', '你的行业'],
    capture_output=True, text=True
)
print(result.stdout)
```

### 方式 2：作为 Python 模块导入

```python
import sys
sys.path.insert(0, '/path/to/saibo/skills/brand-intent-chooser/scripts')
from brand_diagnose import run_brand_diagnose
result = run_brand_diagnose(brand="你的品牌", industry="你的行业")
```

### 方式 3：HTTP API（V2.0 计划）

未来版本会提供 FastAPI 包装，支持 HTTP 调用。

---

## 五、常见问题

### Q1：克隆失败（HTTPS 443 阻断）

如果你在国内，HTTPS 协议可能被 GFW 阻断。用 SSH 协议：
```bash
git clone git@github.com:cigfrank001-hash/saibo.git
```
需要先配置 SSH key（参考 GitHub 文档）。

### Q2：Stage 2/4 需要手动跑 prompt？

是的，**MVP 半自动**。V1.0/V1.1 不接 5 家 AI 平台的 API，需要用户手动复制 prompt 跑 + 收集结果。V2.0 计划全自动化。

### Q3：`reference/` 文档不在仓库里？

`reference/` 不上 git（每个用户本地从 PARA 知识库手动同步）。如果你需要 GEO 知识沉淀文档，可以：
- 找 Frank 索取
- 或自己建立 GEO 知识库（参考 [docs/skill-spec.md](./docs/skill-spec.md)）

### Q4：跑 Python 脚本报错 `openpyxl` 缺失？

```bash
pip3 install openpyxl
```

### Q5：怎么知道 skill 是否被 OpenClaw 识别？

检查 `~/.openclaw/workspace/skills/` 目录下是否有对应目录。如果有软链接，OpenClaw 也能识别。

---

## 六、版本说明

| 版本 | 状态 | 关键变更 |
|------|------|----------|
| V1.1 | ✅ 稳定 | 场景意图（通意意图子集）+ 按锚点分组（5 sheet）|
| V1.0 | ✅ 稳定 | MVP 4 stage 半自动 |

---

## 七、贡献新 skill

想为 saibo 仓库贡献新 skill？

详见 [CONTRIBUTING.md](./CONTRIBUTING.md)：
1. Fork 仓库
2. 在 `skills/<your-skill>/` 下创建新 skill
3. 写 SKILL.md + README.md + 脚本 + 模板
4. 跑标杆 demo 验证
5. 提交 PR

---

## 八、License

[MIT](./LICENSE) — 任何人都可以自由使用、修改、分发。

---

## 九、联系

- 维护者：Frank（`cigfrank001@...`）+ 小赛博 (CyberHelper)
- 飞书群：小赛博-数字助理群
- 仓库：https://github.com/cigfrank001-hash/saibo

---

*最后更新：2026-06-29*
