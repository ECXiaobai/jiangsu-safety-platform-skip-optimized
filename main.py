import time
import utils
import json
import os
import sys
import shutil

# “2026江苏省大学新生安全知识教育”一键完成脚本 (登录版)
# Scwizard/HAM:BA4TLH
# 2025/08/14 (Rebuild at 2026/07/25)

# print("本脚本开源免费，禁止倒卖。") # 卖吧 无所谓了

STATS = False # 脚本用量统计，我们只保存您的脚本最终得分和运行时长，不会记录浏览器指纹、IP地址、客户端信息等内容
# 如果您不想开启此功能，请把 True 改成 False

if getattr(sys, "frozen", False):
    # PyInstaller 打包运行：临时解压目录不可写持久，数据库必须放在 exe 旁边
    script_dir = os.path.dirname(os.path.abspath(sys.executable))
else:
    script_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(script_dir)
print("切换到工作目录：", os.getcwd())
# 首次运行时把内置题库复制到 exe 旁，之后缓存（tiku_article）写入 exe 旁的数据库
if getattr(sys, "frozen", False):
    bundled_db = os.path.join(sys._MEIPASS, "database.db")
    real_db = os.path.join(script_dir, "database.db")
    if not os.path.exists(real_db) and os.path.exists(bundled_db):
        shutil.copy(bundled_db, real_db)
        print("已初始化数据库：", real_db)
# 修一下目录问题
# 2026 的时候回来发现还有一些历史遗留问题，需要解决，比如数据库的路径
print("您正在运行：登录版 (v1.0.5)")
session = utils.session # 统一采用 Session 管理会话继承 cookies
collegeId = utils.getUserSchool()
username = str(input("请输入账号：").strip())
password = str(input("请输入密码：").strip())

loginResult = utils.loginMethod(username, password, collegeId)
if loginResult['success'] == False:
    print("登录失败，请检查账号密码和学校是否正确")
    print(loginResult)
    utils.end(1)
openId = loginResult['data']['openId']
userId = loginResult['data']['userId']
print(f"获取到了userId {userId}，开始执行脚本")
realCollegeId = loginResult['data'].get('collegeId', collegeId)
print("查询课程使用学校ID：%s" % realCollegeId)
start_time = time.time() # 计时器，启动！
tiku1 = {"articleId":"2080135073788600321","title":"题库学习","userId":userId,"ah":"","question":"2080136617019842561-1","quesType":"3"}
tiku2 = {"articleId":"2079132357549375490","title":"入学安全","userId":userId,"ah":"","question":"2079154657984266242-1","quesType":"3"}
tiku3 = {"articleId":"2079133938168643585","title":"国家安全","userId":userId,"ah":"","question":"2079156723934838786-B","quesType":"1"}
tiku4 = {"articleId":"2079139032318623745","title":"财物安全","userId":userId,"ah":"","question":"2079446660177477633-1","quesType":"3"}
tiku5 = {"articleId":"2079140991327027201","title":"心理健康","userId":userId,"ah":"","question":"2079467760328392705-D","quesType":"1"}
tiku6 = {"articleId":"2079142411614830593","title":"消防安全","userId":userId,"ah":"","question":"2079492272201678850-C","quesType":"1"}
tiku7 = {"articleId":"2079143452481699842","title":"人身安全","userId":userId,"ah":"","question":"2079527272678703105-1","quesType":"3"}
tiku8 = {"articleId":"2079144978977669121","title":"交通安全","userId":userId,"ah":"","question":"2079540470853156866-A","quesType":"1"}
tiku9 = {"articleId":"2079146093836255234","title":"禁毒防艾","userId":userId,"ah":"","question":"2079548501443756034-1","quesType":"3"}
tiku10 = {"articleId":"2079146628521934850","title":"应急救护","userId":userId,"ah":"","question":"~2079553855799967746-A~2079553855799967746-B~2079553855799967746-C~2079553855799967746-D","quesType":"2"}
tiku11 = {"articleId":"2079147344531570690","title":"防灾减灾","userId":userId,"ah":"","question":"2079558043292418049-D","quesType":"1"}

table = {0:tiku1, 1:tiku2, 2:tiku3, 3:tiku4, 4:tiku5, 5:tiku6, 6:tiku7, 7:tiku8, 8:tiku9, 9:tiku10, 10:tiku11} # 题库映射

# ===== 必修课程（courseType=1）完成模块 =====
# 平台考试资格判定依赖必修课程完成度（getRecord.bx），原脚本只完成专题课（courseType=2）。
# 必修课每篇文章只需答对 1 道题即可通过，这里用试错法找答案。

def completeCompulsory(userId, collegeId):
    import sqlite3
    db_path = os.path.join(script_dir, 'database.db')
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute("CREATE TABLE IF NOT EXISTS tiku_article (articleId TEXT PRIMARY KEY, questionId TEXT, answer TEXT, quesType TEXT)")
    conn.commit()

    def get_cache(aid):
        cur.execute("SELECT questionId, answer, quesType FROM tiku_article WHERE articleId=?", (aid,))
        return cur.fetchone()

    def save_cache(aid, qid, ans, qt):
        cur.execute("INSERT OR REPLACE INTO tiku_article (articleId, questionId, answer, quesType) VALUES (?,?,?,?)", (aid, qid, ans, qt))
        conn.commit()

    def submit_unit(aid, atitle, qid, ans, qt):
        if qt == "2":
            qstr = "".join("~%s-%s"%(qid,c) for c in ans)
        else:
            qstr = "%s-%s"%(qid,ans)
        form = [("articleId",aid),("title",atitle),("userId",userId),("ah",""),
                ("question",qstr),("questionId",qid),("quesType",qt)]
        rr = session.post("http://wap.xiaoyuananquantong.com/guns-vip-main/wap/unitTest", data=form).text
        try:
            return json.loads(rr).get("data",{}).get("isSuccess", False)
        except Exception:
            return False

    print("正在检查必修课程完成度：")
    res = session.post("http://wap.xiaoyuananquantong.com/guns-vip-main/wap/compulsory/list", data={"userId":userId,"collegeId":collegeId,"courseType":"1"}).text
    data = json.loads(res)
    courses = data["data"]
    j = 1
    unfinished = []
    for i in courses:
        if i["isFinsh"]:
            print("必修第%s课 %s 已完成" % (j, i["name"]))
        else:
            unfinished.append(i)
            print("必修第%s课 %s 未完成" % (j, i["name"]))
        j += 1
    if not unfinished:
        print("必修课程已全部完成")
        return
    for c in unfinished:
        cid = c["id"]
        cname = c["name"]
        print("正在完成必修课 %s ..." % cname)
        res = session.post("http://wap.xiaoyuananquantong.com/guns-vip-main/wap/directory/list", data={"name":"","courseId":cid,"userId":userId,"collegeId":collegeId,"ah":""}).text
        d = json.loads(res)
        for chap in d["data"]:
            for item in chap["list"]:
                if item["isFinsh"]:
                    continue
                aid = item["id"]
                atitle = item.get("course", cname)
                # 0) 标记文章已观看（平台 8/28 新增 markArticleViewed 校验，
                #    正常流程先标记观看再取题，模拟真实学习避免服务器不计数）
                try:
                    session.get("http://wap.xiaoyuananquantong.com/guns-vip-main/wap/markArticleViewed", params={"articleId":aid,"userId":userId})
                except Exception:
                    pass
                # 1) 优先用缓存答案直接提交（1 次请求）
                cache = get_cache(aid)
                if cache:
                    qid, ans, qt = cache
                    if submit_unit(aid, atitle, qid, ans, qt):
                        print("  [OK] %s -> %s (缓存)" % (atitle, ans))
                        continue
                    else:
                        cur.execute("DELETE FROM tiku_article WHERE articleId=?", (aid,))
                        conn.commit()
                        print("  [--] %s 缓存失效，重新试错" % atitle)
                # 2) 无缓存：取题 + 试错
                rq = session.get("http://wap.xiaoyuananquantong.com/guns-vip-main/wap/question/list", params={"articleId":aid,"ah":""}).text
                try:
                    qlist = json.loads(rq).get("data",{}).get("list",[])
                except Exception:
                    qlist = []
                if not qlist:
                    print("  [--] %s 无题目，跳过" % atitle)
                    continue
                ok = False
                for q in qlist:
                    qid = q["id"]
                    qt = q["quesType"]
                    if qt == "判断":
                        for ans in ("1","0"):
                            if submit_unit(aid, atitle, qid, ans, "3"):
                                print("  [OK] %s 判断题 %s -> %s" % (atitle,qid,ans))
                                save_cache(aid, qid, ans, "3")
                                ok = True
                                break
                    elif qt == "单选":
                        for opt in "ABCD":
                            if submit_unit(aid, atitle, qid, opt, "1"):
                                print("  [OK] %s 单选题 %s -> %s" % (atitle,qid,opt))
                                save_cache(aid, qid, opt, "1")
                                ok = True
                                break
                    else:
                        for combo in ("ABCD","ABC","ABD","ACD","BCD","AB","AC","AD","BC","BD","CD","A","B","C","D"):
                            if submit_unit(aid, atitle, qid, combo, "2"):
                                print("  [OK] %s 多选题 %s -> %s" % (atitle,qid,combo))
                                save_cache(aid, qid, combo, "2")
                                ok = True
                                break
                    if ok:
                        break
                if not ok:
                    print("  [!!] %s 未能通过，请手动检查" % atitle)
    print("必修课程完成度查询(完成后)：")
    res = session.post("http://wap.xiaoyuananquantong.com/guns-vip-main/wap/compulsory/list", data={"userId":userId,"collegeId":collegeId,"courseType":"1"}).text
    data = json.loads(res)
    for i in data["data"]:
        print("%s: %s" % (i["name"], "已完成" if i["isFinsh"] else "未完成"))
    conn.close()

res = session.post("http://wap.xiaoyuananquantong.com/guns-vip-main/wap/compulsory/list", data={"userId":userId,"collegeId":realCollegeId}).text
data = json.loads(res)
print("正在遍历课程列表，查询完成度：")
course = data["data"]
j = 1
k = 0
unfinished = []
for i in course:
    if i["isFinsh"] == True:
        print(f"第{j}课 {i['name']} 已完成")
    else:
        unfinished.append(k)
        print(f"第{j}课 {i['name']} 未完成")
    j += 1
    k += 1

process = ()
# 保留一个turple 但这个东西不太好搞 且没啥实质影响 就不搞了()
if unfinished == []:
    print("检测到所有课程已经完成，直接进入考试")
else:
    for i in unfinished:
        print(f"正在完成 {table[i]['title']}")
        res = session.post("http://wap.xiaoyuananquantong.com/guns-vip-main/wap/unitTest", data=table[i]).text
        # res = json.loads(res)
    print("课程完成度查询(完成后)：")
    res = session.post("http://wap.xiaoyuananquantong.com/guns-vip-main/wap/compulsory/list",data={"userId":userId,"collegeId":realCollegeId}).text
    data = json.loads(res)
    course = data["data"]
    j = 1
    for i in course:
        if i["isFinsh"] == True:
            print("第%s课 %s 已完成" % (j, i["name"]))
        else:
            print("第%s课 %s 未完成" % (j, i["name"]))
        j += 1
    print("已完成课程学习")
print("正在检查必修课程...")
completeCompulsory(userId, realCollegeId)
print("正在进入考试流程...")
examResult = utils.creatExam(userId)
if not isinstance(examResult, dict) or "data" not in examResult or "logId" not in examResult["data"]:
    print("创建考试失败，平台返回：", examResult)
    print("可能原因：已参加过考试、学校考试未开放，或账号状态异常")
    utils.end(1)
logId = examResult["data"]["logId"]
print("取得logId %s" % logId)
examList = utils.getExam(logId=logId, userId=userId)
if not isinstance(examList, dict) or "data" not in examList or "data" not in examList["data"]:
    print("获取考题失败，平台返回：", examList)
    utils.end(1)
print("取得考题列表，正在从数据库中读取答案然后整合...")
questions = examList["data"]["data"]
questionList = []
data = utils.getExamId(userId)
if not isinstance(data, dict):
    print("获取考试信息失败，平台返回：", data)
    utils.end(1)
if data.get("code") == 500:
    print("""出错了！你的账号未完成内容学习，可能由以下几点原因导致
        1.你所在学校不属于江苏省
        2.脚本题库出错
        3.平台更新""")
    print("程序已自动结束，非常抱歉给您带来不便，您可以联系脚本作者！")
    utils.end(1)
if "data" not in data:
    print("获取考试信息失败，平台返回：", data)
    utils.end(1)
examId = data["data"]["id"]
for i in range(0,50):
    questionList.append(questions[i]["questionId"])
answers = ()
for i in questionList:
    try:
        answers += utils.getAnswerById(i)
    except:
        print("err: 数据库读写错误")
        utils.end(1)
print("答案已生成，正在执行imitateExam提交答案...")
res = utils.imitateExam(examId, logId, userId, answers)
# print(res.text)
res = json.loads(res.text)
score = res["data"]["count"]
print(f'得分：{score}')
if int(score) != 100:
    print("没到100分，这是一个历史遗留问题，重刷一次就行了，因为题库录入的时候有一题出错了。")
else:
    print(f"前往 http://wap.xiaoyuananquantong.com/guns-vip-main/wap/qrCode?userId={userId} 下载结课证书")
utils.UntyingMethod(userId)  # 静默解绑 openId，不打印
end_time = time.time()
elapsed_ms = (end_time - start_time) * 1000
print(f"execute time: {elapsed_ms:.3f} ms.")
print("开源地址：https://github.com/ECXiaobai/jiangsu-safety-platform-skip-optimized")
print("获取更多免费脚本加Q群：1048953452")
if STATS == True:
    try:
        res = utils.upload_stats(score, round(elapsed_ms, 3))
        print("脚本统计已上传，只记录分数和运行时长，不会保存您的IP地址与设备信息，您可以在脚本开头选择是否开启该功能")
        print(res)
    except:
        print("脚本统计未被上传")
input("程序结束，感谢使用!")
