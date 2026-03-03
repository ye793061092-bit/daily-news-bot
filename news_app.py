import streamlit as st
from duckduckgo_search import DDGS
from deep_translator import GoogleTranslator
import datetime

# ================= 核心功能 =================

def translate_text(text):
    """使用 deep_translator 进行免费翻译"""
    try:
        # 自动翻译成简体中文
        return GoogleTranslator(source='auto', target='zh-CN').translate(text)
    except:
        return text

def get_news_and_summarize():
    """三保险模式：AI总结 -> 失败则原文翻译 -> 失败则显示原文"""
    ddgs = DDGS()
    translator = GoogleTranslator(source='auto', target='zh-CN')
    
    # 1. 抓取新闻链接
    status_placeholder = st.empty()
    status_placeholder.write("🔍 正在抓取全球新闻源...")
    
    raw_context_for_ai = "" # 给 AI 看英文（更准）
    backup_content = ""     # 备用的中文显示内容
    
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
                raw_context_for_ai += f"### {category}\n"
                backup_content += f"### {category}\n"
                
                for r in results:
                    # 给 AI 喂英文
                    raw_context_for_ai += f"* [{r['title']}]({r['url']})\n  > {r['body']}\n\n"
                    
                    # 准备备用中文内容 (只在 AI 失败时才实时翻译，节省时间)
                    backup_content += f"* [{r['title']}]({r['url']})\n  > {{body_placeholder_{r['url']}}}\n\n"
                    # 这里先存着，等需要展示备用内容时再翻译 body
    
    except Exception as e:
        return f"⚠️ 网络抓取失败: {e}"

    if not raw_context_for_ai:
        return "⚠️ 未搜索到有效新闻，请稍后重试。"

    # 2. 尝试调用 AI
    status_placeholder.write("🤖 正在调用 AI 进行分析...")
    
    try:
        # 尝试使用 DuckDuckGo 的 AI
        prompt = f"""
        你是一名中文新闻编辑。请将以下抓取到的英文新闻资讯，整理成一份简报。
        
        【原始数据】：
        {raw_context_for_ai}

        【输出要求】：
        1. 必须使用**简体中文**。
        2. 分为“美国/特朗普”、“欧洲”、“全球”三个板块。
        3. 标题加粗，下面跟一句中文简要说明。
        4. 只要干货，不要开场白。
        """
        
        # 这一步需要 duckduckgo-search>=6.3.0 版本
        response = ddgs.chat(prompt, model='gpt-4o-mini')
        status_placeholder.empty()
        return response
        
    except Exception as e:
        # 🔥【翻译保底模式】如果 AI 失败了，启动翻译机
        status_placeholder.write("⚠️ AI 繁忙，正在启动自动翻译模式...")
        
        final_backup = ""
        # 重新遍历一次来翻译，虽然慢点但能看懂
        try:
            for category, query in queries:
                final_backup += f"### {category}\n"
                results = list(ddgs.news(query, region="wt-wt", timelimit="d", max_results=3))
                for r in results:
                    # 翻译标题
                    cn_title = translate_text(r['title'])
                    # 翻译摘要
                    cn_body = translate_text(r['body'])
                    
                    final_backup += f"* **[{cn_title}]({r['url']})**\n"
                    final_backup += f"  > *{cn_body}*\n\n"
        except:
            return f"翻译也失败了，请检查网络。\n\n{raw_context_for_ai}"

        status_placeholder.empty()
        return f"""
        **⚠️ AI 暂时繁忙，已为您切换到【自动翻译模式】：**
        
        ---
        {final_backup}
        """

# ================= 网页界面 =================

st.set_page_config(page_title="全球热点", page_icon="🌍")
st.title("🌍 每日全球舆情 (自动翻译版)")
st.caption(f"更新时间: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}")

if st.button("🚀 获取简报", type="primary", use_container_width=True):
    with st.spinner('正在连接美国节点...'):
        summary = get_news_and_summarize()
        
    st.markdown("---")
    st.markdown(summary)
