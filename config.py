import json

# 从 config.json 文件中读取配置
def load_config():
    try:
        with open("config.json", "r") as config_file:
            config = json.load(config_file)
            return config["email_account"], config["password"]
    except Exception as e:
        print(f"读取配置文件失败: {e}")
        return None, None
