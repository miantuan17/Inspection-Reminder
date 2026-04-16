import os
import requests
import json

# 1. 从 GitHub Secrets 读取变量
WEBHOOK_URL = os.getenv('WECHAT_WEBHOOK_URL')
FORM_URL = os.getenv('FEISHU_DOC_URL')

def send_remind():
    # 检查 Webhook 地址是否存在
    if not WEBHOOK_URL:
        print("错误: 未找到 WECHAT_WEBHOOK_URL，请检查 GitHub Secrets 配置。")
        return

    # 2. 构造通知内容 (保持原样)
    clean_url = FORM_URL.strip() if FORM_URL else "未配置链接"
    msg_content = (
        "各位同学，快下班了，记得提交今天的巡检记录哦。\n"
        "Don't forget to submit the inspection record.\n\n"
        f"填写链接：{clean_url}"
    )

    # 3. 构造纯文本 Payload，确保 @所有人 100% 成功
    payload = {
        "msgtype": "text",
        "text": {
            "content": msg_content,
            "mentioned_list": ["@all"]  # 强提醒艾特
        }
    }

    # 4. 执行发送
    try:
        headers = {"Content-Type": "application/json"}
        response = requests.post(
            WEBHOOK_URL, 
            json=payload, 
            headers=headers, 
            timeout=10
        )
        if response.status_code == 200:
            print("消息发送指令已成功发出！")
        else:
            print(f"发送失败，状态码: {response.status_code}, 详情: {response.text}")
    except Exception as e:
        print(f"网络异常: {e}")

if __name__ == "__main__":
    send_remind()
