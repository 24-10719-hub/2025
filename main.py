import streamlit as st
import random

# MBTI별 음식 추천 데이터
food_recommendations = {
    "INTJ": "🍣 스시 – 차분하고 전략적인 당신에게 어울려요!",
    "INTP": "🍜 라멘 – 깊고 진한 국물처럼 사고가 깊은 당신!",
    "ENTJ": "🥩 스테이크 – 강렬하고 당당한 리더의 선택!",
    "ENTP": "🌮 타코 – 자유롭고 유쾌한 모험가의 맛!",
    "INFJ": "🥗 샐러드 – 따뜻하고 배려심 깊은 당신에게 어울려요!",
    "INFP": "🍝 파스타 – 감성 가득, 부드러운 당신의 스타일!",
    "ENFJ": "🍛 커리 – 다채로운 매력, 모두를 감싸는 리더십!",
    "ENFP": "🍕 피자 – 언제나 즐겁고 활기찬 에너지!",
    "ISTJ": "🍱 돈까스 – 안정적이고 든든한 선택!",
    "ISFJ": "🍲 죽 – 따뜻하고 편안한 안식 같은 존재!",
    "ESTJ": "🐷 삼겹살 – 현실적이고 든든한 리더십!",
    "ESFJ": "🌶️ 떡볶이 – 친근하고 정이 넘치는 국민 간식!",
    "ISTP": "🍔 햄버거 – 실용적이면서도 자유로운 영혼!",
    "ISFP": "🍰 케이크 – 예술적 감성과 달콤함의 조화!",
    "ESTP": "🍗 치킨 – 에너지 넘치고 액티브한 매력!",
    "ESFP": "🍧 빙수 – 화려하고 반짝이는 파티의 중심!",
}

# 반짝이 이모지
sparkles = ["✨", "🌟", "💫", "🌈", "🎆", "🎉", "💎", "🔥", "🦄", "🌸", "🍀"]
def random_effect(n=15):
    return "".join(random.choices(sparkles, k=n))

def main():
    st.set_page_config(page_title="MBTI 음식 추천기 🍴", page_icon="🍕", layout="centered")

    # 배경 꾸미기 (CSS)
    st.markdown(
