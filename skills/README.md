# skills/ · Skills 目录

> 这里是所有可立即复用的 Agent 技能包

---

## 📦 当前 Skills

| Skill | 版本 | 简介 | 文档 |
|-------|------|------|------|
| **[brand-intent-chooser](./brand-intent-chooser/)** | V1.1 | GEO 品牌意图选词助手 | [README](./brand-intent-chooser/README.md) · [SKILL.md](./brand-intent-chooser/SKILL.md) |

---

## 🚀 如何安装一个 skill 到 OpenClaw

```bash
# 1. 克隆整个 saibo 仓库
git clone git@github.com:cigfrank001-hash/saibo.git

# 2. 复制某个 skill 到你的 OpenClaw workspace
cp -r saibo/skills/<skill-name> ~/.openclaw/workspace/skills/

# 3. 直接用
cd ~/.openclaw/workspace/skills/<skill-name>/scripts
python3 <main-script>.py
```

或用一个完整路径（推荐）：
```bash
ln -s $(pwd)/saibo/skills/<skill-name> ~/.openclaw/workspace/skills/<skill-name>
```

---

## 🛠 如何添加新 skill

### 步骤 1：创建子目录

```bash
mkdir -p skills/<new-skill-name>/{scripts,templates,reference,output}
```

### 步骤 2：写 SKILL.md（YAML frontmatter + 章节）

参考 [skill-spec.md](../docs/skill-spec.md) 的 SKILL.md 规范。

### 步骤 3：写 Python 脚本

参考 [skill-spec.md](../docs/skill-spec.md) 的 Python 脚本规范。

### 步骤 4：写 README.md（人类阅读版）

### 步骤 5：跑标杆 demo

### 步骤 6：Frank 拍板 + git push

---

## 📋 Skill 清单（计划中）

- [x] brand-intent-chooser（V1.1）
- [ ] news-digest（每日新闻摘要）
- [ ] link-capture（网页内容捕获）
- [ ] weather-qweather（天气播报）
- [ ] competitor-monitor（竞品监控）

---

*最后更新：2026-06-29*
