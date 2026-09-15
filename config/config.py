# ========== 服务器基础配置 ==========
from typing import Dict

BASE_URL = "http://127.0.0.1:8787"         # 被测服务器地址（截图中的 flaskServer）

# ========== 账号密码配置（按角色划分） ==========
# 示例账号（来自接口文档）
TEST_USER = "test01"
TEST_PWD  = "admin123"

# ========== 基础请求头（最常用） ==========
DEFAULT_HEADERS: dict[str, str] = {
    "Content-Type": "application/x-www-form-urlencoded;charset=UTF-8",
    "Accept": "application/json",
}

# 如果后续有多角色，直接在此扩展：
# ADMIN_USER = "admin"
# ADMIN_PWD  = "admin123"
# USER_USER  = "user01"
# USER_PWD   = "user123"

