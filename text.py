# app.py
# -*- coding: utf-8 -*-
"""
날씨와 기분을 입력(또는 API로 가져오기)하면 음식을 추천해 주는 Streamlit 앱.
- 수동/자동(OpenWeather) 날씨 입력 지원
- 기분, 예산, 식단(비건/베지), 매운맛 선호 반영
- 추천 사유와 함께 Top-N 결과 출력

실행 방법:
1) pip install streamlit requests
2) streamlit run app.py

※ OpenWeather를 쓰려면: https://openweathermap.org/ 에서 API 키 발급 후 앱에서 입력
"""

from __future__ import annotations
import os
import random
from datetime import datetime
from typing import Dict, List, Tuple

import requests
import streamlit as st

st.set_page_config(page_title="🍽️ 날씨&기분 음식 추천", page_icon="🍜", layout="wide")

# -----------------------------
# 유틸
# -----------------------------
@st.cache_data(show_spinner=False)
def get_weather_from_openweather(city: str, api_key: str, units: str = "metric") -> Tuple[str, float]:
    """OpenWeather에서 현재 날씨(메인 상태)와 기온(°C)을 가져온다.
    반환: (weather_main, temp_c)
    예외 발생 시 ValueError
    """
    url = "https://api.openweathermap.org/data/2.5/weather"
    params = {"q": city, "appid": api_key, "units": units, "lang": "kr"}
    r = requests.get(url, params=params, timeout=10)
    if r.status_code != 200:
        raise ValueError(f"API 오류: {r.status_code} {r.text[:120]}")
    data = r.json()
    weather_main = data["weather"][0]["main"]  # Clear, Clouds, Rain, Snow...
    temp_c = float(data["main"]["temp"])
    return weather_main, temp_c


def categorize_temp(temp_c: float) -> str:
    if temp_c <= 10:
        return "cold"
    if temp_c <= 18:
        return "cool"
    if temp_c <= 24:
        return "mild"
    if temp_c <= 30:
        return "warm"
    return "hot"


def weather_flags(weather_main: str) -> Dict[str, bool]:
    w = weather_main.lower()
    return {
        "rainy": any(k in w for k in ["rain", "drizzle", "thunder"]),
        "snowy": "snow" in w,
        "clear": "clear" in w,
        "cloudy": "cloud" in w,
        "misty": any(k in w for k in ["mist", "haze", "fog", "smoke", "dust"]),
    }


# -----------------------------
# 메뉴 데이터(간단 규칙 기반)
# 각 항목: 이름, 태그, 식단, 예산
#   tags: {"rainy", "cold", "hot", "comfort", "celebrate", "light", "spicy", "noodles", ...}
#   diet: "any" | "vegetarian" | "vegan"
#   budget: "low" | "mid" | "high"
# -----------------------------
MENU: List[Dict] = [
    {"name": "김치찌개", "tags": {"rainy", "cold", "comfort", "spicy", "stew"}, "diet": "any", "budget": "low"},
    {"name": "된장찌개", "tags": {"rainy", "cold", "comfort", "stew"}, "diet": "vegetarian", "budget": "low"},
    {"name": "부대찌개", "tags": {"rainy", "cold", "comfort", "spicy", "stew"}, "diet": "any", "budget": "mid"},
    {"name": "순두부찌개", "tags": {"rainy", "cold", "comfort", "spicy", "stew"}, "diet": "vegetarian", "budget": "low"},
    {"name": "칼국수", "tags": {"rainy", "cool", "comfort", "noodles"}, "diet": "any", "budget": "low"},
    {"name": "잔치국수", "tags": {"mild", "comfort", "noodles"}, "diet": "vegetarian", "budget": "low"},
    {"name": "쌀국수(퍼)", "tags": {"rainy", "cool", "comfort", "light", "noodles"}, "diet": "any", "budget": "mid"},
    {"name": "비빔국수", "tags": {"warm", "hot", "spicy", "noodles", "light"}, "diet": "vegetarian", "budget": "low"},
    {"name": "냉면", "tags": {"hot", "light", "noodles"}, "diet": "any", "budget": "mid"},
    {"name": "메밀소바", "tags": {"hot", "light", "noodles"}, "diet": "vegetarian", "budget": "mid"},
    {"name": "샐러드 볼", "tags": {"hot", "warm", "light", "healthy"}, "diet": "vegan", "budget": "mid"},
    {"name": "포케(하와이안)", "tags": {"hot", "light", "healthy"}, "diet": "any", "budget": "high"},
    {"name": "비빔밥", "tags": {"mild", "comfort", "healthy"}, "diet": "vegetarian", "budget": "mid"},
    {"name": "김밥", "tags": {"mild", "light", "on-the-go"}, "diet": "vegetarian", "budget": "low"},
    {"name": "떡볶이", "tags": {"cool", "cold", "spicy", "comfort", "street"}, "diet": "vegetarian", "budget": "low"},
    {"name": "치킨", "tags": {"clear", "celebrate", "sharing"}, "diet": "any", "budget": "mid"},
    {"name": "삼겹살 구이", "tags": {"clear", "celebrate", "bbq"}, "diet": "any", "budget": "mid"},
    {"name": "스테이크", "tags": {"celebrate", "high-protein"}, "diet": "any", "budget": "high"},
    {"name": "초밥", "tags": {"celebrate", "light"}, "diet": "any", "budget": "high"},
    {"name": "파스타(크림)", "tags": {"cool", "comfort"}, "diet": "vegetarian", "budget": "mid"},
    {"name": "파스타(토마토)", "tags": {"mild", "light"}, "diet": "vegetarian", "budget": "mid"},
    {"name": "마라탕", "tags": {"cold", "spicy", "adventure"}, "diet": "any", "budget": "mid"},
    {"name": "쌈밥", "tags": {"mild", "healthy", "clear"}, "diet": "any", "budget": "mid"},
    {"name": "카레라이스", "tags": {"mild", "comfort", "spicy"}, "diet": "vegetarian", "budget": "low"},
    {"name": "카레 우동", "tags": {"cool", "comfort", "spicy", "noodles"}, "diet": "any", "budget": "mid"},
    {"name": "라멘", "tags": {"rainy", "cold", "comfort", "noodles"}, "diet": "any", "budget": "mid"},
    {"name": "토마토 해물짬뽕", "tags": {"rainy", "spicy", "noodles"}, "diet": "any", "budget": "mid"},
    {"name": "부침개+막걸리", "tags": {"rainy", "comfort", "sharing"}, "diet": "vegetarian", "budget": "low"},
    {"name": "죽(소고기/전복/야채)", "tags": {"cold", "cool", "comfort", "sick-day"}, "diet": "any", "budget": "mid"},
    {"name": "크림리조또", "tags": {"cool", "comfort"}, "diet": "vegetarian", "budget": "mid"},
    {"name": "아보카도 토스트", "tags": {"hot", "light", "healthy"}, "diet": "vegan", "budget": "mid"},
    {"name": "토마토 모짜렐라 샌드위치", "tags": {"mild", "light"}, "diet": "vegetarian", "budget": "mid"},
    {"name": "갈비탕", "tags": {"cold", "comfort", "soup"}, "diet": "any", "budget": "mid"},
    {"name": "설렁탕", "tags": {"cold", "comfort", "soup"}, "diet": "any", "budget": "low"},
    {"name": "도시락(연어/치킨)", "tags": {"mild", "healthy", "on-the-go"}, "diet": "any", "budget": "mid"},
]

# 기분(무드) → 가중 태그
MOOD_TAGS: Dict[str, List[str]] = {
    "행복/설렘": ["celebrate", "sharing", "bbq"],
    "다운/우울": ["comfort", "sick-day"],
    "스트레스": ["spicy", "comfort"],
    "피곤/기력없음": ["healthy", "soup", "comfort"],
    "모험/새로움": ["adventure", "spicy"],
    "편안/휴식": ["comfort", "light"],
    "집중/일": ["light", "on-the-go", "healthy"],
    "축하/파티": ["celebrate", "sharing"],
}

# 날씨 조건 → 가중 태그
WEATHER_TAGS: Dict[str, List[str]] = {
    "rainy": ["rainy", "stew", "soup", "comfort", "noodles"],
    "snowy": ["cold", "stew", "soup", "comfort"],
    "clear": ["clear", "celebrate", "sharing", "bbq", "light"],
    "cloudy": ["comfort"],
    "misty": ["soup", "comfort"],
    "cold": ["cold", "comfort", "stew", "soup"],
    "cool": ["comfort"],
    "mild": ["mild", "light"],
    "warm": ["light"],
    "hot": ["hot", "light", "noodles"],
}


def score_item(item: Dict, active_tags: List[str], diet: str, budget: str, spicy_pref: int) -> float:
    # 식단 필터 하드 제한
    if diet == "vegan" and item["diet"] != "vegan":
        return -1
    if diet == "vegetarian" and item["diet"] not in {"vegetarian", "vegan"}:
        return -1
    # 예산 가벼운 정합성(하드 제한은 아님)
    score = 0.0
    if budget == item["budget"]:
        score += 1.0
    # 태그 매칭 점수
    score += sum(1.0 for t in active_tags if t in item["tags"])
    # 매운맛 선호: item이 spicy 태그를 가질 때 가점/감점
    if "spicy" in item["tags"]:
        score += spicy_pref * 0.7  # -1 ~ +1
    else:
        score += (0 if spicy_pref >= 0 else 0.2)  # 매운맛 회피 시 비(非)매운 메뉴 소폭 가점
    return score


# -----------------------------
# UI
# -----------------------------
st.title("🍽️ 날씨 & 기분 기반 음식 추천기")
st.caption("*오늘 날씨와 지금 기분을 반영해 메뉴를 골라 드려요. (데모)*)")

with st.sidebar:
    st.header("⚙️ 설정")
    mode = st.radio("날씨 입력 방식", ["수동 입력", "OpenWeather 사용"], index=0)
    city = st.text_input("도시/지역 (예: Seoul, KR)", value="Seoul, KR")
    api_key = st.text_input("OpenWeather API Key (선택)", type="password")

colA, colB, colC = st.columns([1.2, 1, 1])

with colA:
    mood = st.select_slider(
        "지금 기분은?",
        options=list(MOOD_TAGS.keys()),
        value="편안/휴식",
    )
    diet = st.radio("식단", ["상관없음", "채식(유제품/달걀 OK)", "비건"], index=0, horizontal=True)
    budget = st.select_slider("예산 감각", options=["low", "mid", "high"], value="mid")
    spicy_pref = st.select_slider("매운맛 선호", options=[-1, 0, 1], value=0, format_func=lambda x: { -1:"매운맛 회피", 0:"보통", 1:"매운맛 좋아요"}[x])

with colB:
    if mode == "수동 입력" or not api_key:
        weather_main = st.selectbox("날씨(요약)", ["Clear", "Clouds", "Rain", "Drizzle", "Thunderstorm", "Snow", "Mist", "Haze", "Fog"], index=0)
        temp_c = st.slider("기온 (℃)", min_value=-15, max_value=40, value=23)
        weather_info = (weather_main, float(temp_c))
        fetched = False
    else:
        try:
            weather_info = get_weather_from_openweather(city, api_key)
            fetched = True
        except Exception as e:
            st.error(f"날씨를 불러오지 못했어요: {e}")
            weather_info = ("Clear", 23.0)
            fetched = False

with colC:
    top_k = st.number_input("추천 개수", min_value=3, max_value=10, value=5, step=1)
    seed_key = st.text_input("랜덤 시드(선택)", value=datetime.now().strftime("%Y%m%d"))

# 식단 라벨 변환
if diet == "상관없음":
    diet_key = "any"
elif diet == "채식(유제품/달걀 OK)":
    diet_key = "vegetarian"
else:
    diet_key = "vegan"

# 추천 실행
if st.button("🍽️ 메뉴 추천 받기", use_container_width=True):
    random.seed(seed_key)

    weather_main, temp_c = weather_info
    flags = weather_flags(weather_main)
    tcat = categorize_temp(temp_c)

    # 활성 태그 구성
    active_tags: List[str] = []
    # 날씨 메인 플래그
    for k, v in flags.items():
        if v:
            active_tags.extend(WEATHER_TAGS.get(k, []))
    # 온도 카테고리
    active_tags.extend(WEATHER_TAGS.get(tcat, []))
    # 기분 태그
    active_tags.extend(MOOD_TAGS[mood])

    # 스코어링
    scored = []
    for item in MENU:
        s = score_item(item, active_tags, diet_key, budget, spicy_pref)
        if s >= 0:
            scored.append((s, item))

    scored.sort(key=lambda x: x[0], reverse=True)

    st.subheader("🔎 추천 결과")
    if not scored:
        st.warning("조건에 맞는 메뉴가 없어요. (식단/예산 조건을 완화해 보세요)")
    else:
        top = scored[: top_k * 2]  # 약간 넉넉히 뽑아 무작위 셔플
        random.shuffle(top)
        top = sorted(top[:top_k], key=lambda x: x[0], reverse=True)

        col1, col2 = st.columns(2)
        with col1:
            if fetched:
                st.success(f"날씨: {weather_main} · {temp_c:.1f}℃  (자동)")
            else:
                st.info(f"날씨: {weather_main} · {temp_c:.1f}℃  (수동)")
        with col2:
            st.write(f"기분: **{mood}** · 식단: **{diet}** · 예산: **{budget}** · 매운맛: **{['회피','보통','선호'][spicy_pref+1]}**")

        for rank, (score, item) in enumerate(top, start=1):
            with st.container(border=True):
                st.markdown(f"### {rank}. {item['name']}")
                reason_bits = []
                # 간단한 추천 사유 생성
                if flags.get("rainy"): reason_bits.append("비 오는 날엔 따끈한 국물/전이 잘 어울려요")
                if flags.get("snowy"): reason_bits.append("눈 오는 날엔 든든한 탕/찜이 좋아요")
                if tcat == "hot": reason_bits.append("더울 땐 가볍고 시원한 메뉴가 좋아요")
                if tcat == "cold": reason_bits.append("추울 땐 따뜻하고 칼로리 있는 메뉴가 좋아요")
                if "spicy" in item["tags"] and spicy_pref >= 0: reason_bits.append("매콤함으로 스트레스 해소!")
                if "light" in item["tags"] and tcat in {"warm", "hot"}: reason_bits.append("더운 날엔 가벼운 한 끼")
                if "celebrate" in item["tags"] and mood in {"행복/설렘", "축하/파티"}: reason_bits.append("축하 분위기에 잘 맞는 메뉴")
                if not reason_bits:
                    reason_bits.append("현재 조건과 잘 맞는 메뉴")

                st.markdown(" · ".join(reason_bits))
                # 태그/메타
                tagline = []
                if item["diet"] in {"vegan", "vegetarian"}:
                    tagline.append(item["diet"]) 
                if "spicy" in item["tags"]: tagline.append("spicy")
                if any(t in item["tags"] for t in ["soup","stew","noodles"]):
                    tagline.append("국/면")
                if any(t in item["tags"] for t in ["light","healthy"]):
                    tagline.append("가벼움/건강")
                if tagline:
                    st.caption("태그: " + ", ".join(tagline))

    with st.expander("🔧 추천 로직 보기"):
        st.write("활성 태그:")
        st.code(", ".join(sorted(set(active_tags))) or "(없음)")
        st.write("필터:")
        st.code(f"diet={diet_key}, budget={budget}, spicy_pref={spicy_pref}")

st.markdown("---")
st.caption("본 앱은 교육용 데모입니다. 취향과 상황에 따라 조정하세요.")
