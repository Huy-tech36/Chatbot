import streamlit as st

def show_sidebar():
    st.sidebar.image("data/images/logo.png", use_column_width=True)
    st.sidebar.markdown('### 🧠 Mental Care chăm sóc sức khỏe tâm thần của bạn')

    st.sidebar.markdown('Hướng dẫn sử dụng:')
    st.sidebar.markdown('1. 🟢 **Đăng nhập tài khoản.**')
    st.sidebar.markdown('2. 💬 **Chức năng Chat - "Nói chuyện với chuyên gia tâm lý AI" để chia sẻ cảm xúc của bạn**')
    st.sidebar.markdown('3. 🔍 **Chức năng tra cứu - Tra cứu thông tin về triệu chứng, dấu hiệu của các bệnh tâm thần từ tài liệu DSM-5**')
    st.sidebar.markdown('4. 📊 **Chức năng User - "Theo dõi thông tin sức khỏe của bạn" xem thống kê chi tiết về chẩn đoán và biểu đồ sức khỏe tinh thần của mình.**')


    st.sidebar.markdown("### 📰 Mẹo Tâm Lý Hôm Nay")
    st.sidebar.markdown("Hãy thử **hít thở sâu** khi cảm thấy lo âu.")

    st.sidebar.markdown("### 📱 Về Ứng Dụng")
    st.sidebar.markdown("Liên hệ hỗ trợ: Gửi ý kiến về [Email](mailto:icl.bahuy@gmail.com)")
