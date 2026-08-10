# 参与贡献

欢迎任何形式的贡献：bug 报告、功能建议、猫设 prompt 调教、代码 PR。

## 提 Issue

- Bug：请附上复现步骤、日志片段（**隐去 Token / Secret 等凭据**）、Python 版本
- 功能建议：先说清使用场景，再谈方案

## 提 PR

1. Fork 并新建分支：`git checkout -b feat/your-feature`
2. 改动代码请同步补充/更新 `tests/` 下的测试
3. 提交前确保 `python -m pytest tests -q` 全部通过
4. Commit message 用 `feat: / fix: / docs: / test:` 前缀
5. PR 描述里说明「做了什么、为什么、怎么验证的」

## 调教猫设

只改 `prompts/cat.md` 的 PR 也欢迎——请在 PR 里贴 2–3 段实际对话效果对比。
