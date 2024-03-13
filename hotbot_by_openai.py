import os
import gradio as gr
import requests
from openai import OpenAI
from dotenv import load_dotenv

# 从环境变量读取openai的api key
load_dotenv()
client = OpenAI(
    # This is the default and can be omitted
    api_key=os.environ.get("OPENAI_API_KEY"),
)

# news_from_select = ["哔哩哔哩热门榜","微博热搜榜","知乎热榜","百度热搜榜","抖音热点榜","抖音热歌榜","豆瓣新片榜","豆瓣讨论小组讨论精选","百度贴吧热议榜","少数派热榜","IT 之家热榜","澎湃新闻热榜","今日头条热榜","36 氪热榜","稀土掘金热榜","腾讯新闻热点榜","网易新闻热点榜","英雄联盟更新公告","原神最新消息","微信读书飙升榜","快手热榜","网易云音乐排行榜","QQ音乐排行榜","NGA热帖","GithubTrending","V2EX热榜","历史上的今天指定日期"]
news_from_select = ["bilibili","weibo","zhihu","baidu","douyin","douyin_music","douban_new","douban_group","tieba","sspai","ithome","thepaper","toutiao","36kr","juejin","newsqq","netease","lol","genshin","weread","kuaishou","netease_music_toplist","qq_music_toplist","ngabbs","github","v2ex","calendar"]
your_field_select = ["体育", "健康", "游戏"]
topics = ["今日话题"]

# 设置交互获得输出
def find_news(news_from_dropdown, your_field_dropdown):
    # 发送请求并获取新闻
    api_url = "https://todayhot.ai4uo.com/"+ news_from_dropdown
    response = requests.get(api_url)
    data = response.json()['data']
    # 获取全部热点
    title_str = "；".join([item["title"] for item in data])
    # 定义提示词
    your_prompt = "我会给你一些新闻标题，请你帮我找出和" + your_field_dropdown + "相关的标题：" + title_str + "。请直接回复相关标题，不要解释。标题间不要换行，以；分隔。"
    
    # 调用openai的API
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{ "role": "user", "content": your_prompt }],
        temperature=0.5,
        max_tokens=50,
        top_p=1,
        frequency_penalty=0.5,
        presence_penalty=0,
    )
    print(response.choices[0].message.content)
    #放进下拉框
    topic_found = response.choices[0].message.content.split("；")
    topic_set_dropdown=gr.Dropdown(choices=topic_found,label="选择一个话题")
    return topic_set_dropdown

def generating(topic):
    # 定义提示词
    your_prompt = "请以" + topic + "为主题，创作100字左右的小红书文案。"
    # 调用openai的API
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{ "role": "user", "content": your_prompt }],
        temperature=0.5,
        max_tokens=50,
        top_p=1,
        frequency_penalty=0.5,
        presence_penalty=0,
    )
    return response.choices[0].message.content
# 设置gradio界面

with gr.Blocks(title = "追踪热点") as demo:
#    description = "追踪各大平台热点新闻",
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

        found_btn.click(find_news, inputs=[news_from_dropdown, your_field_dropdown], outputs=topics_dropdown)
        write_btn.click(generating, inputs=topics_dropdown, outputs=article)

demo.launch(server_name='0.0.0.0', server_port=5002, auth=("admin", "123456"))
