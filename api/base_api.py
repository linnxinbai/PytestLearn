import requests


class BaseApi:
    def __init__(self, base_url: str, headers: dict = None):
        self.session = requests.Session()
        self.base_url = base_url
        if headers:
            self.session.headers.update(headers)

    def set_token(self, token: str, token_type: str = "Bearer"):
        """统一注入鉴权 Token，后续所有请求自动携带"""
        self.session.headers.update({
            "Authorization": f"{token_type} {token}"
        })

    def clear_token(self):
        """登出或切换账号时清除 Token"""
        self.session.headers.pop("Authorization", None)

    def request(self, method: str, path: str, **kwargs):
        url = f"{self.base_url}{path}"
        try:
            resp = self.session.request(method, url, **kwargs)
            resp.raise_for_status()          # 自动抛 4xx/5xx 异常
            return resp
        except requests.RequestException as e:
            raise RuntimeError(f"请求失败: {url}, 错误: {e}")

    def get(self, path, params=None):
        return self.request("GET", path, params=params)

    def post(self, path, json=None, data=None):
        return self.request("POST", path, json=json, data=data)
