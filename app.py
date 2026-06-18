import streamlit as st
from collections import deque
from datetime import datetime, timedelta

st.set_page_config(
    page_title="스마트 지하철 경로 추천기",
    page_icon="🚇",
    layout="wide"
)

# -------------------------
# 예제 지하철 데이터
# -------------------------

subway_lines = {
    "1호선": [
        "서울역",
        "시청",
        "종각",
        "종로3가",
        "동대문",
        "신설동"
    ],
    "2호선": [
        "시청",
        "을지로입구",
        "을지로3가",
        "동대문역사문화공원",
        "신당",
        "왕십리"
    ],
    "3호선": [
        "종로3가",
        "을지로3가",
        "충무로",
        "약수",
        "옥수"
    ]
}

# -------------------------
# 그래프 생성
# -------------------------

graph = {}
station_lines = {}

for line, stations in subway_lines.items():

    for station in stations:
        graph.setdefault(station, [])
        station_lines.setdefault(station, []).append(line)

    for i in range(len(stations) - 1):
        a = stations[i]
        b = stations[i + 1]

        graph[a].append(b)
        graph[b].append(a)

all_stations = sorted(graph.keys())

# -------------------------
# BFS 최단경로
# -------------------------

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

            for neighbor in graph[node]:
                new_path = list(path)
                new_path.append(neighbor)
                queue.append(new_path)

    return None

# -------------------------
# 환승 계산
# -------------------------

def count_transfers(route):
    if len(route) < 2:
        return 0

    current_line = None
    transfers = 0

    for i in range(len(route) - 1):

        s1 = route[i]
        s2 = route[i + 1]

        common = set(station_lines[s1]) & set(station_lines[s2])

        if not common:
            continue

        line = list(common)[0]

        if current_line is None:
            current_line = line

        elif current_line != line:
            transfers += 1
            current_line = line

    return transfers

# -------------------------
# UI
# -------------------------

st.title("🚇 스마트 지하철 경로 추천기")

st.markdown(
    """
    출발역과 도착역을 선택하면
    최적 지하철 경로와 예상 도착 시간을 안내합니다.
    """
)

col1, col2 = st.columns(2)

with col1:
    start_station = st.selectbox(
        "출발역",
        all_stations
    )

with col2:
    end_station = st.selectbox(
        "도착역",
        all_stations,
        index=min(1, len(all_stations)-1)
    )

if st.button("경로 찾기", use_container_width=True):

    try:

        if start_station == end_station:
            st.warning("출발역과 도착역이 같습니다.")
            st.stop()

        route = find_route(start_station, end_station)

        if not route:
            st.error("경로를 찾을 수 없습니다.")
            st.stop()

        station_count = len(route) - 1

        # 역간 평균 2분
        travel_time = station_count * 2

        transfer_count = count_transfers(route)

        arrival_time = datetime.now() + timedelta(
            minutes=travel_time
        )

        st.success("경로 탐색 완료")

        st.subheader("추천 경로")

        st.write(" ➜ ".join(route))

        c1, c2, c3 = st.columns(3)

        with c1:
            st.metric(
                "정차역 수",
                station_count
            )

        with c2:
            st.metric(
                "환승 횟수",
                transfer_count
            )

        with c3:
            st.metric(
                "예상 소요시간",
                f"{travel_time}분"
            )

        st.subheader("도착 예정 정보")

        st.info(
            f"""
현재 시각 : {datetime.now().strftime('%H:%M')}

도착까지 : {travel_time}분

예상 도착 시각 : {arrival_time.strftime('%H:%M')}
"""
        )

    except Exception as e:
        st.error(f"오류가 발생했습니다: {e}")

st.divider()

st.caption(
    "예제용 내장 노선 데이터 사용"
)
