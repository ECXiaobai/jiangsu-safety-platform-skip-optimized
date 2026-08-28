# 江苏省安全教育平台一键完成脚本（2026 增强版）

"2026江苏省大学新生安全知识教育" 一键完成脚本。

> 本项目基于 [Scwizard/jiangsu-safety-platform-skip](https://github.com/Scwizard/jiangsu-safety-platform-skip)
> （Apache License 2.0）衍生优化，并融合了社区提交的必修课修复方案，感谢原作者与贡献者。

## 功能

- **登录版**（`main.py`）：输入学校名称、账号、密码即可，支持：
  - 关键词自动匹配学校（唯一匹配直接选中，多个匹配可交互选择）；
  - 自动完成必修课程（courseType=1）与专题课程（courseType=2）；
  - 完成后自动进入考试并提交答案；
  - 完成后静默解绑 openId 并退出登录。

## 适配 2026 平台改动

- 平台 2026-08-28 新增 Cookie 认证，需登录取得 Cookie（已移除 userid 版本）；
- 考试资格判定要求**必修课程（courseType=1）全部完成**，本脚本通过
  `compulsory/list`（courseType=1）遍历 14 门必修课、约 119 篇文章完成学习；
- 平台新增 `markArticleViewed` 观看校验，每篇文章作答前先标记已观看；
- 考试题库已更新（题目 id 以 2079 开头），`database.db` 已同步重建。

## 主要文件

| 文件 | 说明 |
|---|---|
| `main.py` | 主脚本（登录版） |
| `database.db` | 考试题库（2026 新版） |
| `course_answers.json` | 必修课答案缓存（1178 条，自动收割累积） |
| `utils.py` | 平台接口封装 |

## 使用方法

1. 安装 Python 3 与依赖：`pip install -r requirements.txt`（仅需 `requests`）；
2. 运行 `python main.py`；
3. 按程序提示输入学校、账号、密码即可。

## 打包成 exe

```bash
pip install pyinstaller
pyinstaller --clean --noconfirm 安全知识教育一键完成_登录版.spec
```

## 免责声明

- 本脚本仅供学习交流使用，**禁止用于盈利**；
- 使用本脚本可能违反学校或平台的相关规定，请自行评估风险，后果自负；
- 脚本使用过程中产生的账号风险与作者无关。

## License

[Apache License 2.0](LICENSE)
