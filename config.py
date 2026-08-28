"""
共享配置 - 题库数据及常量
"""
import os
import sys


def _get_exe_dir() -> str:
    """获取 exe / 脚本所在目录（兼容 PyInstaller 打包和源码运行两种模式）"""
    if getattr(sys, "frozen", False):
        # PyInstaller 打包成 exe 时，sys.executable 是 exe 的真实路径
        return os.path.dirname(os.path.abspath(sys.executable))
    # 源码模式
    return os.path.dirname(os.path.abspath(__file__))


# 脚本工作目录（exe 或 .py 文件所在的目录，不是临时解压目录）
SCRIPT_DIR = _get_exe_dir()

# 学校ID（江苏省）
COLLEGE_ID = "1224316234189443073"

# 考试ID
EXAM_ID = "1948924196784492546"

# 平台基础 URL
BASE_URL = "http://wap.xiaoyuananquantong.com/guns-vip-main/wap"

# ===== 题库映射 =====
# 每个题库条目字段说明：
#   article_id - 文章/课程ID（与 complete_unit_test 的参数一致）
#   title      - 课程名称
#   question   - 题目ID(含题型后缀)
#   ques_type  - 题型: 1=单选, 2=多选, 3=判断

TIKU = [
    {"article_id": "2080135073788600321", "title": "题库学习",
     "question": "2080136617019842561-1", "ques_type": "3"},
    {"article_id": "2079132357549375490", "title": "入学安全",
     "question": "2079154657984266242-1", "ques_type": "3"},
    {"article_id": "2079133938168643585", "title": "国家安全",
     "question": "2079156723934838786-B", "ques_type": "1"},
    {"article_id": "2079139032318623745", "title": "财物安全",
     "question": "2079446660177477633-1", "ques_type": "3"},
    {"article_id": "2079140991327027201", "title": "心理健康",
     "question": "2079467760328392705-D", "ques_type": "1"},
    {"article_id": "2079142411614830593", "title": "消防安全",
     "question": "2079492272201678850-C", "ques_type": "1"},
    {"article_id": "2079143452481699842", "title": "人身安全",
     "question": "2079527272678703105-1", "ques_type": "3"},
    {"article_id": "2079144978977669121", "title": "交通安全",
     "question": "2079540470853156866-A", "ques_type": "1"},
    {"article_id": "2079146093836255234", "title": "禁毒防艾",
     "question": "2079548501443756034-1", "ques_type": "3"},
    {"article_id": "2079146628521934850", "title": "应急救护",
     "question": "~2079553855799967746-A~2079553855799967746-B~2079553855799967746-C~2079553855799967746-D",
     "ques_type": "2"},
    {"article_id": "2079147344531570690", "title": "防灾减灾",
     "question": "2079558043292418049-D", "ques_type": "1"},
]

# 请求超时（秒）
# 参考原版：不设置超时（None = 无限等待），避免服务器响应稍慢就误判为超时
REQUEST_TIMEOUT = None

# 网络请求重试：遇到连接超时/读超时/服务器 5xx 时按指数退避自动重试，避免偶发网络抖动直接崩溃
REQUEST_RETRIES = 3        # 最大重试次数（含首次请求）
REQUEST_RETRY_BACKOFF = 2  # 退避基数（秒），第 n 次重试前等待 backoff ** n

# 抓包/调试相关（可通过命令行 --proxy / --log 开启）
PROXY = None        # 代理地址，例如 "http://127.0.0.1:8080"
PRINT_LOG = False   # 打印每次请求与响应，方便抓包调试
MAX_LOG_BODY = 120  # --log 模式下打印请求体的最大字符数
MAX_LOG_RESP = 200  # --log 模式下打印响应的最大字符数
