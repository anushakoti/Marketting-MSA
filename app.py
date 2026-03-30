import streamlit as st
from dotenv import load_dotenv
load_dotenv()  # MUST BE BEFORE OTHER IMPORTS

import asyncio
import os
import json
import logging
from langchain_core.messages import HumanMessage, AIMessage
from graph.graph import graph
from supabase_client import supabase_mgr

logger = logging.getLogger(__name__)

# --- Check Credentials ---
def check_supabase_creds():
    url = os.environ.get("SUPABASE_URL")
    key = os.environ.get("SUPABASE_KEY")
    if not url or not key:
        try:
            url = url or st.secrets.get("SUPABASE_URL")
            key = key or st.secrets.get("SUPABASE_KEY")
        except: pass
    return url and key

if not check_supabase_creds():
    st.error("Supabase credentials not found. Please set `SUPABASE_URL` and `SUPABASE_KEY` in your `.env` file or Streamlit secrets.")
    st.stop()

st.set_page_config(
    page_title="EcoShop AI Assistant",
    page_icon="🌿",
    layout="wide",
)

st.markdown("""
    <style>
        .stApp { background-color: #f0f7f0; color: #2d4a2d; }
        section[data-testid="stSidebar"] { background-color: #d6ead6; }
        h1 { color: #2d6a2d !important; font-family: 'Georgia', serif; }
        .stCaption { color: #5a8a5a !important; }
        .stChatInput textarea { background-color: #e8f5e8 !important; border: 1.5px solid #5a8a5a !important; color: #2d4a2d !important; border-radius: 12px !important; }
        .stChatMessage[data-testid="stChatMessageUser"] { background-color: #c8e6c8 !important; border-radius: 12px !important; }
        .stChatMessage[data-testid="stChatMessageAssistant"] { background-color: #e8f5e8 !important; border-radius: 12px !important; }
        .stButton > button { background-color: #4caf50 !important; color: white !important; border-radius: 8px !important; border: none !important; }
        .stButton > button:hover { background-color: #388e3c !important; }
        hr { border-color: #a5c8a5; }
    </style>
""", unsafe_allow_html=True)

# --- State Initialization ---
if "user" not in st.session_state:
    st.session_state.user = None
if "current_page" not in st.session_state:
    st.session_state.current_page = "Home"
if "conv_id" not in st.session_state:
    st.session_state.conv_id = None
if "messages" not in st.session_state:
    st.session_state.messages = []

async def run_agent_stream(messages, conv_id):
    full_response = ""
    placeholder = st.empty()
    extras = {}

    config = {"configurable": {"thread_id": conv_id}}
    
    async for event in graph.astream_events(
        {"messages": messages},
        config=config,
        version="v2",
    ):
        kind = event["event"]
        if kind == "on_chat_model_stream":
            chunk = event["data"]["chunk"]
            content = chunk.content
            
            text = ""
            if isinstance(content, list):
                for block in content:
                    if isinstance(block, dict):
                        text += block.get("text", "")
                    elif hasattr(block, "text"):
                        text += block.text
                    else:
                        text += str(block)
            elif content:
                text = str(content)
                
            if text:
                full_response += text
                placeholder.markdown(full_response + "▌")
        elif kind == "on_tool_start":
            tool_name = event.get("name", "tool")
            placeholder.markdown(full_response + f"\n\n🌱 *Running {tool_name}...*")
        elif kind == "on_tool_end":
            tool_name = event["name"]
            tool_output = event["data"]["output"]
            
            # Ensure tool_output is JSON-serializable for database storage
            serializable_output = tool_output
            if hasattr(tool_output, "content"):
                serializable_output = str(tool_output.content)
            elif not isinstance(tool_output, (dict, list, str, int, float, bool, type(None))):
                serializable_output = str(tool_output)

            # Save ALL tool outputs in extras for the dashboard to find
            extras[tool_name] = serializable_output

            if tool_name == "generate_logo":
                try:
                    # Robust handling of tool_output (could be string or dict)
                    res_data = serializable_output
                    if isinstance(res_data, str):
                        try:
                            res_data = json.loads(serializable_output)
                        except:
                            pass
                    
                    if isinstance(res_data, dict) and "image_url" in res_data:
                        extras["image_url"] = res_data["image_url"]
                        # Update conversation title from business name if possible
                        if "business_name" in event["data"]["input"]:
                            new_title = f"Brand: {event['data']['input']['business_name']}"
                            supabase_mgr.update_conversation_title(conv_id, new_title)
                except Exception as e:
                    logger.error(f"Error parsing logo output: {e}")

    placeholder.markdown(full_response)
    if extras.get("image_url"):
        st.image(extras["image_url"], caption="🌱 Generated Asset", width=300)
    
    return full_response, extras

# --- Sidebar ---
def sidebar():
    st.sidebar.title("🌿 EcoShop AI")
    if st.session_state.user:
        st.sidebar.write(f"Logged in: **{st.session_state.user.email}**")
        if st.sidebar.button("Logout", use_container_width=True):
            supabase_mgr.logout()
            st.session_state.user = None
            st.session_state.current_page = "Home"
            st.rerun()
        
        st.sidebar.divider()
        if st.sidebar.button("💬 Chatbot", use_container_width=True):
            st.session_state.current_page = "Chatbot"
            st.rerun()
        if st.sidebar.button("📊 Dashboard", use_container_width=True):
            st.session_state.current_page = "Dashboard"
            st.rerun()
            
        if st.session_state.current_page == "Chatbot":
            st.sidebar.divider()
            st.sidebar.subheader("My Conversations")
            if st.sidebar.button("🆕 New Chat", use_container_width=True):
                st.session_state.conv_id = None
                st.session_state.messages = []
                st.rerun()
            
            try:
                convs = supabase_mgr.get_conversations(st.session_state.user.id)
                for conv in convs:
                    if st.sidebar.button(conv['title'], key=f"conv_{conv['id']}", use_container_width=True):
                        st.session_state.conv_id = conv['id']
                        st.session_state.messages = supabase_mgr.get_messages(conv['id'])
                        st.rerun()
            except: pass
    else:
        if st.sidebar.button("🏠 Home", use_container_width=True):
            st.session_state.current_page = "Home"
            st.rerun()
        if st.sidebar.button("🔑 Login / Signup", use_container_width=True):
            st.session_state.current_page = "Auth"
            st.rerun()

def home_page():
    st.title("🌿 Welcome to EcoShop AI")
    st.markdown("""
    ### Build your sustainable brand in minutes.
    Our AI assistant helps you create a business strategy, generate logos, optimize SEO, and much more.
    """)
    
    c1, c2, c3 = st.columns(3)
    with c1: st.info("🎨 **Logo Generation**\nProfessional logos uploaded directly to the cloud.")
    with c2: st.info("📈 **Growth Strategy**\nAI-driven plans for eco-friendly businesses.")
    with c3: st.info("💾 **History**\nAll your conversations and assets saved securely.")

    if not st.session_state.user:
        if st.button("Start Your Journey", type="primary"):
            st.session_state.current_page = "Auth"
            st.rerun()
    else:
        if st.button("Go to Chatbot", type="primary"):
            st.session_state.current_page = "Chatbot"
            st.rerun()

def auth_page():
    st.title("🔑 Get Started")
    tab1, tab2 = st.tabs(["Login", "Sign Up"])
    
    with tab1:
        with st.form("login"):
            e = st.text_input("Email")
            p = st.text_input("Password", type="password")
            if st.form_submit_button("Login"):
                try:
                    res = supabase_mgr.login(e, p)
                    st.session_state.user = res.user
                    st.session_state.current_page = "Chatbot"
                    st.rerun()
                except Exception as ex: st.error(f"Error: {ex}")
                
    with tab2:
        with st.form("signup"):
            e = st.text_input("Email")
            p = st.text_input("Password", type="password")
            if st.form_submit_button("Sign Up"):
                try:
                    supabase_mgr.sign_up(e, p)
                    st.success("Check your email!")
                except Exception as ex: st.error(f"Error: {ex}")

def chatbot_page():
    st.title("💬 EcoShop Assistant")
    
    if not st.session_state.messages:
        st.info("""
        ### Welcome! 🌿 
        I'm your **EcoShop AI Consultant**. I can help you build your brand from scratch.
        
        **You can ask me to:**
        *   🎨 **Generate a Logo** for your business
        *   📈 Create a **Marketing Strategy**
        *   ✨ Brainstorm **Taglines & Pitches**
        *   🔍 Provide **SEO Keywords** & Content Ideas
        *   📱 Write **Social Media Posts** (Instagram, LinkedIn, etc.)
        *   📢 Draft **Google/Social Ads**
        *   📧 Create an **Email Marketing Campaign**
        *   🌐 Suggest **Domain Names**
        
        *Try saying: "Help me build a marketing plan for my eco-friendly soap business"*
        """)

    for m in st.session_state.messages:
        role = "user" if m['role'] == "user" else "assistant"
        with st.chat_message(role):
            st.markdown(m['content'])
            if m.get('extras') and m['extras'].get('image_url'):
                st.image(m['extras']['image_url'], width=300)

    if prompt := st.chat_input("How can I help you today?"):
        if not st.session_state.user:
            st.warning("Please log in.")
            return

        if not st.session_state.conv_id:
            title = f"Brand: {prompt[:15]}..."
            new_conv = supabase_mgr.create_conversation(st.session_state.user.id, title)
            st.session_state.conv_id = new_conv['id']
        
        st.session_state.messages.append({"role": "user", "content": prompt})
        supabase_mgr.save_message(st.session_state.conv_id, "user", prompt)
        
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            langchain_msgs = []
            for m in st.session_state.messages:
                if m['role'] == "user": langchain_msgs.append(HumanMessage(content=m['content']))
                else: langchain_msgs.append(AIMessage(content=m['content']))
            
            response, extras = asyncio.run(run_agent_stream(langchain_msgs, st.session_state.conv_id))
            
            supabase_mgr.save_message(st.session_state.conv_id, "assistant", response, extras)
            st.session_state.messages.append({"role": "assistant", "content": response, "extras": extras})

def dashboard_page():
    if not st.session_state.user:
        st.warning("Please log in to view your dashboard.")
        st.session_state.current_page = "Auth"
        st.rerun()
        return

    st.title("📊 My Brand Assets")
    st.caption("Central dashboard for all generated logos, strategies, and taglines.")
    
    try:
        user_id = st.session_state.user.id
        convs = supabase_mgr.get_conversations(user_id)
        
        if not convs:
            st.info("No conversations found. Start a chat to generate assets!")
            return

        found_any = False
        
        tab1, tab2, tab3 = st.tabs(["🎨 Logos", "💡 Messaging & Strategy", "🚀 Marketing & SEO"])
        
        strategy_keys = ["generate_taglines", "create_marketing_strategy"]
        marketing_keys = ["generate_seo_keywords", "get_domain_suggestions", "create_social_media_content", "create_ad_copy", "create_email_campaign"]

        for c in convs:
            msgs = supabase_mgr.get_messages(c['id'])
            for m in msgs:
                # Ensure extras is a dictionary
                extras = m.get('extras')
                if not extras:
                    extras = {}
                elif isinstance(extras, str):
                    try:
                        extras = json.loads(extras)
                    except:
                        extras = {}
                
                if not isinstance(extras, dict):
                    extras = {}

                with tab1:
                    image_url = extras.get('image_url')
                    
                    if not image_url and "generate_logo" in extras:
                        logo_data = extras["generate_logo"]
                        if isinstance(logo_data, str):
                            try:
                                logo_data = json.loads(logo_data)
                            except: pass
                        if isinstance(logo_data, dict) and "image_url" in logo_data:
                            image_url = logo_data["image_url"]
                    
                    # Fallback to content if it looks like a URL
                    if not image_url and m.get('role') == 'assistant':
                        content = str(m.get('content', ''))
                        if content.startswith('http') and ('.png' in content or '.jpg' in content or 'supabase' in content):
                            image_url = content

                    if image_url:
                        found_any = True
                        with st.container(border=True):
                            col1, col2 = st.columns([1, 2])
                            with col1:
                                st.image(image_url, use_container_width=True)
                            with col2:
                                st.subheader(f"Logo for {c['title']}")
                                st.write(f"**Created**: {m.get('created_at', 'N/A')}")
                                st.markdown(f"🔗 [View Full Image]({image_url})")
                
                # --- Tab 2: Messaging & Strategy ---
                with tab2:
                    for key in strategy_keys:
                        if key in extras and extras[key]:
                            found_any = True
                            title_map = {
                                "generate_taglines": "✨ Taglines & Pitch",
                                "create_marketing_strategy": "📈 Marketing Strategy"
                            }
                            with st.expander(f"{title_map.get(key, key)} (from {c['title']})", expanded=False):
                                st.markdown(extras[key])
                
                # --- Tab 3: Marketing & SEO ---
                with tab3:
                    for key in marketing_keys:
                        if key in extras and extras[key]:
                            found_any = True
                            title_map = {
                                "generate_seo_keywords": "🔍 SEO Keywords",
                                "get_domain_suggestions": "🌐 Domain Ideas",
                                "create_social_media_content": "📱 Social Media Content",
                                "create_ad_copy": "📢 Ad Copy",
                                "create_email_campaign": "📧 Email Campaign"
                            }
                            with st.expander(f"{title_map.get(key, key)} (from {c['title']})", expanded=False):
                                st.markdown(extras[key])
        
        if not found_any:
            st.info("No assets (logos, taglines, or strategies) generated yet. Try asking the chatbot for help with your brand!")
            st.image("https://illustrations.popsy.co/green/searching.svg", width=300)
            
    except Exception as e: 
        st.error(f"Error loading dashboard: {str(e)}")
        logger.error(f"Dashboard Error: {e}")
            
    except Exception as e: 
        st.error(f"Error loading dashboard: {str(e)}")
        logger.error(f"Dashboard Error: {e}")

sidebar()
if st.session_state.current_page == "Home": home_page()
elif st.session_state.current_page == "Auth": auth_page()
elif st.session_state.current_page == "Chatbot": chatbot_page()
elif st.session_state.current_page == "Dashboard": dashboard_page()