import streamlit as st
from duckduckgo_search import DDGS
import google.generativeai as genai
import datetime

# ================= 配置区 =================
# 填入您的 Gemini API Key (免费申请: https://aistudio.google.com/)
GENAI_API_KEY = "AIzaSyDs9dEAOMLOdob-aAK02ozJou8-F_rCw-8" 
genai.configure(api_key=GENAI_API_KEY)

# ================= 核心功能函数 =================

def get_news_links():
    """使用 DuckDuckGo 搜索最新新闻"""
    ddgs = DDGS()
    news_data = []
    
    # 1. 搜索特朗普和美国 (Trump US News)
    st.toast("正在搜索：美国与特朗普新闻...", icon="🇺🇸")
    us_results = list(ddgs.news("Trump US politics", region="wt-wt", timelimit="d", max_results=10))
    news_data.extend([f"[美国] {r['title']} - {r['body']}" for r in us_results])

    # 2. 搜索欧洲 (Europe News)
    st.toast("正在搜索：欧洲局势...", icon="🇪🇺")
    eu_results = list(ddgs.news("Europe politics economy", region="wt-wt", timelimit="d", max_results=8))
    news_data.extend([f"[欧洲] {r['title']} - {r['body']}" for r in eu_results])

    # 3. 搜索全球其他 (World News)
    st.toast("正在搜索：全球要闻...", icon="🌏")
    world_results = list(ddgs.news("World breaking news", region="wt-wt", timelimit="d", max_results=8))
    news_data.extend([f"[全球] {r['title']} - {r['body']}" for r in world_results])
    
    return "\n".join(news_data)

def summarize_with_ai(news_text):
    """调用 Gemini 进行筛选、总结和翻译"""
    model = genai.GenerativeModel('gemini-2.0-flash') # 使用最新的 Flash 模型，速度快
    
    prompt = f"""
    你是一名专业的国际舆情分析师。请根据以下抓取到的英文新闻原数据，整理一份中文简报。
    
    【新闻原数据】：
    {news_text}

    【严格执行以下输出要求】：
    1. **美国与特朗普 (3-5条)**：必须包含特朗普的最新动态/言论。
    2. **欧洲重点 (2-3条)**：英法德等国大事。
    3. **全球要闻 (2-3条)**：其他地区的关键冲突或事件。
    
    【格式要求】：
    * 标题加粗，后面紧跟一句话核心摘要。
    * 如果涉及舆情争议，用*斜体*标注关键观点。
    * 必须使用**简体中文**。
    * 不要任何开场白，直接输出 Markdown 格式的列表。
    """
    
    with st.spinner('AI 正在阅读并撰写简报（约需 10 秒）...'):
        response = model.generate_content(prompt)
    return response.text

# ================= 网页界面 (UI) =================

st.set_page_config(page_title="全球热点速递", page_icon="🗞️")

st.title("🌍 每日全球舆情 (AI版)")
st.caption(f"更新时间: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}")

if st.button("🚀 一键获取最新简报", type="primary", use_container_width=True):
    try:
        # 1. 获取原始数据
        raw_news = get_news_links()
        
        # 2. AI 处理
        summary = summarize_with_ai(raw_news)
        
        # 3. 展示结果
        st.markdown("---")
        st.markdown(summary)
        st.success("更新完毕！")
        
    except Exception as e:
        st.error(f"发生错误，请检查网络或 API Key：\n{e}")

else:

    st.info("👋 你好！点击上方按钮，AI 将为您实时抓取并总结全球新闻。")
