import json
import streamlit as st
from elasticsearch import Elasticsearch, NotFoundError, ConnectionError
from PIL import Image, ImageDraw, ImageFont
import logging
import pandas as pd
import plotly.express as px

def login():
    username = '###'
    password = '##########'
    return (username, password)

es = Elasticsearch(
    ['http:/../'],
    basic_auth=login())

def main():

    st.header("사업계획서 예시")

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

    def get_documents_by_search_word(index_name, search_word=None):
        must_clauses = []
        
        if search_word:
            must_clauses.append({
                "multi_match": {
                    "query": search_word,
                    "fields": ["item_kw^2", "overview.prod_serv_sum", "motivte","detail_desc"],
                    "type": "best_fields",
                    "operator": "and"
                }
            })

        query = {
            "query": {
                "bool": {
                    "must": must_clauses
                }
            },
            "size": 10000  # 검색 결과의 최대 크기를 늘립니다.
        }

        try:
            response = es.search(index=index_name, body=query)
        except NotFoundError:
            st.error(f"인덱스 '{index_name}'를 찾을 수 없습니다.")
            return None
        except ConnectionError:
            st.error("Elasticsearch에 연결할 수 없습니다.")
            return None

        documents = [{"_id": hit["_id"], "_source": hit["_source"], "_score": hit["_score"]} for hit in response["hits"]["hits"]]
        return documents

    def classify_documents_by_industry(documents, industry_mapping):
        classified_documents = {}
        for doc in documents:
            industry_code = doc['_source'].get('ind_code')
            industry_name = next((name for name, code in industry_mapping.items() if code == industry_code), "Unknown")
            if industry_name not in classified_documents:
                classified_documents[industry_name] = []
            classified_documents[industry_name].append(doc)
        return classified_documents

    def get_nested_value(data, keys):
        for key in keys:
            if isinstance(data, list):
                try:
                    key = int(key)
                    data = data[key]
                except (ValueError, IndexError):
                    return None
            elif isinstance(data, dict):
                data = data.get(key)
            else:
                return None
        return data

    def translate_field(key: str, field_mapping: dict) -> str:
        return field_mapping.get(key, key)

    def render_table(data, field_mapping, title=None, highlight_word=None):
        if not data:
            return ""

        headers = []
        rows = []

        # Collect headers and rows while maintaining order
        for item in data:
            row = {}
            for key, value in item.items():
                if key not in headers:
                    headers.append(key)
                row[key] = value
            rows.append(row)
        
        table = "<table style='width:100%; border-collapse: collapse;'>"
        table += "<tr>" + "".join(f"<th style='border: 1px solid #ddd; padding: 8px; text-align:left; font-weight: normal;'>{translate_field(header, field_mapping)}</th>" for header in headers) + "</tr>"
        
        previous_values = {header: None for header in headers}
        rowspan_counts = {header: 0 for header in headers}

        for row in rows:
            table += "<tr>"
            for header in headers:
                cell_value = row.get(header, '')
                cell_value_str = str(cell_value)
                if highlight_word and highlight_word.lower() in cell_value_str.lower():
                    cell_value_str = cell_value_str.replace(highlight_word, f"<b><span style='color: #ff4b4b;'>{highlight_word}</span></b>")
                
                if cell_value == previous_values[header]:
                    rowspan_counts[header] += 1
                else:
                    if rowspan_counts[header] > 1:
                        table = table.replace(f"<td {header}>", f"<td rowspan='{rowspan_counts[header]}' {header}>", 1)
                    rowspan_counts[header] = 1
                
                previous_values[header] = cell_value
                table += f"<td {header} style='border: 1px solid #ddd; padding: 8px; text-align:left; font-weight: normal;'>{cell_value_str}</td>"
            table += "</tr>"
        
        for header in headers:
            if rowspan_counts[header] > 1:
                table = table.replace(f"<td {header}>", f"<td rowspan='{rowspan_counts[header]}' {header}>", 1)

        table += "</table>"
        return table


    def render_overview(data, field_mapping, highlight_word=None):
        overview_data = {
            "prod_serv_sum": get_nested_value(data, "overview.prod_serv_sum".split('.')),
            "motivation": {
                "reason": get_nested_value(data, "overview.motivation.reason".split('.')),
                "market_needs": get_nested_value(data, "overview.motivation.market_needs".split('.')),
                "vision": get_nested_value(data, "overview.motivation.vision".split('.'))
            },
            "uniq": get_nested_value(data, "overview.uniq".split('.')),
            "market_con": get_nested_value(data, "overview.market_con".split('.'))
        }

        st.markdown("#### 개요")
        
        for category, subcategories in overview_data.items():
            if category == "market_con" and subcategories:
                market_con_data = subcategories[0]
                years = list(market_con_data.keys())
                values = list(market_con_data.values())
                market_con_df = pd.DataFrame({'Year': years, 'Value': values}).set_index('Year')

                fig = px.line(market_con_df, x=market_con_df.index, y='Value', 
                                title='시장 집중도',
                                labels={'Value': '집중도', 'Year': '연도'},
                                line_shape='linear', render_mode='svg')
                fig.update_layout(
                    xaxis_title='연도',
                    yaxis_title='HHI',
                    template='plotly_white',
                    hovermode='x unified',
                    hoverlabel=dict(bgcolor="white", font_size=12),
                    legend_title_text='',
                )
                fig.update_traces(line=dict(width=3, color='#ff4b4b'), hovertemplate='%{y}')
                st.plotly_chart(fig, use_container_width=True)

                st.markdown("<div style='color: lightgrey; font-size: small;'>HHI (Herfindahl-Hirschman Index):<br>시장 집중도를 나타내는 지표로, 0에서 10,000 사이의 값을 가집니다.<br>값이 높을수록 시장 집중도가 높음을 의미합니다.</div>", unsafe_allow_html=True)

                continue
            
            if isinstance(subcategories, dict):
                st.markdown(f"##### {translate_field(category, field_mapping)}")
                for subcategory, value in subcategories.items():
                    if value:
                        if highlight_word and highlight_word.lower() in value.lower():
                            value = value.replace(highlight_word, f"<b><span style='color: #ff4b4b;'>{highlight_word}</span></b>")
                        st.markdown(f"**{translate_field(subcategory, field_mapping)}**: {value}", unsafe_allow_html=True)
            elif isinstance(subcategories, list):
                st.markdown(f"##### {translate_field(category, field_mapping)}")
                uniq_kw_list = []
                uniq_desc_list = []
                for item in subcategories:
                    uniq_kw = item.get("uniq_kw", "")
                    uniq_desc = item.get("uniq_desc", "")
                    if highlight_word:
                        uniq_kw = uniq_kw.replace(highlight_word, f"<b><span style='color: #ff4b4b;'>{highlight_word}</span></b>")
                        uniq_desc = uniq_desc.replace(highlight_word, f"<b><span style='color: #ff4b4b;'>{highlight_word}</span></b>")
                    uniq_kw_list.append(uniq_kw)
                    uniq_desc_list.append(uniq_desc)
                uniq_kw_str = ', '.join(uniq_kw_list)
                uniq_desc_str = '<br>'.join(uniq_desc_list)
                st.markdown(f"**{translate_field('uniq_kw', field_mapping)}**: {uniq_kw_str}", unsafe_allow_html=True)
                st.markdown(f"**{translate_field('uniq_desc', field_mapping)}**:<br>{uniq_desc_str}", unsafe_allow_html=True)
            else:
                if subcategories:
                    value = subcategories
                    if highlight_word and highlight_word.lower() in value.lower():
                        value = value.replace(highlight_word, f"<b><span style='color: #ff4b4b;'>{highlight_word}</span></b>")
                    st.markdown(f"**{translate_field(category, field_mapping)}**: {value}", unsafe_allow_html=True)

    def render_section(data, field, field_mapping, highlight_word=None):
        section_data = get_nested_value(data, field.split('.'))
        
        if section_data is None:
            st.write(f"{translate_field(field, field_mapping)}에 대한 데이터가 없습니다.")
            return

        if isinstance(section_data, list):
            table = render_table(section_data, field_mapping, title=field, highlight_word=highlight_word)
            st.markdown(table, unsafe_allow_html=True)
        elif isinstance(section_data, dict):
            render_overview(section_data, field_mapping, highlight_word=highlight_word)
        else:
            cell_value = section_data
            if highlight_word and highlight_word.lower() in cell_value.lower():
                cell_value = cell_value.replace(highlight_word, f"<b><span style='color: #ff4b4b;'>{highlight_word}</span></b>")
            st.markdown(f"{cell_value}", unsafe_allow_html=True)

    def render_canvas_image(doc_id):
        index_name = "business_plan"

        fields = {
            "key_part_kw": ["business_canvas", "key_part", "key_part_kw"],
            "key_act_kw": ["business_canvas", "key_act", "key_act_kw"],
            "val_prop_kw": ["business_canvas", "val_prop", "val_prop_kw"],
            "cust_rel_kw": ["business_canvas", "cust_rel", "cust_rel_kw"],
            "cust_seg_kw": ["business_canvas", "cust_seg", "cust_seg_kw"],
            "key_res_kw": ["business_canvas", "key_res", "key_res_kw"],
            "chn_kw": ["business_canvas", "chn", "chn_kw"],
            "cost_str_kw": ["business_canvas", "cost_str", "cost_str_kw"],
            "rev_streams_kw": ["business_canvas", "rev_streams", "rev_streams_kw"]
        }

        data = {key: set() for key in fields}

        try:
            response = es.get(index=index_name, id=doc_id)

            source = response['_source']
            for key, path in fields.items():
                current = source
                try:
                    for p in path:
                        if isinstance(current, list):
                            for item in current:
                                current = item[p]
                                if isinstance(current, list):
                                    data[key].update(current)
                                else:
                                    data[key].add(current)
                        else:
                            current = current[p]
                    if isinstance(current, list):
                        data[key].update(current)
                    else:
                        data[key].add(current)
                except (KeyError, TypeError, IndexError) as e:
                    logging.warning(f"Field {path} not found in document ID {doc_id}: {e}")
                    continue

        except Exception as e:
            logging.error(f"Error: {e}")

        final_data = {key: '\n'.join(value) for key, value in data.items()}

        image_path = 'BMC.png'
        image = Image.open(image_path).convert("RGB")
        image = image.resize((3000, 2000), Image.LANCZOS)

        draw = ImageDraw.Draw(image)

        font_path = 'Pretendard-Regular.ttf'
        font = ImageFont.truetype(font_path, 35)

        positions = {
            "key_part_kw": (170, 280),
            "key_act_kw": (695, 280),
            "val_prop_kw": (1230, 280),
            "cust_rel_kw": (1790, 280),
            "cust_seg_kw": (2380, 280),
            "key_res_kw": (695, 870),
            "chn_kw": (1790, 870),
            "cost_str_kw": (170, 1450),
            "rev_streams_kw": (1540, 1450)
        }

        for section, text in final_data.items():
            position = positions[section]
            draw.text(position, text, fill="black", font=font)

        st.image(image, caption='Business Model Canvas', use_column_width=True)

    def display_section(data, section, field_mapping, highlight_word=None):
        section_fields = {
            "개요": [
                "overview.prod_serv_sum",
                "overview.motivation.reason",
                "overview.motivation.market_needs",
                "overview.motivation.vision",
                "overview.uniq"
            ],
            "캔버스모델 요약": [],
            "캔버스모델 상세": [
                "business_canvas.cust_seg",
                "business_canvas.val_prop",
                "business_canvas.chn",
                "business_canvas.cust_rel",
                "business_canvas.rev_streams",
                "business_canvas.key_res",
                "business_canvas.key_act",
                "business_canvas.key_part",
                "business_canvas.cost_str"
            ],
            "요약 설명": [
                "detail_desc"
            ]
        }

        if section == "개요":
            render_overview(data['_source'], field_mapping, highlight_word=highlight_word)
        elif section == "캔버스모델 요약":
            render_canvas_image(data['_id'])
        elif section == "요약 설명":
            render_section(data['_source'], "detail_desc", field_mapping, highlight_word=highlight_word)
        elif section == "캔버스모델 상세":
            col1, col2, col3 = st.columns(3)
            selected_fields = []
            for i, field in enumerate(section_fields[section]):
                col = col1 if i % 3 == 0 else col2 if i % 3 == 1 else col3
                if col.checkbox(translate_field(field, field_mapping), key=field):
                    selected_fields.append(field)

            if selected_fields:
                for field in selected_fields:
                    render_section(data['_source'], field, field_mapping, highlight_word=highlight_word)

    def search_callback():
        st.session_state.search_word = st.session_state.search_input
        st.session_state.selected_industry = None
        st.session_state.selected_item = None
    
    search_word = st.sidebar.text_input("사업기획서 관련 단어를 입력해주세요", key='search_input', on_change=search_callback)
    
    if 'search_word' in st.session_state:
        search_word = st.session_state['search_word']
        industry_mapping = load_json('industry_mapping.json')
        if industry_mapping is None:
            return

        documents = get_documents_by_search_word("business_plan", search_word=search_word)
        if documents is None:
            return

        if not documents:
            st.write("검색 결과가 없습니다.")
            return

        classified_documents = classify_documents_by_industry(documents, industry_mapping)

        if classified_documents:
            if 'selected_industry' not in st.session_state or st.session_state.selected_industry is None or st.session_state.selected_industry not in classified_documents:
                st.session_state.selected_industry = list(classified_documents.keys())[0]
            selected_industry = st.sidebar.selectbox(
                "찾고자 하는 산업을 선택해주세요",
                list(classified_documents.keys()),
                index=list(classified_documents.keys()).index(st.session_state['selected_industry'])
            )
            st.session_state['selected_industry'] = selected_industry

            documents = classified_documents[selected_industry]

            field_mapping = load_json('field_mapping.json')
            if field_mapping is None:
                return

            if documents:
                filtered_documents = [doc for doc in documents if search_word.lower() in doc['_source'].get('item_kw', '').lower() or search_word.lower() in doc['_source'].get('detail_desc', '').lower()]
                if filtered_documents:
                    documents = filtered_documents

                item_names = [doc['_source']['item_kw'] for doc in documents]
                if 'selected_item' not in st.session_state or st.session_state.selected_item is None or st.session_state.selected_item not in item_names:
                    st.session_state['selected_item'] = item_names[0]

                selected_item = st.sidebar.selectbox(
                    "아이템을 선택해주세요",
                    item_names,
                    index=item_names.index(st.session_state['selected_item'])
                )
                st.session_state['selected_item'] = selected_item
                
                if selected_item:
                    selected_document = next(doc for doc in documents if doc['_source']['item_kw'] == selected_item)
                    
                    section = st.sidebar.radio(
                        "섹션을 선택해주세요",
                        ["개요", "캔버스모델 요약", "캔버스모델 상세", "요약 설명"]
                    )
                    
                    display_section(selected_document, section, field_mapping, highlight_word=search_word)
            else:
                st.write("해당 산업 코드에 대한 문서가 없습니다.")

if __name__ == "__main__":
    main()

