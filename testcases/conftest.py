import pytest
from api.user_api import UserApi
from config.config import BASE_URL, TEST_USER, TEST_PWD, DEFAULT_HEADERS  # 你的配置

@pytest.fixture(scope="session")
def authorized_api():
    """
    session 级 fixture：整个测试会话只登录一次，
    返回已注入 token 的 UserApi 实例（同时兼容其他业务接口）
    """
    api = UserApi(base_url=BASE_URL, headers=DEFAULT_HEADERS)
    api.login(TEST_USER, TEST_PWD)
    yield api
    # 可选：teardown 时登出
    api.clear_token()