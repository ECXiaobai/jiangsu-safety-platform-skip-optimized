"""
工具函数模块 - 平台交互、数据库查询、统计上传
"""
import json
import os
import sqlite3
import sys
import warnings
from typing import Any

import requests

import config

# 抑制 SSL 警告（verify=False 时）
warnings.filterwarnings("ignore", category=requests.packages.urllib3.exceptions.InsecureRequestWarning)

# ---------- 通用 ----------

def end(code: int = 0) -> None:
    """暂停并退出程序"""
    input("按回车键退出...")
    sys.exit(code)


def _log_response(resp: requests.Response, *args, **kwargs) -> requests.Response:
    """调试日志：打印每次请求的 URL、参数与响应（截断，避免刷屏）"""
    req = resp.request
    print(f"\n[REQ] {req.method} {req.url}")
    body = req.body or ""
    if body:
        cut = len(body) > config.MAX_LOG_BODY
        print(f"[BODY] {body[:config.MAX_LOG_BODY]}{'...[截断]' if cut else ''}")
    text = resp.text or ""
    cut = len(text) > config.MAX_LOG_RESP
    print(f"[RES] {resp.status_code} {text[:config.MAX_LOG_RESP]}{'...[截断]' if cut else ''}")
    return resp


# 全局共享的 Session：所有请求复用同一批 cookie，保证登录后 SESSION 能带到后续接口
_SHARED_SESSION: "requests.Session | None" = None


def _session() -> requests.Session:
    """返回全局共享的 Session（首次创建时配置超时、代理、日志）"""
    global _SHARED_SESSION
    if _SHARED_SESSION is None:
        sess = requests.Session()
        sess.verify = False
        sess.timeout = config.REQUEST_TIMEOUT
        if config.PROXY:
            sess.proxies = {"http": config.PROXY, "https": config.PROXY}
        if config.PRINT_LOG:
            sess.hooks["response"] = [_log_response]
        _SHARED_SESSION = sess
    return _SHARED_SESSION


# ---------- 学校查询 ----------

def get_all_schools(province: str = "江苏省") -> list[dict[str, Any]]:
    """获取指定省份的学校列表"""
    resp = _session().get(
        f"{config.BASE_URL}/select/proCollege",
        params={"provincesName": province},
        timeout=config.REQUEST_TIMEOUT,
    )
    return resp.json()["data"]


def get_user_school() -> str:
    """
    交互式获取用户所在学校的 collegeId。
    用户输入关键词，匹配到唯一学校时直接返回；多个学校时让用户选择。
    """
    school_list = get_all_schools("江苏省")

    while True:
        keyword = input("请输入学校名称[关键词也可以]：").strip()
        if not keyword:
            print("输入不能为空，请重新输入")
            continue

        candidates = [s for s in school_list if keyword in s["name"]]
        if not candidates:
            print("未查找到任何学校，请重新输入")
            continue

        if len(candidates) == 1:
            school_id = candidates[0]["id"]
            print(f"已获取学校id：{school_id}")
            return school_id

        # 多个匹配，让用户选择
        print("查找到以下学校：")
        for i, s in enumerate(candidates):
            print(f"[{i}] {s['name']}")

        while True:
            try:
                n = int(input("请输入数字序号来选择学校："))
                if 0 <= n < len(candidates):
                    school_id = candidates[n]["id"]
                    print(f"已获取学校id：{school_id}")
                    return school_id
                print(f"序号超出范围 (0-{len(candidates) - 1})，请重新输入")
            except ValueError:
                print("输入有误，请输入数字")


# ---------- 登录 / 解绑 ----------

def login_method(username: str, password: str, college_id: str) -> dict[str, Any]:
    """
    登录函数
    返回示例见原版注释
    """
    headers = {
        "Accept": "application/json, text/javascript, */*; q=0.01",
        "Accept-Language": "zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7",
        "Connection": "keep-alive",
        "Content-Type": "application/x-www-form-urlencoded;charset=UTF-8",
        "Origin": "http://wap.xiaoyuananquantong.com",
        "Referer": "http://wap.xiaoyuananquantong.com/guns-vip-main/wap/jiangsuwxJsback",
        "User-Agent": (
            "Mozilla/5.0 (Linux; Android 16; MEIZU 20 Pro Build/BQ2A.251110.001-"
            "BP2A.250605.031.A3; wv) AppleWebKit/537.36 (KHTML, like Gecko) "
            "Version/4.0 Chrome/146.0.7680.178 Mobile Safari/537.36 XWEB/1460249 "
            "MMWEBSDK/20260202 MMWEBID/3950 REV/6666666666666666666666666666666666666666 "
            "MicroMessenger/8.0.71.3080(0x28004750) WeChat/arm64 Weixin NetType/5G "
            "Language/zh_CN ABI/arm64"
        ),
        "X-Requested-With": "XMLHttpRequest",
    }
    data = {
        "openId": "",
        "account": username,
        "collegeId": college_id,
        "password": password,
    }
    resp = _session().post(
        f"{config.BASE_URL}/jsUserLogin",
        headers=headers,
        data=data,
        timeout=config.REQUEST_TIMEOUT,
    )
    return resp.json()


def untying_method(user_id: str) -> dict[str, Any]:
    """微信解绑"""
    headers = {
        "Accept": "application/json, text/javascript, */*; q=0.01",
        "Accept-Language": "zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7",
        "Connection": "keep-alive",
        "Referer": "http://wap.xiaoyuananquantong.com/guns-vip-main/wap/jspersonal",
        "User-Agent": (
            "Mozilla/5.0 (Linux; Android 16; MEIZU 20 Pro Build/BQ2A.251110.001-"
            "BP2A.250605.031.A3; wv) AppleWebKit/537.36 (KHTML, like Gecko) "
            "Version/4.0 Chrome/146.0.7680.178 Mobile Safari/537.36 XWEB/1460249 "
            "MMWEBSDK/20260202 MMWEBID/3950 REV/6666666666666666666666666666666666666666 "
            "MicroMessenger/8.0.71.3080(0x28004750) WeChat/arm64 Weixin NetType/5G "
            "Language/zh_CN ABI/arm64"
        ),
        "X-Requested-With": "XMLHttpRequest",
    }
    params = {"userId": user_id}
    resp = _session().get(
        f"{config.BASE_URL}/JsUntying",
        params=params,
        headers=headers,
        timeout=config.REQUEST_TIMEOUT,
    )
    return resp.json()


# ---------- 课程与考试 ----------

def get_course_list(user_id: str) -> list[dict[str, Any]]:
    """获取课程列表及完成状态"""
    resp = _session().post(
        f"{config.BASE_URL}/compulsory/list",
        data={"userId": user_id, "collegeId": config.COLLEGE_ID},
        timeout=config.REQUEST_TIMEOUT,
    )
    return resp.json()["data"]


def complete_unit_test(user_id: str, article_id: str, title: str,
                       question: str, ques_type: str) -> None:
    """完成一个单元的测试"""
    data = {
        "articleId": article_id,
        "title": title,
        "userId": user_id,
        "ah": "",
        "question": question,
        "quesType": ques_type,
    }
    _session().post(
        f"{config.BASE_URL}/unitTest",
        data=data,
        timeout=config.REQUEST_TIMEOUT,
    )


def create_exam(user_id: str) -> dict[str, Any]:
    """创建考试"""
    resp = _session().post(
        f"{config.BASE_URL}/test/create",
        data={"examId": config.EXAM_ID, "userId": user_id},
        timeout=config.REQUEST_TIMEOUT,
    )
    return resp.json()


def get_exam(log_id: str, user_id: str) -> dict[str, Any]:
    """获取考题列表"""
    url = f"{config.BASE_URL}/test/list?logId={log_id}&page=1&limit=200&ah=&userId={user_id}"
    resp = _session().get(url, timeout=config.REQUEST_TIMEOUT)
    return resp.json()


def get_exam_id(user_id: str) -> dict[str, Any]:
    """获取考试 ID"""
    resp = _session().post(
        f"{config.BASE_URL}/test/getTest",
        data={"examType": 2, "examClass": 20, "userId": user_id, "ah": ""},
        timeout=config.REQUEST_TIMEOUT,
    )
    return resp.json()


# ---------- 数据库（题库） ----------

def get_answer_by_id(question_id: str) -> tuple[tuple[str, str], ...]:
    """
    从 SQLite 题库查询答案，返回适用于 requests POST 的 tuple 片段。

    返回格式：(("question", ...), ("questionId", ...), ("quesType", ...))
    查询不到时返回空 tuple。
    """
    db_path = f"{config.SCRIPT_DIR}/database.db"
    if not os.path.exists(db_path):
        print("错误：未找到题库文件 database.db，请确保它与本程序在同一目录。")
        end(1)

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # 使用参数化查询防止 SQL 注入
    try:
        cursor.execute(
            "SELECT questionId, answer, quesType FROM tiku WHERE questionId = ? ORDER BY questionId",
            (question_id,),
        )
    except sqlite3.OperationalError:
        print("错误：题库文件 database.db 损坏（缺少 tiku 表），请重新获取脚本包。")
        end(1)
    records = cursor.fetchall()
    conn.close()

    if not records:
        print(f"题库中未找到题目 {question_id}")
        return ()

    row = records[0]
    qid, answer, qtype = row

    if qtype == "2":
        # 多选题：拼接多选项
        parts = [f"~{r[0]}-{r[1]}" for r in records]
        question = "".join(parts)
    else:
        # 单选 / 判断
        question = f"{qid}-{answer}"

    return (
        ("question", question),
        ("questionId", qid),
        ("quesType", qtype),
    )


# ---------- 提交答案 ----------

def imitate_exam(exam_id: str, log_id: str, user_id: str,
                 answers: list[tuple[str, str]]) -> requests.Response:
    """提交考试答案"""
    headers = {
        "Content-Type": "application/x-www-form-urlencoded;charset=UTF-8",
        "Referer": (
            f"{config.BASE_URL}/newStudentssimulate"
            f"?examId={exam_id}&examType=2&userId={user_id}&ah"
        ),
    }
    data = [
        ("examId", exam_id),
        ("examType", "2"),
        ("sysSource", "20"),
        ("logId", log_id),
        ("userId", user_id),
        ("ah", ""),
    ]
    data.extend(answers)

    return _session().post(
        f"{config.BASE_URL}/imitateTest",
        data=data,
        headers=headers,
        timeout=config.REQUEST_TIMEOUT,
    )
