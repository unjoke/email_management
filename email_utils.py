import imaplib
import email
from email.header import decode_header
import chardet  # 用于自动检测编码
import re
import os


# 登录到 QQ 邮箱
def login_to_qq_email(email_account, password):
    try:
        mail = imaplib.IMAP4_SSL("imap.qq.com")
        mail.login(email_account, password)
        return mail
    except Exception as e:
        print(f"登录失败: {e}")
        return None


# 获取未读邮件列表
def get_unread_email_list(mail):
    mail.select("inbox")  # 选择收件箱
    status, messages = mail.search(None, "UNSEEN")  # 获取未读邮件
    email_ids = messages[0].split()
    return email_ids


# 自动检测并解码邮件内容
def decode_body(body_bytes, encoding=None):
    if encoding and encoding.lower() == 'unknown-8bit':
        try:
            body = body_bytes.decode('latin1')  # 尝试使用 latin1 解码
        except Exception as e:
            body = body_bytes.decode('utf-8', errors='ignore')  # 如果失败，忽略错误
    else:
        result = chardet.detect(body_bytes)  # 使用 chardet 检测编码
        encoding = result['encoding']
        try:
            body = body_bytes.decode(encoding)  # 使用检测到的编码解码
        except (UnicodeDecodeError, TypeError) as e:
            body = body_bytes.decode('utf-8', errors='ignore')  # 如果解码失败，忽略错误并继续
    return body


# 解码发件人
def decode_sender(sender):
    decoded_sender, encoding = decode_header(sender)[0]
    if isinstance(decoded_sender, bytes):
        try:
            decoded_sender = decoded_sender.decode(encoding or 'utf-8')
        except (UnicodeDecodeError, TypeError) as e:
            decoded_sender = decoded_sender.decode('utf-8', errors='ignore')
    return decoded_sender


# 获取邮件详情（标题、发件人、正文）
def get_email_details(mail, email_id):
    status, msg_data = mail.fetch(email_id, "(RFC822)")
    for response_part in msg_data:
        if isinstance(response_part, tuple):
            msg = email.message_from_bytes(response_part[1])
            subject, encoding = decode_header(msg["Subject"])[0]

            try:
                if isinstance(subject, bytes):
                    subject = subject.decode(encoding or "utf-8")
            except (LookupError, UnicodeDecodeError) as e:
                print(f"解码标题失败，使用 utf-8 回退解码: {e}")
                subject = subject.decode('utf-8', errors='ignore')

            from_ = decode_sender(msg.get("From"))
            body = ""
            has_attachments = False  # 默认没有附件
            content_transfer_encoding = msg.get("Content-Transfer-Encoding")
            if msg.is_multipart():
                for part in msg.walk():
                    if part.get_content_type() == "text/plain":
                        body_bytes = part.get_payload(decode=True)
                        body = decode_body(body_bytes, content_transfer_encoding)
                    content_disposition = str(part.get("Content-Disposition"))
                    if "attachment" in content_disposition:
                        has_attachments = True
            else:
                body_bytes = msg.get_payload(decode=True)
                body = decode_body(body_bytes, content_transfer_encoding)  # 解码邮件正文
            return subject, from_, body, msg, has_attachments
    return None, None, None, None, False


# 根据标题判断邮件是否重要
def classify_email_by_title(subject):
    important_keywords = ['紧急', '重要', '通知', '马上', '立即', '重要事项']
    subject = subject.lower()  # 将标题转为小写，方便匹配
    for keyword in important_keywords:
        if keyword.lower() in subject:
            return "重要"
    return "不重要"


# 解码附件的文件名
def decode_attachment_filename(filename):
    decoded_filename, encoding = decode_header(filename)[0]
    if isinstance(decoded_filename, bytes):
        decoded_filename = decoded_filename.decode(encoding or 'utf-8')
    return decoded_filename


# 下载附件
def download_attachments(msg, email_subject, email_from):
    download_dir = "attachments"
    if not os.path.exists(download_dir):
        os.makedirs(download_dir)

    for part in msg.walk():
        content_disposition = str(part.get("Content-Disposition"))
        if "attachment" in content_disposition:
            filename = part.get_filename()

            if filename:
                decoded_filename = decode_attachment_filename(filename)

                decoded_filename = re.sub(r'[<>:"/\\|?*]', '_', decoded_filename)

                safe_email_subject = re.sub(r'[<>:"/\\|?*]', '_', email_subject)
                safe_email_from = re.sub(r'[<>:"/\\|?*]', '_', email_from)
                new_filename = f"[{safe_email_subject}]_{safe_email_from}_{decoded_filename}"

                filepath = os.path.join(download_dir, new_filename)

                try:
                    with open(filepath, "wb") as f:
                        f.write(part.get_payload(decode=True))
                    print(f"附件 {new_filename} 已下载到 {download_dir}")
                except OSError as e:
                    print(f"无法保存附件 {new_filename}: {e}")
