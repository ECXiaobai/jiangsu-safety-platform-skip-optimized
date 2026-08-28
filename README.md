# 江苏省安全教育平台一键完成脚本（2026 优化版）

"2026江苏省大学新生安全知识教育" 一键完成脚本（重构优化版）。

> 本项目是基于 [Scwizard/jiangsu-safety-platform-skip](https://github.com/Scwizard/jiangsu-safety-platform-skip)
> （Apache License 2.0）重构优化的衍生版本，原作者为南京晓庄学院 Scwizard，感谢原作者的分享。

## 功能

- **登录版**（`main_login.py`）：输入学校名称、账号、密码即可，支持：
  - 关键词自动匹配学校（唯一匹配直接选中，多个匹配可交互选择）；
  - 完成后自动解绑 openId 并退出登录。

## 与原版的区别（优化点）

- 代码模块化重构：`config.py`（配置与题库）、`utils.py`（平台交互）与入口脚本分离；
- 题库查询改用 SQL 参数化查询，避免 SQL 注入；
- 统一使用 `requests.Session`，集中管理超时与请求头；
- 适配 2026 年平台接口与题库；
- 不再向原作者服务器上报任何统计信息。

## 使用方法

1. 安装 Python 3，并安装依赖：`pip install -r requirements.txt`（仅需 `requests`）；
2. 运行 `python main_login.py`；
3. 按程序提示输入即可，运行完成后可在平台主页"结课"中查询证书。

## 免责声明

- 本脚本仅供学习交流使用，**禁止用于盈利**；
- 使用本脚本可能违反学校或平台的相关规定，请自行评估风险，后果自负；
- 脚本使用过程中产生的账号风险与作者无关。

## License

[Apache License 2.0](LICENSE)
