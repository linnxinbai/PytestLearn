import requests

base_url = "http://127.0.0.1:8787"
header = {'Content-Type':'application/x-www-form-urlencoded;charset=UTF-8'}
data = {
    "user_name":"test01",
    "passwd": "admin123"
}
url = "/dar/user/login"
response = requests.post(url=base_url+url,data=data,headers=header)
token = response.json()['token']
print(token)
