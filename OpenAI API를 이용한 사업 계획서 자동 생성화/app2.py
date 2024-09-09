import streamlit as st
import json
from datetime import datetime
from generate_business_plan import generate_business_plan
from dotenv import load_dotenv
import os
from elasticsearch import Elasticsearch
import pandas as pd

# 환경 변수 로드
load_dotenv()

# JSON 파일 로드하는 함수
def load_json(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return json.load(file)
    except FileNotFoundError:
        st.error("JSON 파일을 찾을 수 없습니다.")
        return None
    except json.JSONDecodeError:
        st.error("JSON 파일을 디코딩하는 데 실패했습니다.")
        return None

# 산업 이름 리스트 생성
def get_industry_names(industry_mapping):
    return list(industry_mapping.keys())

# 산업 이름에서 코드로 변환하는 함수
def get_industry_code(industry_name, industry_mapping):
    return industry_mapping.get(industry_name, None)

def main():
    # JSON 파일 로드
    industry_mapping = load_json('industry_mapping.json')
    field_translation = load_json('field_mapping.json')

    if not industry_mapping or not field_translation:
        st.error("JSON 데이터를 로드할 수 없습니다.")
        return

    if 'section' not in st.session_state:
        st.session_state.section = 'initial'

    # Sidebar 메뉴
    with st.sidebar:
        st.header("메뉴")
        if st.button("사업 계획서 생성", key='initial_btn'):
            st.session_state.section = 'initial'
        if 'result' in st.session_state:
            if st.button("개요", key='overview_btn'):
                st.session_state.section = 'overview'
            if st.button("비즈니스 캔버스 1", key='canvas_1_btn'):
                st.session_state.section = 'canvas_1'
            if st.button("비즈니스 캔버스 2", key='canvas_2_btn'):
                st.session_state.section = 'canvas_2'
            if st.button("비즈니스 캔버스 3", key='canvas_3_btn'):
                st.session_state.section = 'canvas_3'
            if st.button("저장", key='complete_btn'):
                st.session_state.section = 'complete'

    if st.session_state.section == 'initial':
        st.header("사업계획서 생성")
        industry_names = get_industry_names(industry_mapping)
        industry_name = st.selectbox("산업 분야를 선택하세요", industry_names)
        item_kw = st.text_input("아이템명을 입력하세요")
        prod_serv_sum = st.text_input("아이템에 대한 설명을 입력하세요")
        end_year = st.number_input("현재 연도를 입력하세요", min_value=2000, max_value=2100, value=datetime.now().year)
        duration = st.number_input("허핀달-허쉬만 지수를 보여줄 기간(년수)을 입력하세요", min_value=1, max_value=10, value=5)

        if st.button("사업 계획서 생성", key='generate_plan'):
            if not item_kw :
                st.error("아이템명을 입력하세요.")
                return
            if not prod_serv_sum:
                st.error("아이템에 대한 설명을 입력하세요.")
                return
            
            industry_code = get_industry_code(industry_name, industry_mapping)
            if not industry_code:
                st.error("산업 코드를 찾을 수 없습니다.")
                return

            result = generate_business_plan(industry_code, item_kw, prod_serv_sum, end_year, duration)
            
            if "error" in result:
                st.error(result["error"])
                st.error(f"API 응답: {result['response']}")
            else:
                st.session_state.result = result
                st.session_state.section = 'generated'

    if 'result' in st.session_state and st.session_state.section == 'generated':
        st.success("사업 계획서가 생성되었습니다.")
        if st.button("수정하기", key='edit_plan'):
            st.session_state.section = 'overview'

    def create_text_area_over(section, content):
        cols = st.columns(len(content))  # 3개의 컬럼으로 분할
        for idx, col in enumerate(cols):
            with col:
                if idx < len(content):
                    item = content[idx]
                    for key, value in item.items():
                        key_label = field_translation.get(key, key)
                        st.text_area(f"{key_label}", value=value, key=f"overview_{section}_{idx}_{key}", height=150)

    if 'result' in st.session_state and st.session_state.section == 'overview':
        st.session_state.section = 'overview'
        with st.form(key='overview_form'):
            for section, content in st.session_state.result["overview"].items():
                if section == "motivation":
                    st.header(field_translation.get(section, section))
                    for sub_section, sub_content in content.items():
                        sub_section_label = field_translation.get(sub_section, sub_section)
                        st.text_area(f"{sub_section_label}", value=sub_content, key=f"overview_{sub_section}", height=150)
                elif section == "uniq":
                    st.header(field_translation.get(section, section))
                    create_text_area_over(section, content)

            overview_submit_button = st.form_submit_button(label='저장하기')

            if overview_submit_button:
                for section in st.session_state.result["overview"]:
                    if isinstance(st.session_state.result["overview"][section], dict):
                        for sub_section in st.session_state.result["overview"][section]:
                            st.session_state.result["overview"][section][sub_section] = st.session_state.get(f"overview_{sub_section}", "")
                    elif section == "uniq":
                        for idx, item in enumerate(st.session_state.result["overview"][section]):
                            for key in item:
                                item[key] = st.session_state.get(f"overview_{section}_{idx}_{key}", "")
                st.success("개요가 수정 및 저장되었습니다.")
                result_json = json.dumps(st.session_state.result, indent=4, ensure_ascii=False)
                # st.json(result_json)

    def create_text_area(section, content):
        cols = st.columns(len(content))
        for idx, col in enumerate(cols):
            with col:
                if idx < len(content):
                    item = content[idx]
                    for key, value in item.items():
                        key_label = field_translation.get(key, key)
                        st.text_area(f"{key_label}", value=value, key=f"business_canvas_{section}_{idx}_{key}", height=150)

    if 'result' in st.session_state and st.session_state.section.startswith('canvas'):
        canvas_sections = {
            'canvas_1': ['cust_seg', 'val_prop', 'chn'],
            'canvas_2': ['cust_rel', 'rev_streams', 'key_res'],
            'canvas_3': ['key_act', 'key_part', 'cost_str']
        }

        current_sections = canvas_sections[st.session_state.section]

        for section in current_sections:
            section_label = field_translation.get(section, section)
            st.header(section_label)
            with st.form(key=f'business_canvas_form_{st.session_state.section}_{section}'):
                create_text_area(section, st.session_state.result["business_canvas"][section])

                canvas_submit_button = st.form_submit_button(label='저장하기')

                if canvas_submit_button:
                    if isinstance(st.session_state.result["business_canvas"][section], list):
                        for idx, item in enumerate(st.session_state.result["business_canvas"][section]):
                            for key in item:
                                item[key] = st.session_state.get(f"business_canvas_{section}_{idx}_{key}", "")
                    st.success(f"{section_label}가(이) 수정 및 저장되었습니다.")
                    result_json = json.dumps(st.session_state.result, indent=4, ensure_ascii=False)
                    # st.json(result_json)

    def login():
        username = '###'
        password = '#######'
        return (username, password)

    # elastic server 호출 및 인증
    es = Elasticsearch(
        ['http:/.../'],
        basic_auth=login())

    # index 내 문서 수 확인 (id 생성을 위해)
    def get_document_count(es, index_name):
        try:
            response = es.count(index=index_name)
            count = response['count']
            return count
        except Exception as e:
            print(f"Error: {e}")
            return None

    # doc 별로 ElasticSearch에 데이터 삽입
    def insert_data(es, index_name, data):
        i = get_document_count(es, index_name)
        response = es.index(index=index_name, id=f"doc_{i+1}", document=data)

    if 'result' in st.session_state and st.session_state.section == 'complete':
        if st.button("저장 완료", key='final_save'):
            result_json = json.dumps(st.session_state.result, indent=4, ensure_ascii=False)
            insert_data(es, 'business_plan', result_json)
            st.success("저장되었습니다.")
            st.stop()  # 이후의 코드를 실행하지 않도록 중지
        st.warning("정말로 저장하시겠습니까? 더 이상 수정할 수 없습니다.")

if __name__ == "__main__":
    main()
