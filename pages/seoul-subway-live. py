import streamlit as st
import requests
import pandas as pd
from google import genai
from google.genai import types
import random

# Page 설정
st.set_page_config(
    page_title="서울 실시간 지하철 대시보드",
    page_icon="🚇",
    layout="wide"
)

# ------------------------------------------------------------------
# 1. 고유 스타일 및 타이틀 정의
# ------------------------------------------------------------------
st.title("🚇 서울 실시간 지하철 노선별 위치 대시보드")
st.markdown("""
이 애플리케이션은 **서울시 지하철 실시간 열차 위치 Open API** 데이터를 기반으로 작동합니다.
원하는 노선을 선택하면 현재 달리고 있는 모든 열차의 실시간 위치와 상태를 확인하고, **Gemini 2.5 Flash-lite**가 분석한 운행 리포트를 볼 수 있습니다.
""")
st.divider()

# ------------------------------------------------------------------
# 2. 사이드바 및 환경 변수 설정
# ------------------------------------------------------------------
st.sidebar.header("⚙️ 설정 및 API 키 관리")

# API Key 확인 (Streamlit Secrets 또는 사이드바 입력 가능하게 유연성 확보)
seoul_api_key = st.sidebar.text_input("서울 열린데이터광장 API Key", value="sample", type="password", 
                                      help="샘플 키 입력 시 모의 데이터로 안전하게 작동합니다.")
gemini_api_key = st.getenv("GEMINI_API_KEY") or st.sidebar.text_input("GEMINI_API_KEY (선택)", type="password")

# 노선 선택 정보
LINE_MAPPING = {
    "1호선": "1호선", "2호선": "2호선", "3호선": "3호선", "4호선": "4호선",
    "5호선": "5호선", "6호선": "6호선", "7호선": "7호선", "8호선": "8호선", "9호선": "9호선",
    "수인분당선": "수인분당선", "경의중앙선": "경의중앙선", "신분당선": "신분당선"
}
selected_line = st.sidebar.selectbox("조회할 지하철 노선을 선택하세요", list(LINE_MAPPING.keys()))

# ------------------------------------------------------------------
# 3. 데이터 수집 함수 (API 호출 및 예외 처리)
# ------------------------------------------------------------------
def get_mock_data(line_name):
    """API 키가 없거나 오류 시 작동할 고품질 가상 데이터 생성기"""
    stations = ["서울역", "시청", "종각", "종로3가", "종로5가", "동대문", "신설동", "제기동", "청량리"] if line_name == "1호선" else ["강남", "역삼", "선릉", "삼성", "종합운동장", "잠실", "성수", "홍대입구", "신도림"]
    mock_list = []
    for i in range(random.randint(8, 15)):
        mock_list.append({
            "trainNo": f"{random.randint(1000, 9999)}",
            "statnNm": random.choice(stations),
            "updnLine": random.choice(["0", "1"]),  # 0: 상행/내선, 1: 하행/외선
            "directAt": random.choice(["0", "1"]),  # 0: 일반, 1: 급행
            "trainSttus": random.choice(["0", "1", "2"]) # 0: 진입, 1: 도착, 2: 출발
        })
    return mock_list

@st.cache_data(ttl=10) # 10초간 캐싱하여 무분별한 API 호출 방지
def fetch_subway_positions(api_key, line_name):
    if api_key == "sample" or not api_key:
        return get_mock_data(line_name)
    
    url = f"http://swopenAPI.seoul.go.kr/api/subway/{api_key}/json/realtimePosition/0/100/{line_name}"
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            data = response.json()
            if "realtimePositionList" in data:
                return data["realtimePositionList"]
            else:
                st.warning(f"⚠️ 서울시 API 메시지: {data.get('RESULT', {}).get('message', '데이터가 없습니다.')}. 샘플 데이터로 대체합니다.")
                return get_mock_data(line_name)
        else:
            st.error(f"API 요청 실패 (Status Code: {response.status_code})")
            return get_mock_data(line_name)
    except Exception as e:
        st.error(f"네트워크 오류가 발생하여 샘플 데이터로 안전 모드 전환합니다: {e}")
        return get_mock_data(line_name)

# ------------------------------------------------------------------
# 4. 데이터 로드 및 UI 렌더링
# ------------------------------------------------------------------
with st.spinner("🔄 실시간 지하철 위치 데이터를 가져오는 중입니다..."):
    raw_data = fetch_subway_positions(seoul_api_key, selected_line)

if raw_data:
    df = pd.DataFrame(raw_data)
    
    # 가독성을 위한 데이터 매핑 가공
    df['상하행'] = df['updnLine'].map({'0': '상행/내선', '1': '하행/외선'}).fillna('정보없음')
    df['열차종류'] = df['directAt'].map({'0': '일반', '1': '급행'}).fillna('일반')
    df['상태'] = df['trainSttus'].map({'0': '역 진입', '1': '역 도착', '2': '출발/운행중'}).fillna('운행중')
    
    # 정제된 데이터프레임 구성
    display_df = df[['trainNo', 'statnNm', '상하행', '열차종류', '상태']].rename(columns={
        'trainNo': '열차 번호',
        'statnNm': '현재/정차 역',
    })
    
    # 대시보드 상단 요약 지표 (Metrics)
    total_trains = len(df)
    up_trains = len(df[df['updnLine'] == '0'])
    down_trains = len(df[df['updnLine'] == '1'])
    express_trains = len(df[df['directAt'] == '1'])
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric(label="📍 총 운행 열차 수", value=f"{total_trains}대")
    with col2:
        st.metric(label="🔼 상행/내선", value=f"{up_trains}대")
    with col3:
        st.metric(label="🔽 하행/외선", value=f"{down_trains}대")
    with col4:
        st.metric(label="⚡ 급행 열차", value=f"{express_trains}대")
        
    st.subheader(f"📊 {selected_line} 실시간 운행 현황 리스트")
    st.dataframe(display_df, use_container_width=True, hide_index=True)

    # ------------------------------------------------------------------
    # 5. Gemini-2.5-flash-lite를 활용한 AI 분석 리포트 기능
    # ------------------------------------------------------------------
    st.divider()
    st.subheader("🤖 Gemini AI 실시간 노선 진단 리포트")
    
    if gemini_api_key:
        try:
            # google-genai SDK 규격에 맞추어 클라이언트 초기화
            client = genai.Client(api_key=gemini_api_key)
            
            # AI에게 전달할 데이터 텍스트 포맷화
            data_summary = display_df.to_string(index=False)
            
            prompt = f"""
            너는 서울시 교통 분석 전문가야. 아래 제공된 데이터는 현재 실시간 서울 지하철 {selected_line}의 운행 정보 데이터다.
            이 데이터를 분석해서 승객들을 위한 브리핑 리포트를 한글로 간결하고 친근하게 작성해줘.

            [지하철 데이터]
            {data_summary}

            [작성 지침]
            1. 현재 노선이 상하행 균형 있게 잘 운행되고 있는지 평가해줘.
            2. 특정 역에 열차가 몰려있거나 급행 열차의 비율이 적절한지 분석해줘.
            3. 출퇴근 시간이나 평시 상황을 가정하여 승객들이 주의해야 할 팁을 한 줄 요약으로 포함해줘.
            4. 너무 딱딱하지 않게 이모지를 섞어서 친절한 톤으로 답변해줘.
            """
            
            with st.spinner("🧠 Gemini가 실시간 운행 데이터를 분석하는 중..."):
                response = client.models.generate_content(
                    model='gemini-2.5-flash-lite',
                    contents=prompt,
                )
                st.info(response.text)
                
        except Exception as e:
            st.error(f"❌ Gemini API 요청 중 오류가 발생했습니다: {e}")
            st.caption("Tip: Secrets 설정에 `GEMINI_API_KEY`가 올바르게 등록되었는지 확인해 주세요.")
    else:
        st.warning("💡 사이드바 혹은 환경 변수에 `GEMINI_API_KEY`를 설정하시면 AI가 실시간 지하철 상황을 요약 브리핑해 줍니다.")

else:
    st.error("데이터를 불러오지 못했습니다. 잠시 후 다시 시도해 주세요.")
