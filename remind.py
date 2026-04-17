import os
import requests
import datetime
import json

# ========== 完全匹配你 GitHub 里的密钥名 ==========
WEBHOOK_URL = os.getenv('WECHAT_WEBHOOK_URL')
FORM_URL = os.getenv('FEISHU_DOC_URL')

def is_workday():
    try:
        today = datetime.datetime.now().strftime('%Y-%m-%d')
        resp = requests.get(f"https://timor.tech/api/holiday/info/{today}", timeout=5)
        
        if resp.status_code == 200:
            try:
                data = resp.json()
                # type: 0=工作日 3=调休工作日 → 发送；1=周末 2=节假日 → 不发送
                day_type = data.get('type', {}).get('type')
                return day_type not in [1, 2]
            except json.JSONDecodeError:
                print("API返回格式异常，默认视为工作日以防漏发。")
                return True
        return True
    except Exception as e:
        print(f"检查节假日失败 ({e})，启用保底逻辑：视为工作日。")
        return True

def send_remind():
    if not is_workday():
        print("今日休息，不发送消息。")
        return

    if not WEBHOOK_URL:
        print("未检测到 Webhook URL，发送终止。")
        return

    content = (
        "各位同学，快下班了，记得提交今天的巡检记录哦。\n"
        "Don't forget to submit the inspection record.\n\n"
        f"填写链接：{FORM_URL.strip() if FORM_URL else ''}"
    )

    payload = {
        "msgtype": "text",
        "text": {
            "content": content,
            "mentioned_list": ["@all"]
        }
    }

    try:
        r = requests.post(WEBHOOK_URL, json=payload, timeout=10)
        print(f"发送结果: {r.status_code}, {r.text}")
    except Exception as e:
        print(f"发送失败: {e}")

if __name__ == "__main__":
    send_remind()

