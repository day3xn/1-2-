import streamlit as st
import pandas as pd
import random

st.set_page_config(
    page_title="Subway Live Crowd",
    page_icon="🚇",
    layout="wide"
)

# -----------------------
# 초기 데이터
# -----------------------

if "crowd_data" not in st.session_state:
    st.session_state.crowd_data = {
        "1호선": [2, 2, 3],
        "2호선": [4, 4, 5],
        "3호선": [2, 3, 2],
        "4호선": [3, 3, 4],
        "5호선": [1, 2, 2],
        "6호선": [2, 2, 3],
        "7호선": [4, 3, 4],
        "8호선": [2, 2, 2],
        "9호선": [5, 4, 5],
        "신분당선": [2, 2, 1],
        "공항철도": [1, 2, 1]
    }

# -----------------------
# 함수
# -----------------------

def avg_crowd(line):
    values = st.session_state.crowd_data[line]
    return round(sum(values) / len(values), 1)

def crowd_color(score):
    if score <= 2:
        return "green"
    elif score == 3:
        return "orange"
    else:
        return "red"

def crowd_text(score):
    if score <= 2:
        return "여유"
    elif score == 3:
        return "보통"
    else:
        return "혼잡"

# -----------------------
# 제목
# -----------------------

st.title("🚇 Subway Live Crowd")
st.caption("실시간 사용자 참여형 지하철 혼잡도 공유 서비스")

# -----------------------
# 경로 검색
# -----------------------

st.header("📍 출발지 / 도착지 검색")

col1, col2 = st.columns(2)

with col1:
    start_station = st.text_input("출발역")

with col2:
    end_station = st.text_input("도착역")

if start_station and end_station:

    route_data = []

    for line in st.session_state.crowd_data.keys():

        crowd = avg_crowd(line)

        travel_time = random.randint(15, 50)

        route_data.append({
            "노선": line,
            "예상시간(분)": travel_time,
            "평균혼잡도": crowd
        })

    route_df = pd.DataFrame(route_data)

    route_df = route_df.sort_values(
        by=["평균혼잡도", "예상시간(분)"]
    )

    st.subheader("🚆 추천 노선")

    st.dataframe(
        route_df,
        use_container_width=True
    )

# -----------------------
# 도착 예정 열차
# -----------------------

st.header("⏱️ 도착 예정 열차")

arrival_data = []

for line in st.session_state.crowd_data.keys():

    arrival_data.append({
        "노선": line,
        "도착예정(분)": random.randint(1, 10),
        "혼잡도": avg_crowd(line)
    })

arrival_df = pd.DataFrame(arrival_data)

st.dataframe(
    arrival_df,
    use_container_width=True
)

# -----------------------
# 혼잡도 현황
# -----------------------

st.header("📊 실시간 혼잡도")

cols = st.columns(3)

for idx, line in enumerate(st.session_state.crowd_data.keys()):

    score = avg_crowd(line)

    color = crowd_color(round(score))

    with cols[idx % 3]:

        st.markdown(
            f"""
            <div style="
                background:{color};
                padding:15px;
                border-radius:10px;
                color:white;
                margin-bottom:10px;
            ">
            <h4>{line}</h4>
            <h2>{score}</h2>
            <p>{crowd_text(round(score))}</p>
            </div>
            """,
            unsafe_allow_html=True
        )

# -----------------------
# 사용자 입력
# -----------------------

st.header("🙋 혼잡도 제보")

selected_line = st.selectbox(
    "현재 탑승 노선",
    list(st.session_state.crowd_data.keys())
)

user_score = st.slider(
    "현재 얼마나 붐비나요?",
    1,
    5,
    3
)

if st.button("혼잡도 등록"):

    st.session_state.crowd_data[selected_line].append(user_score)

    st.success(
        f"{selected_line} 혼잡도 등록 완료!"
    )

# -----------------------
# 전체 현황
# -----------------------

st.header("📈 전체 혼잡도 순위")

ranking = []

for line in st.session_state.crowd_data.keys():

    ranking.append(
        {
            "노선": line,
            "평균혼잡도": avg_crowd(line)
        }
    )

ranking_df = pd.DataFrame(ranking)

ranking_df = ranking_df.sort_values(
    by="평균혼잡도",
    ascending=False
)

st.dataframe(
    ranking_df,
    use_container_width=True
)

st.info(
    "실제 서비스에서는 공공데이터포털 지하철 실시간 도착정보 API와 연동하여 운영할 수 있습니다."
)
