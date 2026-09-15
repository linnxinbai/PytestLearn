from api.base_api import BaseApi


class UserApi(BaseApi):
    def login(self, username: str, password: str) -> dict:
        """登录接口"""
        res = self.post(
            "/dar/user/login",
            data={"username": username, "passwd": password}
        )
        data = res.json()
        token = data.get("token")
        if token:
            self.set_token(token)
        return data

    def add_user(self, username, password, role_id, dates, phone) -> dict:
        """新增用户接口"""
        res = self.post(
            "/dar/user/addUser",
            data={"username": username, "password": password, "role_id": role_id,
                  "dates": dates, "phone": phone
                  }
        )
        return res.json()

    def delete_user(self, user_id: int) -> dict:
        """删除用户接口"""
        res = self.post(
            "/dar/user/deleteUser",
            data={"user_id": user_id}
        )
        return res.json()

    def query_user(self, user_id: int) -> dict:
        """查询用户接口"""
        res = self.post(
            "/dar/user/queryUser",
            data={"user_id": user_id}
        )
        return res.json()

    def update_user(self, username: str, password: str, role_id: str,
                    dates: str, phone: str) -> dict:
        """修改用户接口"""
        res = self.post(
            "/dar/user/updateUser",
            data={
                "username": username,
                "password": password,
                "role_id": role_id,
                "dates": dates,
                "phone": phone,
            }
        )
        return res.json()
