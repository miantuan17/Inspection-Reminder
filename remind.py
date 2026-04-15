import os
import requests
import datetime
import json

WEBHOOK_URL = os.getenv('WECHAT_WEBHOOK_URL')
FORM_URL = os.getenv('FEISHU_DOC_URL') 

def is_workday():
    try:
        today = datetime.datetime.now().strftime('%Y-%m-%d')
        response = requests.get(f"https://timor.tech/api/holiday/info/{today}", timeout=10)
        data = response.json()
        return data.get('type', {}).get('type') not in [1, 2]
    except:
        return True

def send_wechat_remind():
    if not is_workday(): return
    if not WEBHOOK_URL: return

    # 1. 净化链接，防止隐藏字符
    clean_url = FORM_URL.strip() if FORM_URL else ""

    # 2. 构造内容：注意 <@all> 后面直接接两个换行，绝对不加 > 符号
    content = (
        "<@all>\n\n"
        "各位同学，快下班了，记得提交今天的巡检记录哦。\n"
        "Don't forget to submit the inspection record.\n\n"
        f"> [🔥 点击此处直接提交巡检记录]({clean_url})"
    )

    headers = {"Content-Type": "application/json"}
    payload = {
        "msgtype": "markdown",
        "markdown": {
            "content": content
        }
    }

    try:
        requests.post(WEBHOOK_URL, headers=headers, data=json.dumps(payload), timeout=10)
        print("发送指令已发出")
    except Exception as e:
        print(f"报错了: {e}")

if __name__ == "__main__":
    send_wechat_remind()
