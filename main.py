from config import load_config
from gui import create_main_window

if __name__ == "__main__":
    email_account, password = load_config()
    if email_account and password:
        create_main_window(email_account, password)
