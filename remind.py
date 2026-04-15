import os
import requests
import datetime
import json

# 从环境变量读取
WEBHOOK_URL = os.getenv('WECHAT_WEBHOOK_URL')
FORM_URL = os.getenv('FEISHU_DOC_URL')

def is_workday():
    """检查今天是否为工作日"""
    try:
        today = datetime.datetime.now().strftime('%Y-%m-%d')
        response = requests.get(f"https://timor.tech/api/holiday/info/{today}", timeout=10)
        data = response.json()
        day_type = data.get('type', {}).get('type')
        return day_type == 0  # 0=工作日
    except Exception as e:
        print(f"检查节假日失败: {e}")
        return True

def send_wechat_remind():
    if not is_workday():
        print("今天非工作日，不发送提醒。")
        return

    if not WEBHOOK_URL:
        print("错误: 未找到 WEBHOOK 环境变量")
        return

    headers = {"Content-Type": "application/json"}

    # 关键：@all 必须单独一行，不能放在 > 引用块里
    content = f"""各位同学，快下班了，记得提交今天的巡检记录哦。
Don't forget to submit the inspection record.

[🔥 点击此处直接提交巡检记录]({FORM_URL.strip()})

<@all>"""

    payload = {
        "msgtype": "markdown",
        "markdown": {
            "content": content,
            "mentioned_list": ["@all"]  # 强制艾特所有人
        }
    }

    try:
        response = requests.post(WEBHOOK_URL, headers=headers, data=json.dumps(payload, ensure_ascii=False))
        result = response.json()
        if result.get("errcode") == 0:
            print("消息发送成功！@all 已生效")
        else:
            print(f"发送失败: {result}")
    except Exception as e:
        print(f"请求异常: {e}")

if __name__ == "__main__":
    send_wechat_remind()
