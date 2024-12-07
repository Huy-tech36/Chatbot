import streamlit as st

def show_sidebar():
    st.sidebar.image("data/images/logo1.png", use_column_width=True)

    st.sidebar.markdown("### 🌸 Lời Nhắc Tự Chăm Sóc")
    st.sidebar.markdown("Đừng quên nghỉ ngơi và lắng nghe bản thân. Bạn đang làm rất tốt!")
    st.sidebar.markdown("### 📰 Mẹo Tâm Lý Hôm Nay")
    st.sidebar.markdown("Hãy thử **hít thở sâu** khi bạn cảm thấy lo âu.")
    st.sidebar.markdown("**Ghi chú cảm xúc** giúp bạn hiểu bản thân hơn mỗi ngày.")
    st.sidebar.markdown("### 📱 Về Ứng Dụng")
    st.sidebar.markdown("Liên hệ hỗ trợ: Gửi ý kiến về [Email](mailto:icl.bahuy@gmail.com)")
