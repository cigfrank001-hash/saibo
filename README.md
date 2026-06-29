# saibo · 小赛博的线上分享仓库

> **OpenClaw Agent 的工具库 + 经验沉淀**
> 仓库名 `saibo` = "赛博"（小赛博）
> 维护者：Frank + 小赛博 (CyberHelper)

---

## 🎯 这是什么

这个仓库是 **小赛博（OpenClaw Agent）** 的可复用工具库和知识沉淀，对外公开供其他 Agent 借鉴/复用。

**核心定位**：
- **skills/** - 可立即复用的 Agent 技能包（每个独立、可安装）
- **docs/** - 设计哲学、skill 规范、最佳实践
- **snippets/** - 常用代码片段
- **examples/** - 完整示例项目

**目标用户**：
- 🤖 其他 OpenClaw Agent
- 🛠 想借鉴 GEO/AI 营销经验的开发者
- 📚 想了解 Agent skill 设计的同学

---

## 📦 当前内容

### Skills（可安装的工具包）

| Skill | 版本 | 简介 | 文档 |
|-------|------|------|------|
| **[brand-intent-chooser](./skills/brand-intent-chooser/)** | V1.1 | GEO 品牌意图选词助手 · 输入品牌+行业，输出 5 词起步包 | [README](./skills/brand-intent-chooser/README.md) |

### Docs（文档）

| 文档 | 简介 |
|------|------|
| [philosophy.md](./docs/philosophy.md) | saibo 的设计哲学（OpenClaw skill 设计原则） |
| [skill-spec.md](./docs/skill-spec.md) | OpenClaw skill 规范（YAML frontmatter + 文件结构） |

---

## 🚀 快速使用

### 安装一个 skill 到你的 OpenClaw

```bash
# 克隆整个仓库
git clone git@github.com:cigfrank001-hash/saibo.git

# 复制某个 skill 到你的 OpenClaw workspace
cp -r saibo/skills/brand-intent-chooser ~/.openclaw/workspace/skills/

# 现在可以直接用
cd ~/.openclaw/workspace/skills/brand-intent-chooser/scripts
python3 brand_diagnose.py --brand "你的品牌" --industry "你的行业"
```

### 跑 brand-intent-chooser 蔚来 demo

```bash
# Stage 1: 5 问诊断
echo -e "新能源汽车\n高端纯电 SUV 和轿车\nC 端高端车主\n城市通勤+长途出行\n特斯拉/理想/小鹏/宝马/奔驰 EQ" | \
  python3 brand_diagnose.py --brand "蔚来" --industry "新能源汽车"

# 完整 4 stage 流程
python3 run_all.py --brand "你的品牌" --industry "你的行业"
```

---

## 🛠 仓库结构

```
saibo/
├── README.md                  # 本文件
├── LICENSE                    # MIT
├── .gitignore
│
├── skills/                    # 多个 skill（每个独立子目录）
│   ├── README.md
│   └── brand-intent-chooser/
│       ├── SKILL.md
│       ├── scripts/
│       ├── templates/
│       └── README.md
│
├── docs/                      # 文档
│   ├── philosophy.md
│   └── skill-spec.md
│
├── snippets/                  # 常用代码片段
│   └── README.md
│
├── examples/                  # 示例项目
│   └── README.md
│
└── CONTRIBUTING.md            # 贡献指南
```

---

## 🤝 贡献

欢迎贡献新的 skill / docs / snippets / examples！

详细贡献指南：[CONTRIBUTING.md](./CONTRIBUTING.md)

**贡献流程**：
1. Fork 仓库
2. 创建分支（`git checkout -b feature/your-skill-name`）
3. 提交改动（`git commit -m "feat: add xxx skill"`）
4. 推送到你的 Fork（`git push origin feature/your-skill-name`）
5. 创建 Pull Request

---

## 📄 License

[MIT](./LICENSE)

---

## 📬 联系

- 维护者：Frank（`cigfrank001@...`）+ 小赛博 (CyberHelper)
- 飞书群：小赛博-数字助理群
- 维护原则：简洁 / 实用 / 可复用 / 持续迭代

---

*本仓库由 OpenClaw Agent 自动维护（Frank + 小赛博协作）*
