# 贡献指南

> 欢迎为 saibo 贡献新 skill / docs / snippets / examples
> 适用：所有想为仓库添砖加瓦的贡献者

---

## 一、贡献类型

| 类型 | 说明 | 适合谁 |
|------|------|--------|
| **新 skill** | 添加新的 Agent 技能包 | 有具体自动化需求的开发者 |
| **docs** | 改进文档 | 写作者 |
| **snippets** | 添加常用代码片段 | 重度编码者 |
| **examples** | 完整示例项目 | 想展示用法的人 |
| **bug fix** | 修复现有 skill 的 bug | 所有贡献者 |

---

## 二、贡献流程

### 步骤 1：Fork 仓库

在 https://github.com/cigfrank001-hash/saibo 页面点 **「Fork」**。

### 步骤 2：克隆你的 Fork

```bash
git clone git@github.com:<你的用户名>/saibo.git
cd saibo
```

### 步骤 3：创建分支

```bash
# 新 skill
git checkout -b feature/<skill-name>

# 修 bug
git checkout -b fix/<short-description>

# 改文档
git checkout -b docs/<short-description>
```

### 步骤 4：实施

按以下规范实施：
- **Skill 规范**：[docs/skill-spec.md](./docs/skill-spec.md)
- **设计哲学**：[docs/philosophy.md](./docs/philosophy.md)

### 步骤 5：本地测试

```bash
# 跑标杆 demo
cd skills/<your-skill>/scripts
python3 brand_diagnose.py --brand "测试品牌" --industry "测试行业"

# 验证所有 stage 跑通
python3 run_all.py --brand "测试品牌" --industry "测试行业"
```

### 步骤 6：Commit

```bash
git add .
git commit -m "feat(skills): add <skill-name> V1.0

- Stage 1: ...
- Stage 2: ...
- Stage 3: ...
- Stage 4: ...

标杆 demo：<品牌> 端到端跑通
文档：README.md + SKILL.md
"
```

### 步骤 7：Push

```bash
git push origin feature/<skill-name>
```

### 步骤 8：创建 Pull Request

1. 打开 https://github.com/cigfrank001-hash/saibo
2. 点 **「Compare & pull request」**
3. 填写 PR 标题和说明：
   - 标题：`feat(skills): add <skill-name>`
   - 说明：变更内容 + 测试结果 + 关联 issue
4. 点 **「Create pull request」**

---

## 三、Code Review 标准

PR 必须满足：

- [ ] 跑通标杆 demo
- [ ] 有 SKILL.md（含 YAML frontmatter）
- [ ] 有 README.md（人类阅读版）
- [ ] 注释和 docstring 完整
- [ ] 错误处理（不静默失败）
- [ ] 提交信息遵循规范

---

## 四、Commit 规范

格式：`<type>(<scope>): <subject>`

**type**：
- `feat` - 新功能
- `fix` - 修复 bug
- `docs` - 文档变更
- `refactor` - 重构
- `test` - 测试
- `chore` - 杂项

**scope**：
- `skills` - skills 目录
- `docs` - docs 目录
- `snippets` - snippets 目录
- `examples` - examples 目录
- `repo` - 仓库级（README/LICENSE/.gitignore）

**示例**：
```
feat(skills): add brand-intent-chooser V1.1
fix(intent_filter): correct row index for anchor column
docs(philosophy): add action-oriented principle
```

---

## 五、版本管理

- 每次重大变更 → 主版本 +1
- 每次向后兼容功能 → 次版本 +1
- 每次 bug 修复 → 修订号 +1
- 在 SKILL.md 顶部更新版本号 + 增量更新内容

---

## 六、问题反馈

- **Bug** → GitHub Issues
- **功能建议** → GitHub Discussions
- **安全漏洞** → 私下联系 Frank（不开 issue）

---

## 七、License

贡献的代码默认采用 [MIT License](./LICENSE)。

---

*最后更新：2026-06-29*
