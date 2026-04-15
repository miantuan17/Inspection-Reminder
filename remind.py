import os
import requests
import datetime
import json

# 从环境变量读取
WEBHOOK_URL = os.getenv('WECHAT_WEBHOOK_URL')
FORM_URL = os.getenv('FEISHU_DOC_URL')

def is_workday():
    """优化后的节假日逻辑：增加错误拦截与保底机制"""
    try:
        # 获取北京时间日期
        today = datetime.datetime.now().strftime('%Y-%m-%d')
        # 增加 5 秒超时，防止接口卡死
        response = requests.get(f"https://timor.tech/api/holiday/info/{today}", timeout=5)
        
        # 只有当接口返回 200 且内容是 JSON 时才解析
        if response.status_code == 200:
            try:
                data = response.json()
                # type: 0工作日, 3调休加班 (这两者都需要发送)
                # type: 1周末, 2节假日 (这两者跳过)
                day_type = data.get('type', {}).get('type')
                return day_type not in [1, 2]
            except json.JSONDecodeError:
                print("接口返回了非 JSON 格式，执行保底逻辑（视为工作日）。")
                return True
        else:
            print(f"接口状态异常(Code: {response.status_code})，执行保底逻辑。")
            return True
            
    except Exception as e:
        # 捕获网络超时、连接失败等所有异常
        print(f"节假日检查异常: {e}，为防止漏报，默认今天为工作日。")
        return True

def send_wechat_remind():
    # 1. 检查是否需要发送
    if not is_workday():
        print("今日为法定节假日或周末，不发送提醒。")
        return

    if not WEBHOOK_URL:
        print("错误: 未找到 WECHAT_WEBHOOK_URL")
        return

    # 2. 构造纯文本消息
    # 放弃 Markdown，改用 text 模式以确保艾特 100% 生效
    content = (
        "各位同学，快下班了，记得提交今天的巡检记录哦。\n"
        "Don't forget to submit the inspection record.\n\n"
        f"填写链接：{FORM_URL.strip() if FORM_URL else ''}"
    )

    payload = {
        "msgtype": "text",
        "text": {
            "content": content,
            "mentioned_list": ["@all"]  # 官方参数，text 模式下最稳
        }
    }

    try:
        headers = {"Content-Type": "application/json"}
        response = requests.post(
            WEBHOOK_URL, 
            data=json.dumps(payload), 
            headers=headers, 
            timeout=10
        )
        if response.status_code == 200:
            print("提醒消息发送成功！")
        else:
            print(f"发送失败: {response.status_code}, {response.text}")
    except Exception as e:
        print(f"网络请求出错: {e}")

if __name__ == "__main__":
    send_wechat_remind()
