import os
import json
from datetime import datetime
import streamlit as st
from llama_index.core import load_index_from_storage
from llama_index.core import StorageContext
from llama_index.core.memory import ChatMemoryBuffer
from llama_index.core.tools import QueryEngineTool, ToolMetadata
from llama_index.agent.openai import OpenAIAgent
from llama_index.core.storage.chat_store import SimpleChatStore
from llama_index.core.tools import FunctionTool
from src.global_settings import INDEX_STORAGE, CONVERSATION_FILE, SCORES_FILE
from src.prompts import CUSTOM_AGENT_SYSTEM

user_avatar = "data/images/user.png"
professor_avatar = "data/images/ai_icon.png"

def load_chat_store():
    """Tải lịch sử chat từ file nếu có, nếu không khởi tạo mới."""
    if os.path.exists(CONVERSATION_FILE) and os.path.getsize(CONVERSATION_FILE) > 0:
        try:
            chat_store = SimpleChatStore.from_persist_path(CONVERSATION_FILE)
        except json.JSONDecodeError:
            chat_store = SimpleChatStore()
    else:
        chat_store = SimpleChatStore()
    return chat_store

def display_messages(chat_store, container, key):
    """Hiển thị tin nhắn từ lịch sử chat."""
    with container:
        for message in chat_store.get_messages(key=key):
            if message.role == "user":
                with st.chat_message(message.role, avatar=user_avatar):
                    st.markdown(message.content)
            elif message.role == "assistant" and message.content != None:
                with st.chat_message(message.role, avatar=professor_avatar):
                    st.markdown(message.content)
def save_score(score, content, total_guess, username):
        """Ghi điểm và nội dung đánh giá vào file

        Args:
            score (string): Điểm số đánh giá sức khỏe tâm lý của user
            content (string): Nội dung chi tiết liên quan đến kết quả đánh giá hoặc phản hồi cụ thể của chatbot với user
            total_guess (string):Tổng số lần phân tích sức khỏe tâm lý của user
        """
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        new_entry = {
            "username": username,
            "Time": current_time,
            "Score": score,
            "Content": content,
            "Total guess": total_guess
        }

        # Đọc dữ liệu từ file nếu tồn tại
        try:
            with open(SCORES_FILE, "r") as f:
                data = json.load(f)
        except FileNotFoundError:
            data = []

        # Thêm dữ liệu mới vào danh sách
        data.append(new_entry)

        # Ghi dữ liệu trở lại file
        with open(SCORES_FILE, "w") as f:
            json.dump(data, f, indent=4)

def initialize_chatbot(chat_store, container, username, user_info):
    memory = ChatMemoryBuffer.from_defaults(
        token_limit=3000,
        chat_store=chat_store,
        chat_store_key=username
    )
    storage_context = StorageContext.from_defaults(
        persist_dir=INDEX_STORAGE
    )
    index = load_index_from_storage(
        storage_context, index_id="vector"
    )
    dsm5_engine = index.as_query_engine(
        similarity_top_k=3,
    )
    dsm5_tool= QueryEngineTool(
        query_engine=dsm5_engine,
        metadata=ToolMetadata(
            name="dsm5",
            description=(
                f"Cung cấp các thông tin liên quan đến các bệnh "
                f"tâm thần theo tiêu chuẩn DSM5. Sử dụng câu hỏi văn bản thuần túy chi tiết làm đầu vào cho công cụ"
            ),
        )
    )
    save_tool = FunctionTool.from_defaults(fn=save_score)
    agent = OpenAIAgent.from_tools(
        tools=[dsm5_tool, save_tool],
        memory=memory,
        system_prompt=CUSTOM_AGENT_SYSTEM.format(user_info=user_info)
    )
    display_messages(chat_store, container, key=username)
    return agent

def chat_interface(agent, chat_store, container):
    with container:
        with st.chat_message(name="assistant", avatar=professor_avatar):
            st.markdown("Chào bạn, mình là MENTAL CARE. Mình luôn ở đây để để lắng nghe, chia sẻ và đồng hành cùng bạn 🎈")
    prompt = st.chat_input("Hãy chia sẻ vấn đề của bạn tại đây ...")
    if prompt:
        with container:
            with st.chat_message(name="user", avatar=user_avatar):
                st.markdown(prompt)
            response = str(agent.chat(prompt))
            with st.chat_message(name="assistant", avatar=professor_avatar):
                st.markdown(response)
            """assistant_message = st.chat_message(name="assistant", avatar=professor_avatar)
            message_placeholder = assistant_message.empty()
            # Sử dụng stream_chat để nhận phản hồi từng token một
            response = agent.stream_chat(prompt)
            # Tạo một biến để lưu trữ nội dung phản hồi
            full_response = ""
            # Lặp qua các token và kết hợp chúng thành câu hoàn chỉnh
            for token in response.response_gen:
                full_response += token
                message_placeholder.markdown(full_response)"""
        chat_store.persist(CONVERSATION_FILE)
