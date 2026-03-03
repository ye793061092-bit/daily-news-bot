import streamlit as st
from duckduckgo_search import DDGS
import google.generativeai as genai
import datetime

# ================= 配置区 =================
try:
    GENAI_API_KEY = st.secrets["GENAI_API_KEY"]
except:
    st.error("请先在 Streamlit 后台设置 Secrets 里的 GENAI_API_KEY")
    st.stop()

genai.configure(api_key=GENAI_API_KEY)

# ================= 核心功能函数 =================

def get_news_links():
    """使用 DuckDuckGo 搜索最新新闻"""
    ddgs = DDGS()
    news_data = []
    
    try:
        # 1. 搜索美国/特朗普
        us_results = list(ddgs.news("Trump US politics", region="wt-wt", timelimit="d", max_results=5))
        news_data.extend([f"[美国] {r['title']} - {r['body']}" for r in us_results])

        # 2. 搜索欧洲
        eu_results = list(ddgs.news("Europe politics economy", region="wt-wt", timelimit="d", max_results=4))
        news_data.extend([f"[欧洲] {r['title']} - {r['body']}" for r in eu_results])

        # 3. 搜索全球
        world_results = list(ddgs.news("World breaking news", region="wt-wt", timelimit="d", max_results=4))
        news_data.extend([f"[全球] {r['title']} - {r['body']}" for r in world_results])
    except Exception as e:
        return f"搜索时网络波动: {e}"
    
    return "\n".join(news_data)

@st.cache_data(ttl=3600, show_spinner=False) 
def generate_news_report(_news_text):
    if not _news_text or len(_news_text) < 10: return "未找到足够的新闻数据。"
    
    # 🔥 核心修改：使用 gemini-1.5-flash
    # 因为我们在 requirements.txt 里强制升级了工具包，这个模型现在一定能用了！
    model = genai.GenerativeModel('gemini-1.5-flash')
    
    prompt = f"""
    请根据以下新闻原数据，整理一份中文简报。
    
    【新闻数据】：
    {_news_text}

    【要求】：
    1. 美国与特朗普 (3-5条)。
    2. 欧洲重点 (2-3条)。
    3. 全球要闻 (2-3条)。
    
    【格式】：
    * 标题加粗，后接核心摘要。
    * 使用简体中文。
    * 不要开场白。
    """
    
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"生成失败: {e}"

# ================= 网页界面 =================

st.set_page_config(page_title="全球热点", page_icon="🗞️")
st.title("🌍 每日全球舆情 (Flash版)")
st.caption(f"更新时间: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}")

if st.button("🚀 获取简报", type="primary", use_container_width=True):
    try:
        with st.status("正在运行...", expanded=True) as status:
            st.write("🔍 正在抓取新闻...")
            raw_news = get_news_links()
            
            st.write("🤖 正在生成摘要 (使用 Gemini 1.5 Flash)...")
            summary = generate_news_report(raw_news)
            
            status.update(label="✅ 完成", state="complete", expanded=False)
        
        st.markdown("---")
        st.markdown(summary)
        
    except Exception as e:
        st.error(f"出错: {e}")
