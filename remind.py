import os
import requests
import datetime
import json

# 直接引用你 Secrets 里的变量名
WEBHOOK_URL = os.getenv('WECHAT_WEBHOOK_URL')
FORM_URL = os.getenv('FEISHU_DOC_URL')

def is_workday():
    """终极优化节假日逻辑，彻底解决 image_ec1ae7 中的解析报错问题"""
    try:
        today = datetime.datetime.now().strftime('%Y-%m-%d')
        # 增加超时控制
        resp = requests.get(f"https://timor.tech/api/holiday/info/{today}", timeout=5)
        
        # 只有状态码为 200 才尝试解析 JSON
        if resp.status_code == 200:
            try:
                data = resp.json()
                # type: 0工作日, 3调休 (需要发送) | 1周末, 2节假日 (不发送)
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
        print("未检测到 Webhook URL")
        return

    # 按照你的要求：保留原内容，使用 text 模式确保艾特 100% 成功
    content = (
        "各位同学，快下班了，记得提交今天的巡检记录哦。\n"
        "Don't forget to submit the inspection record.\n\n"
        f"填写链接：{FORM_URL.strip() if FORM_URL else ''}"
    )

    payload = {
        "msgtype": "text",
        "text": {
            "content": content,
            "mentioned_list": ["@all"] # 强提醒所有人
        }
    }

    try:
        # 使用 json= 参数会自动设置 content-type 为 application/json
        r = requests.post(WEBHOOK_URL, json=payload, timeout=10)
        print(f"发送结果: {r.status_code}, {r.text}")
    except Exception as e:
        print(f"发送失败: {e}")

if __name__ == "__main__":
    send_remind()
