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
        return day_type not in [1, 2]
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
    
    # 构造消息内容
    # 1. <@all> 放在最前面，确保提醒生效
    # 2. 链接使用 [🔥 点击此处直接提交巡检记录](链接) 的格式
    content = (
        "<@all>\n"
        "各位同学，快下班了，记得提交今天的巡检记录哦。\n"
        "Don't forget to submit the inspection record.\n\n"
        f"> [🔥 点击此处直接提交巡检记录]({FORM_URL.strip()})"
    )

    payload = {
        "msgtype": "markdown",
        "markdown": {
            "content": content
        }
    }

    try:
        response = requests.post(WEBHOOK_URL, headers=headers, data=json.dumps(payload))
        if response.status_code == 200:
            print("消息发送成功！")
        else:
            print(f"发送失败: {response.status_code}, {response.text}")
    except Exception as e:
        print(f"请求异常: {e}")

if __name__ == "__main__":
    send_wechat_remind()
