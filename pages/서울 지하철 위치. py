import streamlit as st
import google.generativeai as genai
import requests

# 1. 페이지 설정
st.set_page_config(page_title="서울 지하철 실시간 안내원", page_icon="🚇", layout="centered")
st.title("🚇 서울 지하철 실시간 안내원")
st.caption("궁금한 지하철역 이름을 말씀하시면 실시간 열차 정보를 알려드려요! (예: '강남역', '홍대입구역 어떻게 돼?')")

# 2. Streamlit Secrets에서 API 키들 안전하게 불러오기
if "GEMINI_API_KEY" in st.secrets and "SEOUL_SUBWAY_API_KEY" in st.secrets:
    gemini_key = st.secrets["GEMINI_API_KEY"]
    seoul_api_key = st.secrets["SEOUL_SUBWAY_API_KEY"]
    genai.configure(api_key=gemini_key)
else:
    st.error("🔑 API 키(GEMINI_API_KEY 또는 SEOUL_SUBWAY_API_KEY)가 Secrets에 설정되지 않았습니다.")
    st.stop()

# 3. 실시간 지하철 정보를 가져오는 도구 함수 정의
def get_realtime_subway(station_name):
    """서울 열린데이터광장 API를 이용해 특정 역의 실시간 도착 정보를 가져옵니다."""
    # 역 이름 뒷글자 '역' 떼기 (API 규격 맞춤: '강남역' -> '강남')
    clean_name = station_name.replace("역", "").strip()
    
    url = f"http://swopenAPI.seoul.go.kr/api/subway/{seoul_api_key}/json/realtimeStationArrival/0/10/{clean_name}"
    
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            data = response.json()
            # 데이터가 정상적으로 있을 경우 정보 추출
            if "realtimeArrivalList" in data:
                arrivals = data["realtimeArrivalList"]
                info_list = []
                for item in arrivals:
                    info = {
                        "노선": item.get("subwayNm", "알수없음"),
                        "방향": item.get("trainLineNm", "알수없음"),
                        "현재위치/상태": item.get("arvlMsg2", "정보없음"),
                        "열차종류": item.get("btrainSttus", "일반"),
                        "도착예정시각": item.get("arvlMsg3", "")
                    }
                    info_list.append(info)
                return info_list
            else:
                return "해당 역의 실시간 열차 운행 정보가 현재 없습니다. 역 이름이 정확한지 확인해 주세요."
        else:
            return f"지하철 API 호출 실패 (상태코드: {response.status_code})"
    except Exception as e:
        return f"지하철 데이터를 가져오는 중 오류 발생: {e}"

# 4. 채팅 기록 초기화
if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "assistant", 
            "content": "안녕하세요! 서울 지하철 실시간 안내원입니다. 어떤 역의 열차 위치가 궁금하신가요? 쉼표나 조사 없이 역 이름만 말씀하셔도 바로 찾아드릴게요! 🚉"
        }
    ]

# 5. 이전 채팅 기록 출력
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 6. 사용자 입력 처리
if user_input := st.chat_input("역 이름을 입력하세요 (예: 서울역, 성수)")):
    st.chat_message("user").markdown(user_input)
    st.session_state.messages.append({"role": "user", "content": user_input})

    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        
        try:
            with st.spinner("지하철 실시간 위치 데이터를 조회하고 답변을 정리 중입니다... 🔍"):
                
                # 7. Gemini에게 사용자가 어떤 역을 물어봤는지 의도 파악 요청 (역 이름만 추출)
                intent_model = genai.GenerativeModel(model_name="gemini-2.5-flash-lite")
                prompt_intent = (
                    f"사용자의 질문: '{user_input}'. "
                    "이 문장에서 사용자가 찾고자 하는 서울 지하철역 이름 딱 하나만 추출해서 답변해줘. "
                    "뒤에 '역'은 빼고 '강남', '홍대입구', '신도림' 같이 핵심 명사만 출력해줘. 역 이름이 없으면 '없음'이라고만 답해줘."
                )
                detected_station = intent_model.generate_content(prompt_intent).text.strip()
                
                # 8. 역 이름이 파악되면 실시간 API 호출
                subway_raw_data = ""
                if "없음" not in detected_station and len(detected_station) < 10:
                    subway_raw_data = get_realtime_subway(detected_station)
                else:
                    subway_raw_data = "사용자가 명확한 역 이름을 언급하지 않았거나 해석하기 어렵습니다."

                # 9. 실시간 API 원본 데이터를 Gemini에게 넘겨 가독성 좋은 답변으로 재구성
                main_model = genai.GenerativeModel(
                    model_name="gemini-2.5-flash-lite",
                    system_instruction=(
                        "당신은 친절하고 명쾌한 서울 지하철 실시간 안내원입니다. "
                        "제공된 실시간 지하철 API 결과 데이터를 바탕으로 사용자가 보기 편하게 답변을 요약 및 재구성해 주세요. "
                        "노선별, 상/하행(내선/외선)별로 나누어 가독성 좋게 Bullet point 나 표를 활용해 정리해 주면 좋습니다. "
                        "만약 API 결과가 에러 메시지거나 데이터가 없다면, 정중하게 역 이름을 다시 확인해 달라고 안내해 주세요."
                    )
                )
                
                # 대화 맥락 유지 처리
                history = []
                for msg in st.session_state.messages[:-1]:
                    role = "user" if msg["role"] == "user" else "model"
                    history.append({"role": role, "parts": [msg["content"]]})
                
                chat = main_model.start_chat(history=history)
                
                # API 데이터와 함께 최종 답변 생성 요청
                final_prompt = f"사용자 질문: {user_input}\n\n[실시간 수집된 지하철 데이터]\n{str(subway_raw_data)}\n\n이 데이터를 기반으로 사용자에게 최종 안내 답변을 작성해줘."
                response = chat.send_message(final_prompt)
                
                ai_response = response.text
                message_placeholder.markdown(ai_response)
                
                st.session_state.messages.append({"role": "assistant", "content": ai_response})
                
        except Exception as e:
            message_placeholder.error(f"❌ 시스템 작동 중 오류가 발생했습니다: {e}")
