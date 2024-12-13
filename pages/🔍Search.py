from llama_index.llms.openai import OpenAI
import openai
import streamlit as st
from llama_index.core import Settings
from src.search_engine import initialize_search, search_interface, load_search_store
import src.sidebar as sidebar

openai.api_key = st.secrets.openai.OPENAI_API_KEY
Settings.llm = OpenAI(model="gpt-4o-mini", temperature=0.2)


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
        st.header("🔍 KHÁM PHÁ DSM-5 - KHỞI ĐẦU CHO SỰ THAY ĐỔI TÍCH CỰC")
        search_store = load_search_store()
        container = st.container()

        search_engine = initialize_search(search_store, container, username)
        search_interface(search_engine, search_store, container, username)


if __name__ == "__main__":
    main()
