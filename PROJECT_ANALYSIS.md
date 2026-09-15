# PytestLearn 项目分析

本分析只基于源码阅读得出，未执行 pytest，也未执行其他测试命令。

## 一、项目结构

```text
PytestLearn/
├─ main.py
├─ api/
│  ├─ __init__.py
│  ├─ base_api.py
│  └─ user_api.py
├─ config/
│  └─ config.py
├─ utils/
│  ├─ __init__.py
│  └─ logger.py
└─ testcases/
   ├─ __init__.py
   ├─ conftest.py
   └─ test_user.py
```

项目中还存在 `__pycache__` 和日志文件，它们是运行缓存或输出文件，不是主要源码。

## 二、每个 Python 文件的职责

- `main.py`：独立的 requests 登录示例，直接发送登录请求并打印 token，不使用 pytest 和项目 API 封装。
- `config/config.py`：保存 `BASE_URL`、测试账号密码以及默认请求头。
- `utils/logger.py`：提供 `get_logger()`，配置控制台和文件日志。
- `api/base_api.py`：通用 HTTP 基类，负责创建 `requests.Session`、拼接 URL、发送 GET/POST、处理 HTTP 异常，以及设置和清除 token。
- `api/user_api.py`：用户业务 API 封装，提供 `login()`、`add_user()`、`query_user()`、`update_user()`、`delete_user()` 等方法，继承 `BaseApi`。
- `testcases/conftest.py`：定义 pytest fixture `authorized_api`，负责会话级登录并向测试用例提供已授权的 `UserApi` 对象。
- `testcases/test_user.py`：编写登录测试、用户增删改查测试和用户生命周期测试，负责调用业务方法并断言结果。
- 各目录下的 `__init__.py`：当前为空，主要用于包结构和导入支持。

## 三、核心文件之间的关系

```text
test_user.py
    ↓ 使用
conftest.py 中的 authorized_api fixture
    ↓ 创建并登录
user_api.py 中的 UserApi
    ↓ 继承
base_api.py 中的 BaseApi
    ↓ 使用
requests.Session 发送 HTTP 请求
```

测试层不直接处理 requests；业务 API 层描述用户接口；基础 API 层处理 HTTP 细节；fixture 层管理登录状态和测试生命周期。

## 四、从 test_user.py 追踪新增用户用例

以 `test_add_user_success(self, authorized_api)` 为例：

1. pytest 发现测试方法参数 `authorized_api`，在 `testcases/conftest.py` 中查找同名 fixture。
2. fixture 是 `scope="session"`，一次 pytest 测试会话中通常只初始化一次。
3. fixture 创建 `UserApi(base_url=BASE_URL, headers=DEFAULT_HEADERS)`。
4. `UserApi` 继承 `BaseApi`，初始化 `requests.Session`，保存基础 URL，并设置默认请求头。
5. fixture 调用 `api.login(TEST_USER, TEST_PWD)`。
6. `UserApi.login()` 调用 `BaseApi.post()`，再调用 `BaseApi.request()`，最后由 `requests.Session.request()` 发送登录请求。
7. 登录响应被解析为 JSON，读取 `data["token"]`。
8. 如果 token 存在，调用 `set_token()`，把 `Authorization: Bearer <token>` 保存到 session 的公共请求头中。
9. `yield api` 将这个已经登录的 `UserApi` 对象注入测试方法的 `authorized_api` 参数。
10. 测试调用 `authorized_api.add_user(...)`。
11. `add_user()` 通过继承得到的 `post()` 和 `request()` 发送新增用户请求。同一个 session 会自动携带 Authorization 请求头。
12. 接口响应被转换为字典，测试检查 `msg_code`、`error_code` 和 `msg`。
13. 依赖该 fixture 的测试完成后，执行 `api.clear_token()` 清除 session 中的 Authorization 头。

调用链为：

```text
test_add_user_success
  → authorized_api fixture
  → UserApi.login
  → BaseApi.post
  → BaseApi.request
  → requests.Session.request
  → BaseApi.set_token
  → yield api
  → UserApi.add_user
  → BaseApi.post
  → BaseApi.request
  → requests.Session.request
  → 返回 JSON
  → 测试断言
  → BaseApi.clear_token
```

## 五、authorized_api fixture 的执行过程

可以分为三个阶段：

```text
setup：创建 UserApi → 创建 Session → 设置基础配置 → 登录 → 保存 token
测试期间：复用同一个 UserApi 和 Session，执行多个用户接口
teardown：删除 Session 中的 Authorization 请求头
```

`scope="session"` 使多个用例能够复用同一次登录会话，例如新增、查询、修改、删除和生命周期测试。

登录测试 `test_login_success()` 和 `test_login_fail_wrong_password()` 没有使用 `authorized_api`，它们手动创建自己的 `UserApi`，因此不会共享 fixture 的 session 或 token。

## 六、token 的保存和传递

token 并没有通过每个业务方法的参数传递，而是保存在 `requests.Session` 的请求头中：

```text
登录响应 JSON
  → data["token"]
  → UserApi.login()
  → BaseApi.set_token(token)
  → api.session.headers["Authorization"]
  → 后续请求复用同一个 Session
  → requests 自动携带 Authorization
```

因此，只要后续接口使用同一个 `UserApi` 对象，token 就会自动随请求发送。

## 七、需要理解的测试设计要点

- `BaseApi.raise_for_status()` 处理的是 HTTP 层面的 4xx/5xx；`msg_code` 是业务层状态码，需要测试代码自己断言。
- `UserApi.login()` 返回登录 JSON，同时把 token 写入 session，返回值和授权状态是两条并行结果。
- `clear_token()` 只清除本地 session 请求头，当前代码没有调用服务器端注销接口。
- 使用 `data=` 发送表单数据，和配置中的 `application/x-www-form-urlencoded` 请求头相匹配。

