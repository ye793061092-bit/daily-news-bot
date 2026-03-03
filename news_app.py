import streamlit as st
from duckduckgo_search import DDGS
from deep_translator import GoogleTranslator
import datetime

# ================= 核心功能 =================

def translate_text(text):
    """辅助功能：将英文翻译成中文"""
    try:
        return GoogleTranslator(source='auto', target='zh-CN').translate(text)
    except:
        return text

def get_news_and_summarize():
    """双保险模式：优先AI总结，失败则自动翻译，全程保留点击跳转"""
    ddgs = DDGS()
    
    # 1. 抓取新闻链接
    status_placeholder = st.empty()
    status_placeholder.write("🔍 正在抓取全球新闻源...")
    
    # 准备两个容器：
    # ai_context: 给 AI 看的（带URL）
    # backup_items: 备用的（存好数据，万一 AI 挂了手动拼装）
    ai_context = ""
    backup_items = [] 
    
    try:
        queries = [
            ("🇺🇸 美国与特朗普", "Trump US politics breaking news"),
            ("🇪🇺 欧洲局势", "Europe politics economy news"),
            ("🌏 全球要闻", "World international breaking news")
        ]
        
        for category, query in queries:
            # 搜索新闻 (max_results=3 控制条数)
            results = list(ddgs.news(query, region="wt-wt", timelimit="d", max_results=3))
            
            if results:
                ai_context += f"### {category}\n"
                
                for r in results:
                    # 1. 喂给 AI 的数据格式：[标题](URL) - 摘要
                    ai_context += f"* Title: [{r['title']}]({r['url']})\n  Summary: {r['body']}\n\n"
                    
                    # 2. 存入备用库
                    backup_items.append({
                        "category": category,
                        "title": r['title'],
                        "url": r['url'],
                        "body": r['body']
                    })
    
    except Exception as e:
        return f"⚠️ 网络抓取失败: {e}"

    if not ai_context:
        return "⚠️ 未搜索到有效新闻，请稍后重试。"

    # 2. 尝试调用 AI (优先)
    status_placeholder.write("🤖 正在调用 AI 进行分析...")
    
    try:
        # 提示词重点：告诉 AI 不要丢掉链接
        prompt = f"""
        你是一名中文新闻编辑。请将以下抓取到的英文新闻资讯，整理成一份简报。
        
        【原始数据】：
        {ai_context}

        【严格要求】：
        1. **保留点击跳转功能**：输出格式必须是 Markdown 链接，即 `[中文标题](原始URL)`。
        2. 将标题和摘要翻译成**简体中文**。
        3. 分为“美国/特朗普”、“欧洲”、“全球”三个板块。
        4. 不要开场白，直接输出列表。
        """
        
        # 调用 DuckDuckGo 的免费 AI
        response = ddgs.chat(prompt, model='gpt-4o-mini')
        status_placeholder.empty()
        return response
        
    except Exception as e:
        # 🔥【翻译保底模式】如果 AI 失败，手动拼接带链接的列表
        status_placeholder.write("⚠️ AI 繁忙，正在启动自动翻译模式...")
        
        final_output = ""
        current_cat = ""
        
        try:
            for item in backup_items:
                # 如果换板块了，加个标题
                if item['category'] != current_cat:
                    final_output += f"\n### {item['category']}\n"
                    current_cat = item['category']
                
                # 翻译
                cn_title = translate_text(item['title'])
                cn_body = translate_text(item['body'])
                
                # 拼接：[翻译后的标题](原始链接)
                final_output += f"* **[{cn_title}]({item['url']})**\n"
                final_output += f"  > {cn_body}\n"
                
        except:
            return f"翻译也失败了，请检查网络。\n\n{ai_context}"

        status_placeholder.empty()
        return f"""
        **⚠️ AI 暂时繁忙，已为您切换到【自动翻译模式】（链接有效）：**
        
        ---
        {final_output}
        """

# ================= 网页界面 =================

st.set_page_config(page_title="全球热点", page_icon="🌍")
st.title("🌍 每日全球舆情 (点击标题跳转)")
st.caption(f"更新时间: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}")

if st.button("🚀 获取简报", type="primary", use_container_width=True):
    with st.spinner('正在连接美国节点...'):
        summary = get_news_and_summarize()
        
    st.markdown("---")
    # 这一步是为了让链接在新标签页打开（优化体验）
    st.markdown(summary, unsafe_allow_html=True)
