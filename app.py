import streamlit as st
from collections import deque
from datetime import datetime, timedelta

st.set_page_config(
    page_title="CrowdMetro",
    page_icon="🚇",
    layout="wide"
)

# ---------------------------------
# 지하철 데이터
# ---------------------------------

subway_lines = {
    "1호선": [
        "서울역",
        "시청",
        "종각",
        "종로3가",
        "동대문"
    ],
    "2호선": [
        "시청",
        "을지로입구",
        "을지로3가",
        "동대문역사문화공원",
        "신당"
    ],
    "3호선": [
        "종로3가",
        "을지로3가",
        "충무로",
        "약수",
        "옥수"
    ]
}

# ---------------------------------
# 최초 실행
# ---------------------------------

if "crowd_data" not in st.session_state:
    st.session_state.crowd_data = {
        "1호선": [2, 2, 3],
        "2호선": [4, 5, 4],
        "3호선": [2, 3, 2]
    }

# ---------------------------------
# 그래프 생성
# ---------------------------------

graph = {}
station_lines = {}

for line, stations in subway_lines.items():

    for station in stations:
        graph.setdefault(station, [])
        station_lines.setdefault(station, []).append(line)

    for i in range(len(stations)-1):
        a = stations[i]
        b = stations[i+1]

        graph[a].append(b)
        graph[b].append(a)

stations = sorted(graph.keys())

# ---------------------------------
# 경로 찾기
# ---------------------------------

def find_route(start, end):

    queue = deque([[start]])
    visited = set()

    while queue:

        path = queue.popleft()
        node = path[-1]

        if node == end:
            return path

        if node not in visited:
            visited.add(node)

            for next_station in graph[node]:
                new_path = list(path)
                new_path.append(next_station)
                queue.append(new_path)

    return None

# ---------------------------------
# 혼잡도 계산
# ---------------------------------

def get_avg(line):
    data = st.session_state.crowd_data[line]
    return round(sum(data)/len(data), 1)

# ---------------------------------
# 색상
# ---------------------------------

def crowd_color(score):

    if score <= 2:
        return "green"

    elif score == 3:
        return "orange"

    else:
        return "red"

# ---------------------------------
# 제목
# ---------------------------------

st.title("🚇 CrowdMetro")
st.subheader("실시간 지하철 혼잡도 공유 서비스")

# ---------------------------------
# 현재 혼잡도
# ---------------------------------

st.header("📊 노선별 혼잡도")

cols = st.columns(3)

for idx, line in enumerate(subway_lines.keys()):

    avg = get_avg(line)
    color = crowd_color(round(avg))

    with cols[idx]:

        st.markdown(
            f"""
            <div style="
            background-color:{color};
            padding:20px;
            border-radius:10px;
            color:white;
            text-align:center;
            ">
            <h3>{line}</h3>
            <h1>{avg}/5</h1>
            </div>
            """,
            unsafe_allow_html=True
        )

# ---------------------------------
# 제보하기
# ---------------------------------

st.header("🙋 현재 탑승 중이라면 혼잡도 제보")

line_select = st.selectbox(
    "노선 선택",
    list(subway_lines.keys())
)

score = st.slider(
    "혼잡도 선택",
    1,
    5,
    3
)

if st.button("혼잡도 등록"):

    try:
        st.session_state.crowd_data[line_select].append(score)

        st.success(
            f"{line_select} 혼잡도 {score} 등록 완료"
        )

    except Exception as e:
        st.error(e)

# ---------------------------------
# 경로 추천
# ---------------------------------

st.header("🗺️ 경로 추천")

col1, col2 = st.columns(2)

with col1:
    start_station = st.selectbox(
        "출발역",
        stations
    )

with col2:
    end_station = st.selectbox(
        "도착역",
        stations,
        index=min(1, len(stations)-1)
    )

if st.button("경로 찾기"):

    try:

        if start_station == end_station:
            st.warning(
                "출발역과 도착역이 같습니다."
            )
            st.stop()

        route = find_route(
            start_station,
            end_station
        )

        if route is None:
            st.error("경로 없음")
            st.stop()

        station_count = len(route)-1

        travel_time = station_count * 2

        arrival = (
            datetime.now()
            + timedelta(minutes=travel_time)
        )

        st.success("추천 경로")

        st.write(
            " ➜ ".join(route)
        )

        c1, c2, c3 = st.columns(3)

        c1.metric(
            "이동역 수",
            station_count
        )

        c2.metric(
            "예상 소요시간",
            f"{travel_time}분"
        )

        c3.metric(
            "도착 예정",
            arrival.strftime("%H:%M")
        )

        # 혼잡도 낮은 노선 추천

        best_line = min(
            subway_lines.keys(),
            key=lambda x: get_avg(x)
        )

        st.info(
            f"""
🚇 가장 덜 붐비는 노선 추천

{best_line}

현재 평균 혼잡도 : {get_avg(best_line)}
"""
        )

    except Exception as e:
        st.error(
            f"오류 발생 : {e}"
        )

# ---------------------------------
# 다음 열차 정보
# ---------------------------------

st.header("🚆 다음 열차 혼잡도 예측")

for line in subway_lines.keys():

    score = get_avg(line)

    color = crowd_color(round(score))

    wait = 2 + list(subway_lines.keys()).index(line) * 3

    st.markdown(
        f"""
<div style="
background:{color};
padding:15px;
border-radius:10px;
color:white;
margin-bottom:10px;
">
<b>{line}</b><br>
도착 예정 : {wait}분 후<br>
혼잡도 : {score}/5
</div>
""",
        unsafe_allow_html=True
    )

st.caption(
    "혼잡도는 사용자 제보 평균값 기반입니다."
)
