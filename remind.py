import os
import requests
import datetime

# 从 GitHub Secrets 中读取敏感信息
# 这样即使代码公开，别人也看不到你的 Webhook 地址和文档链接
WEBHOOK_URL = os.getenv('WECHAT_WEBHOOK_URL')
FEISHU_DOC_URL = os.getenv('FEISHU_DOC_URL')

def is_workday():
    """判断今天是否为法定工作日"""
    today = datetime.datetime.now().strftime('%Y-%m-%d')
    try:
        # 使用提摩节假日API (免费接口)
        response = requests.get(f"https://timor.tech/api/holiday/info/{today}")
        data = response.json()
        
        # type 0 是工作日，1 是周末，2 是节日，3 是调休
        # 只要不是 1 和 2，就是需要上班的日子
        if data['type']['type'] in [0, 3]:
            return True
        return False
    except Exception as e:
        print(f"检查节假日失败: {e}")
        # 如果接口失效，默认按周一到周五执行
        return datetime.datetime.now().weekday() < 5

def send_wechat_remind():
    if not is_workday():
        print("今天不是工作日，跳过提醒。")
        return

    headers = {"Content-Type": "application/json"}
    payload = {
        "msgtype": "text",
        "text": {
            "content": "📝 每日巡检提醒\n各位同学，快下班了，记得提交今天的巡检记录哦。Don't forget to submit the inspection record.\n链接：" + FEISHU_DOC_URL,
            "mentioned_list": ["@all"]
        }
    }
    
    response = requests.post(WECHAT_WEBHOOK_URL, headers=headers, data=json.dumps(payload))
    print(f"发送状态: {response.text}")

if __name__ == "__main__":
    send_wechat_remind()
