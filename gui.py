import tkinter as tk
from tkinter import messagebox
from email_utils import *
from config import load_config


# 显示邮件详情的弹窗
def show_email_details(email_subject, email_from, email_body, has_attachments):
    detail_window = tk.Toplevel()
    detail_window.title("邮件详情")

    # 设置窗口样式
    detail_window.config(bg="#f0f0f0")

    # 创建文本框显示邮件正文，允许复制
    text_box = tk.Text(detail_window, wrap=tk.WORD, height=20, width=80, font=("Arial", 12), bg="#ffffff", fg="#333333")
    text_box.insert(tk.END, email_body)
    text_box.config(state=tk.DISABLED)  # 设置为只读
    text_box.pack(pady=10)

    tk.Label(detail_window, text="标题: " + email_subject, font=("Arial", 14, "bold"), bg="#f0f0f0").pack(pady=5)
    tk.Label(detail_window, text="发件人: " + email_from, font=("Arial", 12), bg="#f0f0f0").pack(pady=5)

    if has_attachments:
        tk.Label(detail_window, text="该邮件有附件。", font=("Arial", 12), bg="#f0f0f0", fg="red").pack(pady=5)
    else:
        tk.Label(detail_window, text="该邮件没有附件。", font=("Arial", 12), bg="#f0f0f0", fg="green").pack(pady=5)


# 创建主窗口
def create_main_window(email_account, password):
    root = tk.Tk()
    root.title("QQ邮箱邮件")

    # 设置窗口大小和样式
    root.geometry("800x600")
    root.config(bg="#f0f0f0")

    # 登录邮箱
    mail = login_to_qq_email(email_account, password)
    if not mail:
        messagebox.showerror("错误", "登录失败，请检查邮箱账号和密码")
        return

    email_listbox = tk.Listbox(root, font=("Arial", 12), bg="#ffffff", fg="#333333", selectmode=tk.SINGLE)
    email_listbox.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    # 填充未读邮件列表
    def populate_email_list(important_only=False):
        email_listbox.delete(0, tk.END)
        email_ids = get_unread_email_list(mail)
        important_emails = []
        non_important_emails = []

        for email_id in email_ids:
            subject, from_, body, msg, has_attachments = get_email_details(mail, email_id)
            category = classify_email_by_title(subject)

            email_info = f"{subject} - {from_} ({category})"
            if has_attachments:
                email_info += " [有附件]"
            else:
                email_info += " [无附件]"

            if category == "重要":
                important_emails.append(email_info)
            else:
                non_important_emails.append(email_info)

        if important_only:
            for email_info in important_emails:
                email_listbox.insert(tk.END, email_info)
        else:
            for email_info in important_emails:
                email_listbox.insert(tk.END, email_info)
            for email_info in non_important_emails:
                email_listbox.insert(tk.END, email_info)

    # 邮件点击事件
    def on_email_select(event):
        selected_index = email_listbox.curselection()
        if selected_index:
            email_id = get_unread_email_list(mail)[selected_index[0]]
            subject, from_, body, msg, has_attachments = get_email_details(mail, email_id)
            show_email_details(subject, from_, body, has_attachments)

    email_listbox.bind("<Double-1>", on_email_select)

    # 下载附件按钮
    def download_attachment():
        selected_index = email_listbox.curselection()
        if selected_index:
            email_id = get_unread_email_list(mail)[selected_index[0]]
            subject, from_, body, msg, has_attachments = get_email_details(mail, email_id)
            if has_attachments:
                download_attachments(msg, subject, from_)
                messagebox.showinfo("下载附件", "附件已下载!")
            else:
                messagebox.showinfo("没有附件", "该邮件没有附件")

    download_button = tk.Button(root, text="下载附件", command=download_attachment, font=("Arial", 14),
                                bg="#4CAF50", fg="white", relief="raised", padx=10, pady=5)
    download_button.pack(pady=20)

    # 刷新邮件列表
    refresh_button = tk.Button(root, text="刷新邮件", command=populate_email_list, font=("Arial", 14),
                                bg="#2196F3", fg="white", relief="raised", padx=10, pady=5)
    refresh_button.pack(pady=10)

    # 重要邮件按钮
    important_button = tk.Button(root, text="显示重要邮件", command=lambda: populate_email_list(important_only=True),
                                 font=("Arial", 14), bg="#FF5722", fg="white", relief="raised", padx=10, pady=5)
    important_button.pack(pady=10)

    # 不重要邮件按钮
    non_important_button = tk.Button(root, text="显示所有邮件", command=lambda: populate_email_list(important_only=False),
                                     font=("Arial", 14), bg="#607D8B", fg="white", relief="raised", padx=10, pady=5)
    non_important_button.pack(pady=10)

    populate_email_list()
    root.mainloop()
