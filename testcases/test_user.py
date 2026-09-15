import json

import allure
import pytest

from api.user_api import UserApi
from config.config import BASE_URL, TEST_USER, TEST_PWD, DEFAULT_HEADERS
from utils.logger import get_logger


logger = get_logger()


def attach_response(name, response):
    """把接口响应附加到 Allure 报告中"""
    allure.attach(
        json.dumps(response, ensure_ascii=False, indent=2),
        name=name,
        attachment_type=allure.attachment_type.JSON
    )


@allure.feature("用户管理")
class TestLogin:
    """登录接口断言"""

    @allure.story("用户登录")
    @allure.title("正常登录成功")
    def test_login_success(self):
        """登录成功：返回200，无错误信息，返回token"""

        with allure.step("创建用户接口客户端"):
            api = UserApi(
                base_url=BASE_URL,
                headers=DEFAULT_HEADERS
            )

        with allure.step("使用正确账号密码调用登录接口"):
            result = api.login(TEST_USER, TEST_PWD)

            attach_response(
                "登录接口响应",
                result
            )

        with allure.step("校验登录返回结果"):
            assert result["msg_code"] == 200
            assert result.get("error_code") is None
            assert result.get("token") is not None

        logger.info(f"登录接口返回结果: {result}")

    @allure.story("用户登录")
    @allure.title("密码错误登录失败")
    def test_login_fail_wrong_password(self):
        """密码错误：应返回错误码或异常"""

        with allure.step("创建用户接口客户端"):
            api = UserApi(
                base_url=BASE_URL,
                headers=DEFAULT_HEADERS
            )

        with allure.step("使用错误密码调用登录接口"):
            result = api.login(
                TEST_USER,
                "wrong_password"
            )

            attach_response(
                "错误密码登录接口响应",
                result
            )

        with allure.step("校验密码错误场景"):
            # 根据实际接口，可能是 msg_code != 200 或存在 error_code
            assert (
                result["msg_code"] != 200
                or result.get("error_code") is not None
            )


@allure.feature("用户管理")
class TestUserCrud:
    """用户增删改查"""

    @allure.story("新增用户")
    @allure.title("新增用户成功")
    def test_add_user_success(self, authorized_api):
        """新增成功，返回成功信息和200"""

        with allure.step("准备新增用户数据"):
            username = "testadduser"
            password = "tset6789890"
            role_id = "123456789"
            dates = "2023-12-31"
            phone = "13800000000"

            allure.dynamic.parameter("username", username)
            allure.dynamic.parameter("role_id", role_id)
            allure.dynamic.parameter("dates", dates)
            allure.dynamic.parameter("phone", phone)

        with allure.step("调用新增用户接口"):
            result = authorized_api.add_user(
                username,
                password,
                role_id,
                dates,
                phone
            )

            attach_response(
                "新增用户接口响应",
                result
            )

        with allure.step("校验新增用户结果"):
            assert result.get("msg_code") == 200
            assert result.get("error_code") is None
            assert result.get("msg") is not None

    @allure.story("查询用户")
    @allure.title("根据用户ID查询用户")
    @pytest.mark.parametrize(
        "user_id",
        [123839387391912]
    )
    def test_query_user(
        self,
        authorized_api,
        user_id
    ):
        """查询用户：成功返回 200"""

        with allure.step(f"查询用户，user_id={user_id}"):
            resp = authorized_api.query_user(
                user_id
            )

            attach_response(
                "查询用户接口响应",
                resp
            )

        with allure.step("校验查询用户结果"):
            assert resp["msg_code"] == 200

    @allure.story("更新用户")
    @allure.title("更新用户信息成功")
    @pytest.mark.parametrize(
        "username, password, role_id, dates, phone",
        [
            (
                "test_update_01",
                "654321",
                "2",
                "2026-06-30",
                "13900139001"
            )
        ]
    )
    def test_update_user(
        self,
        authorized_api,
        username,
        password,
        role_id,
        dates,
        phone
    ):
        """更新用户"""

        with allure.step("准备更新用户数据"):
            allure.dynamic.parameter(
                "username",
                username
            )
            allure.dynamic.parameter(
                "role_id",
                role_id
            )
            allure.dynamic.parameter(
                "dates",
                dates
            )
            allure.dynamic.parameter(
                "phone",
                phone
            )

        with allure.step("调用更新用户接口"):
            resp = authorized_api.update_user(
                username,
                password,
                role_id,
                dates,
                phone
            )

            attach_response(
                "更新用户接口响应",
                resp
            )

        with allure.step("校验更新用户结果"):
            assert resp.get("msg_code") == 200
            assert resp.get("error_code") is None

    @allure.story("删除用户")
    @allure.title("删除用户成功")
    def test_delete_user(self, authorized_api):
        """删除用户：成功返回 200"""

        user_id = 123839387391912

        with allure.step(
            f"调用删除用户接口，user_id={user_id}"
        ):
            resp = authorized_api.delete_user(
                user_id=user_id
            )

            attach_response(
                "删除用户接口响应",
                resp
            )

        with allure.step("校验删除用户结果"):
            assert resp["msg_code"] == 200
            assert resp.get("error_code") is None


@allure.feature("用户管理")
class TestUserFlow:
    """查询用户后删除"""

    @allure.story("用户生命周期")
    @allure.title("查询用户后删除用户")
    @pytest.mark.parametrize(
        "user_id",
        [123839387391912]
    )
    def test_full_user_lifecycle(
        self,
        authorized_api,
        user_id
    ):
        """用户生命周期：查询 -> 删除"""

        with allure.step(
            f"查询用户，user_id={user_id}"
        ):
            resp = authorized_api.query_user(
                user_id
            )

            attach_response(
                "查询用户接口响应",
                resp
            )

            assert resp["msg_code"] == 200

        with allure.step(
            f"删除用户，user_id={user_id}"
        ):
            resp1 = authorized_api.delete_user(
                user_id
            )

            attach_response(
                "删除用户接口响应",
                resp1
            )

            assert resp1["msg_code"] == 200
