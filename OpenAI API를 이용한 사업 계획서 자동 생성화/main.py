import streamlit as st
import app1
import app2

# 메인 함수
def main():
    st.sidebar.title("서비스 선택")
    app_options = ["사업계획서 생성", "사업계획서 예시 보기"]
    app_choice = st.sidebar.selectbox("이용하고자 하는 서비스를 선택하세요", app_options)

    if app_choice == "사업계획서 예시 보기":
        app1.main()
    elif app_choice == "사업계획서 생성":
        app2.main()

if __name__ == "__main__":
    main()