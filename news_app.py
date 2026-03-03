import streamlit as st
from duckduckgo_search import DDGS
import datetime

# ================= 核心功能 =================

def get_news_and_summarize():
    """双保险模式：优先AI总结，失败则显示原新闻"""
    ddgs = DDGS()
    
    # 1. 抓取新闻链接
    status_placeholder = st.empty()
    status_placeholder.write("🔍 正在抓取全球新闻源...")
    
    raw_context = ""
    try:
        queries = [
            ("🇺🇸 美国与特朗普", "Trump US politics breaking news"),
            ("🇪🇺 欧洲局势", "Europe politics economy news"),
            ("🌏 全球要闻", "World international breaking news")
        ]
        
        for category, query in queries:
            # 搜索新闻
            results = list(ddgs.news(query, region="wt-wt", timelimit="d", max_results=3))
            if results:
                raw_context += f"### {category}\n"
                for r in results:
                    # 记录原始数据备用
                    raw_context += f"* [{r['title']}]({r['url']})\n"
                    # 这里的 body 用于给 AI 读
                    raw_context += f"  > 摘要: {r['body']}\n\n"
    
    except Exception as e:
        return f"⚠️ 网络抓取失败: {e}"

    if not raw_context:
        return "⚠️ 未搜索到有效新闻，请稍后重试。"

    # 2. 尝试调用 AI
    status_placeholder.write("🤖 正在调用 GPT-4o mini 进行分析...")
    
    try:
        # 使用 DuckDuckGo 的 AI (免费模型)
        prompt = f"""
        你是一名中文新闻编辑。请将以下抓取到的英文新闻资讯，整理成一份简报。
        
        【原始数据】：
        {raw_context}

        【输出要求】：
        1. 分为“美国/特朗普”、“欧洲”、“全球”三个板块。
        2. 标题加粗，下面跟一句中文简要说明。
        3. 只要干货，不要开场白。
        """
        
        # 这一步需要 duckduckgo-search>=6.3.0 版本
        response = ddgs.chat(prompt, model='gpt-4o-mini')
        status_placeholder.empty() # 清除状态文字
        return response
        
    except Exception as e:
        # 🔥【双保险机制】如果 AI 失败了，直接展示刚才抓到的原始新闻
        status_placeholder.empty()
        return f"""
        **⚠️ AI 暂时繁忙（无免费额度），已为您切换到【直读模式】：**
        
        ---
        {raw_context}
        
        *(错误信息: {e})*
        """

# ================= 网页界面 =================

st.set_page_config(page_title="全球热点", page_icon="🌍")
st.title("🌍 每日全球舆情 (无锁版)")
st.caption(f"更新时间: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}")

if st.button("🚀 获取简报", type="primary", use_container_width=True):
    with st.spinner('正在连接美国节点...'):
        summary = get_news_and_summarize()
        
    st.markdown("---")
    st.markdown(summary)
