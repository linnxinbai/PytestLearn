import pytest
from api.user_api import UserApi
from config.config import BASE_URL, TEST_USER, TEST_PWD, DEFAULT_HEADERS
from utils.logger import get_logger


logger = get_logger()


class TestLogin:
    """登录接口断言"""
    def test_login_success(self):
        """登录成功：返回200，无错误信息，返回token"""
        api = UserApi(base_url=BASE_URL, headers=DEFAULT_HEADERS)
        result = api.login(TEST_USER, TEST_PWD)

        assert result["msg_code"] == 200
        assert result.get("error_code") is None
        assert result.get("token") is not None
        logger.info(f"登录接口返回结果: {result}")

    def test_login_fail_wrong_password(self):
        """密码错误：应返回错误码或异常"""
        api = UserApi(base_url=BASE_URL, headers=DEFAULT_HEADERS)
        result = api.login(TEST_USER, "wrong_password")

        # 根据实际接口，可能是 msg_code != 200 或存在 error_code
        assert result["msg_code"] != 200 or result.get("error_code") is not None

class TestUserCrud:
    """用户增删改查"""
    # @pytest.mark.parametrize("username, password, role_id, dates, phone",
    #                          [("testadduser", "tset6789890", "123456789", "2023-12-31", "13800000000")])
    # def test_add_user_success(self, authorized_api,username, password, role_id, dates, phone):
    def test_add_user_success(self, authorized_api):
        """新增成功，返回成功信息和200"""
        username = "testadduser"
        password = "tset6789890"
        role_id = "123456789"
        dates = "2023-12-31"
        phone = "13800000000"
        result = authorized_api.add_user(username, password, role_id, dates, phone)

        assert result.get("msg_code") == 200
        assert result.get("error_code") is None
        assert result.get("msg") is not None

    @pytest.mark.parametrize("user_id", [123839387391912])
    def test_query_user(self, authorized_api,user_id):
        """查询用户：成功返回 200"""
        # 先用一个已知 user_id 查询，或依赖 add_user 的结果
        resp = authorized_api.query_user(user_id)
        assert resp["msg_code"] == 200

    @pytest.mark.parametrize(
        "username, password, role_id, dates, phone",
        [("test_update_01", "654321", "2", "2026-06-30", "13900139001")]
    )
    def test_update_user(self, authorized_api, username, password, role_id, dates, phone):
        """更新用户"""
        resp = authorized_api.update_user(username, password, role_id, dates, phone)
        assert resp.get("msg_code") == 200
        assert resp.get("error_code") is None

    def test_delete_user(self, authorized_api):
        """删除用户：成功返回 200"""
        resp = authorized_api.delete_user(user_id=123839387391912)
        assert resp["msg_code"] == 200
        assert resp.get("error_code") is None


class TestUserFlow:
    """查询用户后删除"""
    @pytest.mark.parametrize("user_id", [123839387391912])
    def test_full_user_lifecycle(self, authorized_api,user_id):
        """用户生命周期：查询 -> 删除"""
        resp = authorized_api.query_user(user_id)
        resp1 = authorized_api.delete_user(user_id)

        assert resp["msg_code"] == 200
        assert resp1["msg_code"] == 200


