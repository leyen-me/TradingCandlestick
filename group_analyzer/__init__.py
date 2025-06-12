# import schedule
import os
from datetime import datetime, timedelta
from config import DEFAULT_WATCHLIST_NAME
from longport.openapi import QuoteContext, Config, Period, AdjustType
from notifications import EmailNotifier
from openai import OpenAI

client = OpenAI(
        base_url='https://api-inference.modelscope.cn/v1/',
        api_key=os.getenv("MODELSCOPE_SDK_TOKEN"), # ModelScope Token
    )
EXTRA_BODY = {
    # enable thinking, set to False to disable
    "enable_thinking": False,
    # use thinking_budget to contorl num of tokens used for thinking
    # "thinking_budget": 4096
}
MODEL_ID = 'Qwen/Qwen3-235B-A22B'
STREAM = False

# 总结:
def summary(email_str):
    response = client.chat.completions.create(
        model=MODEL_ID,
        messages=[
            {
                'role': 'system',
                'content': """总结邮件中的内容，并整理成表格"""
            },
            {
                'role': 'user',
                'content': f"""{email_str}"""
            }
        ],
        stream=STREAM,
        extra_body=EXTRA_BODY
    )
    return response.choices[0].message.content
    

def ai_analysis(kline_data):
    response = client.chat.completions.create(
        model=MODEL_ID,
        messages=[
            {
                'role': 'system',
                'content': """你是一位价格行为分析师，擅长分析股票价格行为，请根据用户提供的日K数据，给出建议(买入、卖出、观望)，及其理由"""
            },
            {
                'role': 'user',
                'content': f"""{kline_data}"""
            }
        ],
        stream=STREAM,
        extra_body=EXTRA_BODY
    )
    return response.choices[0].message.content


def run():
    config = Config.from_env()
    ctx = QuoteContext(config)
    email_notifier = EmailNotifier()

    print(f"开始获取股票数据 - {datetime.now()}")
    resp = ctx.watchlist()
    email_str = ""
    
    for item in resp:
        if item.name == DEFAULT_WATCHLIST_NAME:
            for stock in item.securities:
                print(f"获取股票 {stock.symbol} 的数据")
                # 获取日K线数据
                try:
                    kline_data = ctx.history_candlesticks_by_offset(
                        stock.symbol, 
                        Period.Day, 
                        AdjustType.NoAdjust, 
                        True,
                        36,
                        datetime.now() - timedelta(days=36)
                    )
                    result = ai_analysis(kline_data)
                    print(result)
                    email_str += f"股票: {stock.symbol} 的建议: {result}\n"
                except Exception as e:
                    print(f"获取 {stock.symbol} 数据时出错: {str(e)}")
    
    # 总结
    summary_result = summary(email_str)
    email_notifier.send_email("股票池分析", summary_result)
    