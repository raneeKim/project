import openai
from datetime import datetime
import json
import os
import streamlit as st
from dotenv import load_dotenv

# 환경 변수 로드
load_dotenv()

def call_openai_api(conversation):
    openai.api_key = os.getenv('OPENAI_API_KEY')
    try:
        response = openai.ChatCompletion.create(
            response_format={"type": "json_object"},
            model="gpt-4o-mini",
            messages=conversation,
            temperature=0.8,
            top_p=1
        )
        return response.choices[0].message['content']
    except openai.error.OpenAIError as e:
        st.error(f"API 호출 오류: {e}.")
        return None

def clean_response(response):
    if response is None:
        return None
    # 응답에서 불필요한 백틱(```)을 제거
    response = response.strip()
    if response.startswith("```") and response.endswith("```"):
        response = response[3:-3].strip()
    return response

def generate_business_plan(industry_code, item_kw, prod_serv_sum, end_year, duration):
    current_date = datetime.now().strftime("%y%m%d%H%M%S")
    doc_id_base = industry_code + current_date

    item = {
        "doc_id": f"{doc_id_base}0001",
        "item_kw": item_kw,
        "ind_code": industry_code,
        "overview": {
            "prod_serv_sum": prod_serv_sum,
            "motivation": {
                "reason": "",
                "market_needs": "",
                "vision": ""
            },
            "uniq": {},
            "market_con": {}
        },
        "business_canvas": {
            "cust_seg": {},
            "val_prop": {},
            "chn": {},
            "cust_rel": {},
            "rev_streams": {},
            "key_res": {},
            "key_act": {},
            "key_part": {},
            "cost_str": {}
        }
    }

    # 비즈니스 캔버스 항목 생성
    canvas_questions = {
        "motivation": "다음 질문에 답변해주세요. {item_name}에 대한 창업을 계획하게 된 동기는 무엇인가요? 보고서 형식의 문체로 작성해주세요. 응답 형식은 JSON 형식으로 해주세요. 예: 'motivation': {{ 'reason': '동기 이유', 'market_needs': '시장 필요성', 'vision': '비전' }}",
        "uniq": "{item_name}(이)가 어떤 특징 혹은 차별점을 가지고 있는지, 보고서 형식의 문체로 JSON 형식으로 3가지 이상 작성해주세요. 예: 'uniq': {{ 'uniq_kw': '차별점 키워드', 'uniq_desc': '키워드에 대한 설명' }}",
        "cust_seg": "{item_name} 관련된 사업을 창업할 예정입니다. 비즈니스 모델 캔버스를 작성하기 위해 이 사업이 어떤 고객들에게 필요할지 고객 세그먼트를 작성해주세요. 보고서 형식의 문체로 JSON 형식으로 응답해주세요. 예: 'cust_seg': [ {{ 'cust_seg_kw': '고객 세그먼트 키워드', 'cust_seg_detail': '세그먼트 상세 설명' }} ]",
        "val_prop": "고객들이 이 사업을 통해 지닌 문제나 니즈에 대해 차별적으로 해결해 줄 수 있는 이점들을 무엇이 있는지 고객 세그먼트별로 여러가지 작성해주세요. 보고서 형식의 문체로 JSON 형식으로 응답해주세요. 예: 'val_prop': [ {{ 'cust_seg_kw': '고객 세그먼트 키워드', 'val_prop_kw': '가치 제안 키워드', 'val_prop_detail': '가치 제안 상세 설명' }} ]",
        "chn": "고객들이 어떤 경로를 통해 해당 사업에 노출되고, 구매할 수 있는지 고객별로 여러 가지 채널에 대해 작성해주세요. 보고서 형식의 문체로 JSON 형식으로 응답해주세요. 예: 'chn': [ {{ 'cust_seg_kw': '고객 세그먼트 키워드', 'chn_kw': '채널 키워드', 'chn_detail': '채널 상세 설명' }} ]",
        "cust_rel": "고객과의 관계 형성을 위해 무엇이 필요한지 고객별 관계 형성에 필요한 것들을 작성해주세요. 보고서 형식의 문체로 JSON 형식으로 응답해주세요. 예: 'cust_rel': [ {{ 'cust_seg_kw': '고객 세그먼트 키워드', 'cust_rel_kw': '관계 형성 키워드', 'cust_rel_detail': '관계 형성 상세 설명' }} ]",
        "rev_streams": "우리 사업이 어떤 곳에서 수익이 발생할지 JSON 형식으로 작성해주세요. 보고서 형식의 문체로 응답해주세요. 예: 'rev_streams': [ {{ 'rev_streams_kw': '수익원 키워드', 'rev_streams_detail': '수익원 상세 설명' }} ]",
        "key_res": "이 사업을 원활하게 운영하기 위해 가장 필요한 자원들이 무엇인지 JSON 형식으로 작성해주세요. 보고서 형식의 문체로 응답해주세요. 예: 'key_res': [ {{ 'key_res_kw': '자원 키워드', 'key_res_detail': '자원 상세 설명' }} ]",
        "key_act": "이 사업을 원활하게 운영하기 위해 필요한 활동들이 무엇인지 JSON 형식으로 작성해주세요. 보고서 형식의 문체로 응답해주세요. 예: 'key_act': [ {{ 'key_act_kw': '핵심 활동 키워드', 'key_act_detail': '핵심 활동 상세 설명' }} ]",
        "key_part": "우리 사업에 필요한 협업 업체 또는 파트너를 JSON 형식으로 작성해주세요. 보고서 형식의 문체로 응답해주세요. 예: 'key_part': [ {{ 'key_part_kw': '파트너 키워드', 'key_part_detail': '파트너 상세 설명' }} ]",
        "cost_str": "우리 사업에서 발생하는 비용에는 어떤 것들이 있는지 JSON 형식으로 작성해주세요. 보고서 형식의 문체로 응답해주세요. 예: 'cost_str': [ {{ 'cost_str_kw': '비용 키워드', 'cost_str_detail': '비용 상세 설명' }} ]",
        "market_con": "{item_name} 산업의 {start_year}년부터 {end_year}년까지의 연도별 허핀달-허쉬만 지수를 보여주는 데이터를 integer로 제공해주세요. 만약 수치가 없다고 하면, 그럴듯한 임의의 숫자여도 좋습니다. 보고서 형식의 문체로 응답해주세요. 예: 'market_con': [ {{ '{start_year}': '{start_year}년의 허핀달-허쉬만 지수', ... ,'{end_year}': '{end_year}년의 허핀달-허쉬만 지수' }} ]"
    }

    conversation = [
        {"role": "system", "content": "You are a business consultant tasked with creating comprehensive business plans in a report format."},
        {"role": "user", "content": f"산업 분야: {item['ind_code']}, 아이템: {item['item_kw']}"}
    ]
    
    # 각 섹션에 대해 질문을 던지고 응답을 받아 저장
    for key, question_template in canvas_questions.items():
        item_name = item["item_kw"]
        start_year = end_year - duration + 1
        question = question_template.format(item_name=item_name, start_year=start_year, end_year=end_year)

        conversation.append({"role": "user", "content": question})
        assistant_response = call_openai_api(conversation)

        # 불필요한 백틱(```) 제거
        clean_response_text = clean_response(assistant_response)

        if clean_response_text is None:
            st.error("OpenAI API 응답이 없습니다.")
            return {"error": "API 응답 없음"}

        try:
            response_data = json.loads(clean_response_text)
        except json.JSONDecodeError:
            st.error("OpenAI API 응답을 JSON으로 디코딩하는 데 실패했습니다.")
            st.error(f"API 응답: {clean_response_text}")
            return {"error": "JSON 디코딩 실패", "response": clean_response_text}

        if isinstance(response_data, dict) and key in response_data:
            if key == "motivation":
                item["overview"]["motivation"]["reason"] = response_data["motivation"].get("reason", "")
                item["overview"]["motivation"]["market_needs"] = response_data["motivation"].get("market_needs", "")
                item["overview"]["motivation"]["vision"] = response_data["motivation"].get("vision", "")
            elif key in ["uniq", "market_con"]:
                item["overview"][key] = response_data[key]
            else:
                item["business_canvas"][key] = response_data[key]
        else:
            st.error(f"Invalid response format for key {key}. Response: {response_data}")
            return {"error": "Invalid response format", "response": response_data}

    return item
