import requests

# 主账号 API Key
MASTER_API_KEY = "OieAIhJx9zGMGgBgCSvl2SS6NCaOyCYQKJ0oCymc1EE"


def create_printnode_subaccount(firstname, lastname, email, password):
    url = "https://api.printnode.com/account"
    headers = {"Content-Type": "application/json"}
    auth = (MASTER_API_KEY, "")
    payload = {
        "firstname": firstname,
        "lastname": lastname,
        "email": email,
        "password": password,
        "termsOfService": "yes"
    }

    print(f"📤 正在创建子账户: {email}")
    response = requests.post(url, json=payload, auth=auth, headers=headers)

    if response.status_code == 201:
        print("✅ 子账户创建成功！")

        # 登录获取 API Key
        print("🔐 正在获取 API Key...")
        auth_response = requests.get("https://api.printnode.com/account",
                                     auth=(email, password))
        if auth_response.status_code == 200:
            api_key = auth_response.json().get("apiKey", None)
            if api_key:
                print(f"✅ API Key: {api_key}")
                return api_key
            else:
                print("⚠️ 子账户创建成功，但未能获取 API Key")
        else:
            print(
                f"❌ 获取 API Key 失败: {auth_response.status_code} {auth_response.text}"
            )
    else:
        print(f"❌ 子账户创建失败: {response.status_code} {response.text}")

    return None


# 示例调用（替换为你要注册的客户信息）
if __name__ == "__main__":
    create_printnode_subaccount(firstname="Zhou",
                                lastname="Customer",
                                email="haroldzhou95@gmail.com",
                                password="letsee")
