import streamlit as st
from duckduckgo_search import DDGS
import datetime

# ================= 核心功能 =================

def get_news_and_summarize():
    """使用 DuckDuckGo 搜索并直接调用其 AI 进行总结"""
    ddgs = DDGS()
    
    # 1. 抓取新闻链接
    news_items = []
    status_text = ""
    
    try:
        # 搜索策略：分板块搜索
        queries = [
            ("美国与特朗普", "Trump US politics breaking news"),
            ("欧洲局势", "Europe politics economy news"),
            ("全球要闻", "World international breaking news")
        ]
        
        raw_context = ""
        for category, query in queries:
            results = list(ddgs.news(query, region="wt-wt", timelimit="d", max_results=4))
            for r in results:
                raw_context += f"[{category}] {r['title']}: {r['body']}\n"
        
        if not raw_context:
            return "⚠️ 未搜索到有效新闻，请稍后重试。"

        # 2. 直接使用 DuckDuckGo 的 AI (GPT-4o mini) 进行总结
        # 这一步不需要 Key，完全免费
        prompt = f"""
        请扮演专业的中文舆情分析师。基于以下抓取到的英文新闻摘要，写一份简报。
        
        【原始数据】：
        {raw_context}

        【输出要求】：
        1. **美国与特朗普 (3-5条)**：关注特朗普最新动态。
        2. **欧洲重点 (2-3条)**。
        3. **全球要闻 (2-3条)**。
        
        【格式】：
        * 使用Markdown列表。
        * 标题加粗，后接一句话摘要（中文）。
        * 只要干货，不要开场白。
        """
        
        # 调用 chat 接口 (model='gpt-4o-mini')
        response = ddgs.chat(prompt, model='gpt-4o-mini')
        return response

    except Exception as e:
        return f"运行出错: {e}"

# ================= 网页界面 =================

st.set_page_config(page_title="全球热点(免Key版)", page_icon="🌍")
st.title("🌍 每日全球舆情 (无锁直连)")
st.caption(f"更新时间: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}")

if st.button("🚀 获取简报", type="primary", use_container_width=True):
    with st.status("正在通过美国节点连接...", expanded=True) as status:
        st.write("🔍 正在抓取全球新闻源...")
        st.write("🤖 正在调用 GPT-4o mini 进行分析...")
        
        summary = get_news_and_summarize()
        
        status.update(label="✅ 完成", state="complete", expanded=False)
    
    st.markdown("---")
    st.markdown(summary)
