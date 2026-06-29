# OpenClaw Skill 规范

> 如何写一个符合 OpenClaw 规范的 skill
> 适用：所有要在 OpenClaw 平台运行的 skill

---

## 一、目录结构

每个 skill 是一个**独立子目录**，放在 `~/.openclaw/workspace/skills/<skill-name>/`：

```
<skill-name>/
├── SKILL.md              # 必须：主入口
├── scripts/              # 必须：Python 脚本
├── templates/            # 可选：模板文件
├── reference/            # 可选：引用文档（用户本地同步，不上 git）
├── output/               # 可选：产出物（每个用户本地生成）
├── examples/             # 可选：示例数据
└── README.md             # 推荐：人类阅读版
```

---

## 二、SKILL.md 规范

### 2.1 YAML frontmatter（必须）

```yaml
---
name: skill-name
description: 一句话说明 skill 用途 + 触发条件
---
```

**示例**：
```yaml
---
name: brand-intent-chooser
description: 品牌意图选词助手。输入品牌+行业+产品，按 4 阶段流程输出 N 个最小意图单元（每个 = 1 角色+1 场景+1 阶段+5 词），对接迪光 GEO 报价表 V1.1。用于"按品牌出最小意图清单"或"为新 GEO 客户准备 5 词起步包"。
---
```

### 2.2 正文结构（推荐）

```markdown
# Skill 名称

**功能**：...
**作者**：...
**版本**：...
**规划位置**：...

---

## 🎯 一句话定位

> 一句话说明做什么

---

## 🔄 流程

```
阶段 1 - ...
阶段 2 - ...
```

---

## 🚀 使用方式

### 全流程跑
```bash
python3 scripts/run_all.py
```

### 单阶段跑
```bash
python3 scripts/stage_1.py
```

### 触发关键词
- 用户说"XX" → 调 skill
- 飞书群 @ 触发

---

## 📁 文件结构
...

---

## 📦 产出物清单
...

---

## 🔗 跟现有体系的关系
...

---

## 🛠 MVP 实现说明
...

---

## ✅ 验收标准
...

---

## 🐛 已知限制
...

---

## 📈 未来迭代
...

---

## 📚 关联资源
...

---

*最后更新：YYYY-MM-DD*
*作者：小赛博*
*拍板人：Frank*
```

---

## 三、Python 脚本规范

### 3.1 文件头注释

```python
#!/usr/bin/env python3
"""
script_name.py - 阶段 N: ...

输入：...
输出：...
"""
```

### 3.2 命令行参数

```python
import argparse

def main():
    parser = argparse.ArgumentParser(description="阶段 N: 描述")
    parser.add_argument("--input", required=True, help="输入文件")
    parser.add_argument("--output", help="输出文件")
    args = parser.parse_args()
    # ...

if __name__ == "__main__":
    main()
```

### 3.3 路径处理

- 用 `Path(__file__).parent` 算相对路径
- 输出文件用日期/品牌命名：`5词起步包-{品牌}-{日期}.xlsx`
- 不写死绝对路径

### 3.4 错误处理

- 显式错误信息（带 emoji 标记）
- 不静默失败

```python
print("❌ 找不到品牌档案，请先跑 Stage 1")
sys.exit(1)
```

### 3.5 输出格式

- 表格用 Markdown 表格
- 关键数字加粗
- 用 emoji 标记状态

---

## 四、reference 规范

`reference/` 放引用文档，**不上 git**（每个用户从本地 PARA 知识库手动同步）。

**同步方式**：
```bash
# 用户从 PARA 知识库复制
cp ~/Desktop/.../PARA/Areas/GEO/GEO知识沉淀.md \
   ~/.openclaw/workspace/skills/<skill>/reference/
```

**reference 文档应该是**：
- 完整的知识沉淀（不是片段）
- 用户可独立阅读理解
- 与 SKILL.md 互补（不重复）

---

## 五、output 规范

`output/` 放每个用户本地生成的产出物，**必须 .gitignore**。

**文件命名**：
- Stage 1：`{类型}-{对象}-{日期}.{ext}`（如 `品牌档案-蔚来-20260629.json`）
- Stage 2：`{类型}-{对象}-{日期}.{ext}`（如 `候选意图池-蔚来-20260629.md`）
- Stage 3：`{类型}-{对象}-{日期}.{ext}`（如 `最小意图清单-蔚来-20260629.xlsx`）
- Stage 4：`{类型}-{对象}-{日期}.{ext}`（如 `5词起步包-蔚来-20260629.xlsx`）

**Stage 中间结果**（如 prompt 池、模拟数据）用 `-stage{N}-results.json` 后缀。

---

## 六、版本管理

### 6.1 版本号

- 主版本.次版本.修订号（SemVer）
- V1.0 第一个稳定版
- 重大变更 → 主版本 +1
- 新增功能（向后兼容）→ 次版本 +1
- Bug 修复 → 修订号 +1

### 6.2 版本变更记录

每个版本变更必须：
1. 更新 SKILL.md 的"版本"字段
2. 沉淀到 PARA/Projects/<对应项目>/进度日志
3. 飞书群通知 Frank

---

## 七、测试与验收

每个 skill 应该有：
- [ ] 标杆 demo 跑通（如 brand-intent-chooser 的蔚来 demo）
- [ ] 单元测试（可选，V2.0 引入）
- [ ] 端到端测试（4 stage 串联）
- [ ] 真实数据验证（不是模拟数据）

---

## 八、提交规范

### 8.1 Commit message

格式：`<type>(<scope>): <subject>`

**type**：
- `feat` - 新功能
- `fix` - 修复 bug
- `docs` - 文档变更
- `refactor` - 重构
- `test` - 测试
- `chore` - 杂项

**示例**：
```
feat(skills): add brand-intent-chooser V1.1
fix(intent_filter): correct row index for anchor column
docs(readme): update skill installation guide
```

### 8.2 分支策略

- `main` - 主分支（稳定）
- `develop` - 开发分支
- `feature/xxx` - 功能分支
- `hotfix/xxx` - 紧急修复

---

## 九、安全审查

提交新 skill 前：

1. 检查代码无硬编码密钥
2. 检查无破坏性操作
3. 用 `skill-vetter` 跑安全审查
4. Frank 拍板后才 push

---

## 十、结语

> **好的 skill 是跑出来的，不是写出来的。**
> **V1.0 先跑通，V2.0 再优雅。**

---

*最后更新：2026-06-29*
*作者：小赛博*
