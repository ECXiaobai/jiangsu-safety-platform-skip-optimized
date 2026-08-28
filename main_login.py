"""
"2026江苏省大学新生安全知识教育"一键完成脚本 - 登录版
Scwizard/HAM:BA4TLH
2025/08/14 (Rebuild at 2026/07/25, Optimized 2026/07/29)
"""
import argparse
import json
import os
import time
import sys

import config
import utils


def complete_courses(user_id):
    """遍历并完成所有未完成的课程"""
    print("正在遍历课程列表，查询完成度：")
    course_list = utils.get_course_list(user_id)
    unfinished = []
    for idx, course in enumerate(course_list):
        status = "已完成" if course["isFinsh"] else "未完成"
        print(f"第{idx + 1}课 {course['name']} {status}")
        if not course["isFinsh"]:
            unfinished.append(idx)

    if not unfinished:
        print("检测到所有课程已经完成，直接进入考试")
        return

    for idx in unfinished:
        tiku = config.TIKU[idx]
        print(f"正在完成 {tiku['title']}")
        utils.complete_unit_test(user_id, **tiku)

    # 再次查询确认完成状态
    print("课程完成度查询(完成后)：")
    course_list = utils.get_course_list(user_id)
    for idx, course in enumerate(course_list):
        status = "已完成" if course["isFinsh"] else "未完成"
        print(f"第{idx + 1}课 {course['name']} {status}")
    print("已完成课程学习")


def run_exam(user_id):
    """执行考试流程"""
    print("正在进入考试流程...")

    # 创建考试
    exam_data = utils.create_exam(user_id)
    log_id = exam_data["data"]["logId"]
    print(f"取得logId {log_id}")

    # 获取考题
    exam_list = utils.get_exam(log_id, user_id)
    questions = exam_list["data"]["data"]
    print(f"取得考题列表({len(questions)}题)，正在从数据库中读取答案...")

    # 提取题目ID
    question_ids = [q["questionId"] for q in questions[:50]]

    # 获取考试ID
    exam_info = utils.get_exam_id(user_id)
    if exam_info.get("code") == 500 or "data" not in exam_info:
        print("""出错了！你的账号未完成内容学习，可能由以下几点原因导致：
        1. 你所在学校不属于江苏省
        2. 脚本题库出错
        3. 平台更新""")
        print("程序已自动结束，非常抱歉给您带来不便，您可以联系脚本作者！")
        utils.end(1)

    exam_id = exam_info["data"]["id"]

    # 从题库查询答案（使用列表代替元组拼接）
    answers = []
    for qid in question_ids:
        result = utils.get_answer_by_id(qid)
        if not result:
            print(f"错误：题库中未找到题目 {qid} 的答案")
            utils.end(1)
        answers.extend(result)

    # 提交答案
    print(f"答案已生成（{len(answers)} 题），正在执行 imitateExam 提交答案...")
    resp = utils.imitate_exam(exam_id, log_id, user_id, answers)
    result = resp.json()
    score = result["data"]["count"]
    print(f"得分：{score}")

    if int(score) != 100:
        print("没到100分，这是一个历史遗留问题，重刷一次就行了，因为题库录入的时候有一题出错了。")
    else:
        print(f"前往 {config.BASE_URL}/qrCode?userId={user_id} 下载结课证书")


def main():
    # 解析命令行参数（--proxy / --log）
    parser = argparse.ArgumentParser(description="江苏省安全教育平台一键完成脚本 - 登录版")
    parser.add_argument("--proxy", help="HTTP/HTTPS 代理地址，例如 http://127.0.0.1:8080")
    parser.add_argument("--log", action="store_true", help="打印每次请求与响应，方便抓包调试")
    args = parser.parse_args()
    config.PROXY = args.proxy
    config.PRINT_LOG = args.log

    # 切换到脚本所在目录
    os.chdir(config.SCRIPT_DIR)
    print(f"切换到工作目录：{os.getcwd()}")
    print("您正在运行：登录版")

    # 获取学校
    college_id = utils.get_user_school()

    # 获取账号密码
    username = input("请输入账号：").strip()
    password = input("请输入密码：").strip()

    # 登录
    login_result = utils.login_method(username, password, college_id)
    if not login_result.get("success"):
        print("登录失败，请检查账号密码和学校是否正确")
        utils.end(1)

    user_id = login_result["data"]["userId"]
    print(f"获取到了userId {user_id}，开始执行脚本")
    start_time = time.time()

    # 完成课程
    complete_courses(user_id)

    # 执行考试
    run_exam(user_id)

    # 解绑并退出登录（成功时静默，失败才提示）
    unbind_result = utils.untying_method(user_id)
    if not unbind_result.get("success"):
        print(f"解绑失败：{unbind_result.get('message', unbind_result)}")

    # 计时
    elapsed_ms = (time.time() - start_time) * 1000
    print(f"执行耗时: {elapsed_ms:.3f} ms")
    print("项目地址: https://github.com/ECXiaobai/jiangsu-safety-platform-skip-optimized")

    print("获取更多免费脚本加Q群：1048953452")
    input("程序结束，感谢使用！")


if __name__ == "__main__":
    main()
