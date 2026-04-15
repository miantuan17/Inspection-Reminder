import os
import requests
import datetime
import json

# 直接引用你 Secrets 里的变量名
WEBHOOK_URL = os.getenv('WECHAT_WEBHOOK_URL')
FORM_URL = os.getenv('FEISHU_DOC_URL')

def is_workday():
    """
    终极优化的节假日逻辑：
    - 增加 5 秒请求超时
    - 增加完整的 JSON 解析保护
    - 异常保底：接口挂了也返回 True，确保工作日不漏发
    """
    try:
        today = datetime.datetime.now().strftime('%Y-%m-%d')
        # 接口来源：提摩科技节假日 API
        resp = requests.get(f"https://timor.tech/api/holiday/info/{today}", timeout=5)
        
        if resp.status_code == 200:
            data = resp.json()
            # type: 0工作日, 3调休加班 (需发送) | 1周末, 2节假日 (不发送)
            day_type = data.get('type', {}).get('type')
            return day_type not in [1, 2]
        
        return True # 接口返回非 200 时，默认是工作日
    except Exception as e:
        print(f"节假日检查异常 ({e})，启用保底机制：照常发送。")
        return True

def send_remind():
    # 1. 节假日拦截
    if not is_workday():
        print("今日非工作日，脚本结束。")
        return

    # 2. 检查配置
    if not WEBHOOK_URL:
        print("错误: GitHub Secrets 中未找到 WECHAT_WEBHOOK_URL")
        return

    # 3. 构造消息（纯文本模式 + 官方参数化艾特）
    clean_url = FORM_URL.strip() if FORM_URL else "未配置链接"
    msg_content = (
        "各位同学，快下班了，记得提交今天的巡检记录哦。\n"
        "Don't forget to submit the inspection record.\n\n"
        f"填写链接：{clean_url}"
    )

    payload = {
        "msgtype": "text",
        "text": {
            "content": msg_content,
            "mentioned_list": ["@all"]  # 强提醒艾特所有人
        }
    }

    # 4. 执行发送
    try:
        headers = {"Content-Type": "application/json"}
        # 使用 json=payload 会自动处理 Python 字典到 JSON 字符串的转换
        response = requests.post(WEBHOOK_URL, json=payload, headers=headers, timeout=10)
        print(f"发送状态: {response.status_code}, 响应: {response.text}")
    except Exception as e:
        print(f"发送过程中出现异常: {e}")

if __name__ == "__main__":
    send_remind()
