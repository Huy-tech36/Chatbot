import os
import json
import streamlit as st
from llama_index.core import load_index_from_storage
from llama_index.core import StorageContext,get_response_synthesizer
from llama_index.core.memory import ChatMemoryBuffer
from llama_index.core.retrievers import VectorIndexRetriever
from llama_index.core.postprocessor import SimilarityPostprocessor
from llama_index.core.query_engine import RetrieverQueryEngine
from llama_index.core.storage.chat_store import SimpleChatStore
from src.global_settings import INDEX_STORAGE, SEARCH_FILE
from llama_index.core import Settings
from llama_index.llms.openai import OpenAI
import openai

Settings.llm = OpenAI(model="gpt-4o-mini", temperature=0.2)
openai.api_key = st.secrets.openai.OPENAI_API_KEY

user_avatar = "data/images/user.png"
professor_avatar = "data/images/ai_icon.png"

def load_search_store():
    """Tải lịch sử chat từ file nếu có, nếu không khởi tạo mới."""
    if os.path.exists(SEARCH_FILE) and os.path.getsize(SEARCH_FILE) > 0:
        try:
            search_store = SimpleChatStore.from_persist_path(SEARCH_FILE)
        except json.JSONDecodeError:
            search_store = SimpleChatStore()
    else:
        search_store = SimpleChatStore()
    return search_store

def display_search(search_store, container, key):
    """Hiển thị tin nhắn từ lịch sử chat."""
    with container:
        for message in search_store.get_messages(key=key):
            if message.role == "user":
                with st.chat_message(message.role, avatar=user_avatar):
                    st.markdown(message.content)
            elif message.role == "assistant" and message.content != None:
                with st.chat_message(message.role, avatar=professor_avatar):
                    st.markdown(message.content)

def initialize_search(search_store, container, username):
    memory = ChatMemoryBuffer.from_defaults(
        token_limit=3000,
        chat_store=search_store,
        chat_store_key=username
    )

    # Tải index đã được lưu
    storage_context = StorageContext.from_defaults(persist_dir=INDEX_STORAGE)
    index = load_index_from_storage(storage_context, index_id="vector")

    retriever = VectorIndexRetriever(
        index=index,
        similarity_top_k=5
    )

    response_synthesizer = get_response_synthesizer(response_mode="tree_summarize", )

    pp = SimilarityPostprocessor(similarity_cutoff=0.5)

    query_engine = RetrieverQueryEngine(
        retriever=retriever,
        response_synthesizer=response_synthesizer,
        node_postprocessors=[pp]
    )

    display_search(search_store, container, key=username)
    return query_engine

def search_interface(search_engine, search_store, container, username):
    if not os.path.exists(SEARCH_FILE) or os.path.getsize(SEARCH_FILE) == 0:
        with container:
            with st.chat_message(name="assistant", avatar=professor_avatar):
                st.markdown("Chào mừng bạn đến với chức năng tìm kiếm thông tin từ tài liệu DSM-5 🎈")
    query = st.chat_input("Hãy nhập thông tin bệnh cần tìm kiếm ...")
    if query:
        with container:
            with st.chat_message(name="user", avatar=user_avatar):
                st.markdown(query)
            response = str(search_engine.query(query))
            with st.chat_message(name="assistant", avatar=professor_avatar):
                st.markdown(response)

        # Thêm câu hỏi và câu trả lời vào SimpleChatStore
        search_store.add_message(
            message={"content": query, "role": "user"}, key=username
        )
        search_store.add_message(
            message={"content": str(response), "role": "assistant"}, key=username
        )
        search_store.persist(SEARCH_FILE)