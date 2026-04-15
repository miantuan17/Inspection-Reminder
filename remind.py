import os
import requests
import datetime
import json

WEBHOOK_URL = os.getenv('WECHAT_WEBHOOK_URL')
FORM_URL = os.getenv('FEISHU_DOC_URL')

def is_workday():
    try:
        today = datetime.datetime.now().strftime('%Y-%m-%d')
        response = requests.get(f"https://timor.tech/api/holiday/info/{today}", timeout=8)
        data = response.json()
        day_type = data.get('type', {}).get('type')
        return day_type == 0
    except:
        return True

def send_wechat_remind():
    if not is_workday():
        print("非工作日，不发送")
        return

    # 纯文本内容（里面 绝对不要写 <@all>！！！）
    content = f"""各位同学，快下班了，记得提交今天的巡检记录哦。
Don't forget to submit the inspection record.

{FORM_URL.strip()}"""

    # --------------------------
    # 企业微信 官方最终正确格式
    # 全世界唯一 100% 生效 @all 写法
    # --------------------------
    payload = {
        "msgtype": "text",
        "text": {
            "content": content,
            "mentioned_list": ["@all"]
        }
    }

    try:
        resp = requests.post(
            WEBHOOK_URL,
            json=payload
        )
        result = resp.json()
        if result.get("errcode") == 0:
            print("✅ 发送成功 → @all 已强制生效")
        else:
            print("❌ 发送失败：", result)
    except Exception as e:
        print("异常：", e)

if __name__ == "__main__":
    send_wechat_remind()
