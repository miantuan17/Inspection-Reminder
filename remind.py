import os
import requests
import datetime
import json

# 从环境变量读取（确保和你 GitHub Secrets 里的名字一致）
WEBHOOK_URL = os.getenv('WECHAT_WEBHOOK_URL')
FORM_URL = os.getenv('FEISHU_DOC_URL')

def is_workday():
    """
    带容错的节假日逻辑：
    - type: 0工作日, 3调休 (发送)
    - type: 1周末, 2节假日 (不发送)
    - 任何异常情况下默认返回 True (确保不漏发)
    """
    try:
        # 获取当天日期
        today = datetime.datetime.now().strftime('%Y-%m-%d')
        # 增加 5 秒超时，防止 API 响应慢导致任务卡死
        response = requests.get(f"https://timor.tech/api/holiday/info/{today}", timeout=5)
        
        # 只有当接口返回 200 时才尝试解析
        if response.status_code == 200:
            try:
                data = response.json()
                day_type = data.get('type', {}).get('type')
                # 只有明确是周末或法定节假日时，才返回 False
                if day_type in [1, 2]:
                    return False
            except Exception as e:
                print(f"JSON解析失败: {e}，将默认视为工作日。")
        else:
            print(f"接口状态码异常: {response.status_code}，将默认视为工作日。")
            
    except Exception as e:
        # 捕获所有网络异常、超时等
        print(f"节假日接口请求异常: {e}，为保险起见，默认今天需要提醒。")
    
    return True

def send_remind():
    # 1. 节假日拦截逻辑
    if not is_workday():
        print("检测到今日为休息日，脚本安全退出。")
        return

    # 2. 检查 Webhook 配置
    if not WEBHOOK_URL:
        print("错误: 未配置 WECHAT_WEBHOOK_URL")
        return

    # 3. 构造通知内容
    clean_url = FORM_URL.strip() if FORM_URL else "未配置链接"
    msg_content = (
        "各位同学，快下班了，记得提交今天的巡检记录哦。\n"
        "Don't forget to submit the inspection record.\n\n"
        f"填写链接：{clean_url}"
    )

    # 4. 采用 Text 模式，确保 @所有人 100% 成功
    payload = {
        "msgtype": "text",
        "text": {
            "content": msg_content,
            "mentioned_list": ["@all"]
        }
    }

    try:
        headers = {"Content-Type": "application/json"}
        r = requests.post(WEBHOOK_URL, json=payload, headers=headers, timeout=10)
        print(f"发送结果: {r.status_code}, {r.text}")
    except Exception as e:
        print(f"发送请求出现错误: {e}")

if __name__ == "__main__":
    send_remind()

