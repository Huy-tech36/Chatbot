import streamlit as st
from llama_index.llms.openai import OpenAI
import openai
from src.conversation_engine import initialize_chatbot, chat_interface, load_chat_store
from llama_index.core import Settings
import src.sidebar as sidebar

Settings.llm = OpenAI(model="gpt-4o-mini", temperature=0.2)
openai.api_key = st.secrets.openai.OPENAI_API_KEY

def main():
    st.set_page_config(
        page_title="MENTAL CARE",
        page_icon=":heart:",
        layout="wide"
    )
    sidebar.show_sidebar()
    
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False
    if st.session_state.logged_in:
        username = st.session_state.username
        user_info = st.session_state.user_info
        st.header("💬 MENTALCARE - HÀNH TRÌNH VÌ SỨC KHỎE TÂM HỒN CỦA BẠN")
        chat_store = load_chat_store()
        container = st.container()
        agent = initialize_chatbot(chat_store, container, username, user_info)
        chat_interface(agent, chat_store, container)

if __name__ == "__main__":
    main()
