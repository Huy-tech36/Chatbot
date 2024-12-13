import streamlit as st
from src.authenticate import login, register, guest_login
import src.sidebar as sidebar

def main():
    st.set_page_config(
        page_title="MENTAL CARE",
        page_icon=":heart:",
        layout="wide"
    )
    sidebar.show_sidebar()

    # Giao diện đăng nhập
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False

    if not st.session_state.logged_in:
        with st.expander('MENTAL CARE', expanded=True):
            login_tab, create_tab, guest_tab = st.tabs(
                [
                    "Đăng nhập",
                    "Tạo tài khoản",
                    "Khách"
                ]
            )
            with create_tab:
                register()
            with login_tab:
                login()
            with guest_tab:
                guest_login()
    else:
        col1, col2, col3 = st.columns(3)

        with col1:
            st.image("data/images/tu_van.png")
            if st.button("Trò chuyện với chuyên gia tâm lý AI"):
                st.switch_page("pages/💬Chat.py")

        with col2:
            st.image("data/images/search.png")
            if st.button("Tìm kiếm thông tin về bệnh tâm lý"):
                st.switch_page("pages/🔍Search.py")

        with col3:
            st.image("data/images/theo_doi.png")
            if st.button("Theo dõi thông tin sức khỏe của bạn"):
                st.switch_page("pages/👦User.py")

        st.success(f'Chào mừng {st.session_state.username}, hãy khám phá các tính năng của ứng dụng chăm sóc sức khỏe tinh thần nhé!', icon="🎉")
if __name__ == "__main__":
    main()
