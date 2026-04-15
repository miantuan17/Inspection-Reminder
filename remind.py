import os
import requests
import datetime
import json  # 修复：必须导入 json 库

# 从环境变量读取（这里的名字要和 main.yml 里的 env 对应）
WEBHOOK_URL = os.getenv('WECHAT_WEBHOOK_URL')
FEISHU_DOC_URL = os.getenv('FEISHU_DOC_URL')

def is_workday():
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
        print("错误: 未找到 WECHAT_WEBHOOK_URL 环境变量")
        return

    # 飞书跳转协议
    feishu_jump_url = f"feishu://applink/client/docs/open?url={FEISHU_DOC_URL}"

    headers = {"Content-Type": "application/json"}
    payload = {
        "msgtype": "markdown",
        "markdown": {
            "content": (
                f"### 📝 巡检文档填写提醒\n"
                f"各位同学，快下班了，请及时更新今日的巡检文档。\n\n"
                f"> [🔥 点击此处直接打开飞书文档]({feishu_jump_url})\n\n"
                f"<@all>"
            )
        }
    }

    try:
        # 注意：这里使用的是上面定义的 WEBHOOK_URL
        response = requests.post(WEBHOOK_URL, headers=headers, data=json.dumps(payload))
        if response.status_code == 200:
            print("提醒消息发送成功！")
        else:
            print(f"发送失败: {response.status_code}, {response.text}")
    except Exception as e:
        print(f"请求异常: {e}")

if __name__ == "__main__":
    send_wechat_remind()
