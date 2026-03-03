import streamlit as st
from duckduckgo_search import DDGS
import google.generativeai as genai
import datetime

# ================= 配置区 =================
# 从 Secrets 安全读取 Key
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
    
    # 搜索词优化，增加容错
    try:
        us_results = list(ddgs.news("Trump US politics", region="wt-wt", timelimit="d", max_results=5))
        news_data.extend([f"[美国] {r['title']} - {r['body']}" for r in us_results])

        eu_results = list(ddgs.news("Europe politics economy", region="wt-wt", timelimit="d", max_results=5))
        news_data.extend([f"[欧洲] {r['title']} - {r['body']}" for r in eu_results])

        world_results = list(ddgs.news("World breaking news", region="wt-wt", timelimit="d", max_results=5))
        news_data.extend([f"[全球] {r['title']} - {r['body']}" for r in world_results])
    except Exception as e:
        return f"搜索新闻源时出现网络波动: {e}"
    
    return "\n".join(news_data)

# 🔥 重点修改：增加了 @st.cache_data 装饰器
# ttl=3600 表示：这份简报生成后，1小时(3600秒)内如果再有人点，直接显示旧的，不消耗您的 API 额度！
@st.cache_data(ttl=3600, show_spinner=False) 
def generate_news_report(_news_text):
    """调用 Gemini 进行总结"""
    if not _news_text: return "未找到足够的新闻数据。"
    
    model = genai.GenerativeModel('gemini-1.5-flash')
    
    prompt = f"""
    你是一名专业的国际舆情分析师。请根据以下抓取到的英文新闻原数据，整理一份中文简报。
    
    【新闻原数据】：
    {_news_text}

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
    
    response = model.generate_content(prompt)
    return response.text

# ================= 网页界面 (UI) =================

st.set_page_config(page_title="全球热点速递", page_icon="🗞️")

st.title("🌍 每日全球舆情 (AI版)")
st.caption(f"当前时间: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}")

if st.button("🚀 一键获取最新简报", type="primary", use_container_width=True):
    try:
        with st.status("正在通过 AI 联网分析...", expanded=True) as status:
            st.write("🔍 正在抓取全球新闻源...")
            raw_news = get_news_links()
            
            st.write("🤖 AI 正在阅读并撰写简报...")
            summary = generate_news_report(raw_news)
            
            status.update(label="✅ 简报已生成", state="complete", expanded=False)
        
        st.markdown("---")
        st.markdown(summary)
        
    except Exception as e:
        st.error(f"发生错误（可能是请求太快，请等1分钟再试）：\n{e}")

else:
    st.info("👋 点击上方按钮，AI 将为您总结全球新闻。(每小时自动更新一次)")

