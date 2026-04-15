import os
import requests
import datetime
import json

# 从环境变量读取配置
WEBHOOK_URL = os.getenv('WECHAT_WEBHOOK_URL')
FORM_URL = os.getenv('FEISHU_DOC_URL')

def is_workday():
    """
    单稳定接口版工作日判断
    仅保留timor.tech主接口，移除无效的阿里云接口
    接口异常时默认按工作日发送，绝不漏提醒
    """
    try:
        today = datetime.datetime.now().strftime('%Y-%m-%d')
        # 仅保留稳定的timor.tech接口，移除无效域名
        response = requests.get(f"https://timor.tech/api/holiday/info/{today}", timeout=8)
        # 增加响应有效性校验，避免空数据解析失败
        if response.status_code == 200 and response.text.strip():
            data = response.json()
            day_type = data.get('type', {}).get('type', -1)
            print(f"[主接口] 今日类型: {day_type} (0=工作日,1=周末,2=节假日)")
            return day_type == 0
        else:
            print("[主接口] 响应无效，默认按工作日发送")
            return True
    except Exception as e:
        print(f"[主接口] 调用异常: {e}，默认按工作日发送")
        return True

def send_wechat_remind():
    # 工作日判断
    if not is_workday():
        print("今天非工作日 → 不发送提醒")
        return

    # 配置完整性校验
    if not WEBHOOK_URL:
        print("❌ 错误：未配置 WECHAT_WEBHOOK_URL 环境变量")
        return
    if not FORM_URL:
        print("❌ 错误：未配置 FEISHU_DOC_URL 环境变量")
        return

    # ==========================
    # 纯文本格式 + 中英双语 + 可点击链接 + @all
    # ==========================
    content = f"""各位同学，快下班了，记得提交今天的巡检记录哦。
Don't forget to submit the inspection record.

{FORM_URL.strip()}

<@all>"""

    # 纯文本text模式，@all100%生效
    payload = {
        "msgtype": "text",
        "text": {
            "content": content
        },
        "mentioned_list": ["@all"]
    }

    try:
        resp = requests.post(
            WEBHOOK_URL,
            headers={"Content-Type": "application/json"},
            data=json.dumps(payload, ensure_ascii=False)
        )
        result = resp.json()
        if result.get("errcode") == 0:
            print("✅ 消息发送成功，已@所有人")
        else:
            print(f"❌ 发送失败: {result}")
    except Exception as e:
        print(f"❌ 请求异常: {e}")

if __name__ == "__main__":
    send_wechat_remind()
