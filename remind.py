import os
import requests
import datetime
import json

WEBHOOK_URL = os.getenv('WECHAT_WEBHOOK_URL')
FORM_URL = os.getenv('FEISHU_DOC_URL')

def is_workday():
    """双接口兜底的工作日判断，彻底解决接口不稳定问题"""
    today = datetime.datetime.now().strftime('%Y-%m-%d')
    # 接口1：timor.tech（主接口）
    try:
        resp = requests.get(f"https://timor.tech/api/holiday/info/{today}", timeout=5)
        if resp.status_code == 200 and resp.text.strip():
            data = resp.json()
            day_type = data.get('type', {}).get('type', -1)
            print(f"[主接口] 今日类型: {day_type} (0=工作日,1=周末,2=节假日)")
            return day_type == 0
    except Exception as e:
        print(f"[主接口] 调用失败: {e}")

    # 接口2：阿里云节假日API（备用，更稳定）
    try:
        resp = requests.get(f"https://dayu.aliyun.com/api/holiday/getHoliday?date={today}", timeout=5)
        if resp.status_code == 200 and resp.text.strip():
            data = resp.json()
            is_holiday = data.get('data', {}).get('isHoliday', False)
            print(f"[备用接口] 是否节假日: {is_holiday}")
            return not is_holiday
    except Exception as e:
        print(f"[备用接口] 调用失败: {e}")

    # 双接口都失败，默认按工作日发送
    print("⚠️ 所有节假日接口异常，默认按工作日发送提醒")
    return True

def send_wechat_remind():
    if not is_workday():
        print("今天非工作日 → 不发送提醒")
        return

    if not WEBHOOK_URL:
        print("❌ 错误：未配置 WECHAT_WEBHOOK_URL 环境变量")
        return
    if not FORM_URL:
        print("❌ 错误：未配置 FEISHU_DOC_URL 环境变量")
        return

    headers = {"Content-Type": "application/json"}
    content = f"""各位同学，记得提交今天的巡检记录哦。
Don't forget to submit the inspection record.

[🔥 点击提交巡检记录]({FORM_URL.strip()})

<@all>"""

    payload = {
        "msgtype": "markdown",
        "markdown": {"content": content},
        "mentioned_list": ["@all"]
    }

    try:
        resp = requests.post(WEBHOOK_URL, headers=headers, data=json.dumps(payload, ensure_ascii=False))
        result = resp.json()
        if result.get("errcode") == 0:
            print("✅ 消息发送成功，已@所有人")
        else:
            print(f"❌ 发送失败: {result}")
    except Exception as e:
        print(f"❌ 请求异常: {e}")

if __name__ == "__main__":
    send_wechat_remind()
