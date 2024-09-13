import os
import requests
import gradio as gr
from openai import OpenAI
from dotenv import load_dotenv

# 从环境变量读取大模型的api key
load_dotenv()
client = OpenAI(
    api_key=os.getenv('API_KEY_SPARKO'),
    base_url=os.getenv('URL_SPARK'), 
)

# news_from_select = ["哔哩哔哩","AcFun","微博","知乎","知乎日报","百度","抖音","豆瓣电影","豆瓣讨论小组","百度贴吧","少数派","IT之家","IT之家「喜加一」","简书","澎湃新闻","今日头条","36 氪","51CTO","CSDN","NodeSeek","稀土掘金","腾讯新闻","新浪网","新浪新闻","网易新闻","吾爱破解","全球主机交流","虎嗅","虎扑","爱范儿","英雄联盟","原神","崩坏3","崩坏：星穹铁道","微信读书","NGA","V2EX","HelloGitHub","中央气象台","中国地震台","历史上的今天"]
news_from_select = ["bilibili","acfun","weibo","zhihu","zhihu-daily","baidu","douyin","douban-movie","douban-group","tieba","sspai","ithome","ithome-xijiayi","jianshu","thepaper","toutiao","36kr","51cto","csdn","nodeseek","juejin","qq-news","sina","sina-news","netease-news","52pojie","hostloc","huxiu","hupu","ifanr","lol","genshin","honkai","starrail","weread","ngabbs","v2ex","hellogithub","weatheralarm","earthquake","history"]
your_field_select = ["体育", "健康", "游戏"]
topics = ["今日话题"]

# 设置交互获得输出
def fetch_news(news_from_dropdown, your_field_dropdown):
    # 发送请求并获取新闻
    api_url = "https://todayhot.ai4uo.com/"+ news_from_dropdown
    response = requests.get(api_url)
    data = response.json()['data']
    # 获取全部热点
    title_str = "；".join([item["title"] for item in data])
    # 定义提示词
    your_prompt = f"我会给你一些新闻标题，请你帮我找出和{your_field_dropdown}相关的标题：{title_str}。请直接回复相关标题，不要解释。标题间不要换行，以；分隔。"

    response = client.chat.completions.create(
        model="4.0Ultra",
        messages=[{ "role": "user", "content": your_prompt }],
        temperature=0.5,
        # max_tokens=50,
        # top_p=1,
        # frequency_penalty=0.5,
        # presence_penalty=0,
    )
    print(response.choices[0].message.content)
    #放进下拉框
    topic_found = response.choices[0].message.content.split("；")
    topic_set_dropdown = gr.Dropdown(choices=topic_found,label="选择一个话题")
    return topic_set_dropdown

def generate_content(topic):
    # 定义提示词
    your_prompt = f"请以{topic}为主题，创作300字左右的小红书文案。"

    try:
        response = client.chat.completions.create(
            model="4.0Ultra",
            messages=[{ "role": "user", "content": your_prompt }],
            temperature=0.5,
            # max_tokens=50,
            # top_p=1,
            # frequency_penalty=0.5,
            # presence_penalty=0,
        )
        answer = response.choices[0].message.content
    except Exception as e:
        answer = "censored by LLM"
        # 在这里处理异常，例如返回一个默认值或重新尝试操作
    return answer


def main():
    # 设置gradio界面

    with gr.Blocks(title = "追踪热点") as demo:
        description = "追踪各大平台热点新闻",
        gr.Markdown("请选择平台."
                    "请选择关注领域")
        with gr.Row():
            news_from_dropdown = gr.Dropdown(choices=news_from_select, label="热点平台")
            your_field_dropdown = gr.Dropdown(choices=your_field_select, label="你专注的领域")
            found_btn = gr.Button(value="确定")
        with gr.Row():
            topics_dropdown = gr.Dropdown(choices=topics, label="选择一个话题", allow_custom_value=True) 
            write_btn = gr.Button(value="创作")
        with gr.Row():
            article = gr.Textbox(label="小红书文案")

            found_btn.click(fetch_news, inputs=[news_from_dropdown, your_field_dropdown], outputs=topics_dropdown)
            write_btn.click(generate_content, inputs=topics_dropdown, outputs=article)

    # demo.launch(server_name='0.0.0.0', server_port=5006, auth=("admin", "123456"))
    demo.launch(server_name='127.0.0.1', server_port=5006)

if __name__ == "__main__":
    main()
