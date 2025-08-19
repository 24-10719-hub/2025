import streamlit as st

# MBTI별 음식 추천 데이터
food_recommendations = {
    "INTJ": "스시 🍣",
    "INTP": "라멘 🍜",
    "ENTJ": "스테이크 🥩",
    "ENTP": "타코 🌮",
    "INFJ": "샐러드 🥗",
    "INFP": "파스타 🍝",
    "ENFJ": "커리 🍛",
    "ENFP": "피자 🍕",
    "ISTJ": "돈까스 🍱",
    "ISFJ": "죽 🍲",
    "ESTJ": "삼겹살 🐷",
    "ESFJ": "떡볶이 🌶️",
    "ISTP": "햄버거 🍔",
    "ISFP": "케이크 🍰",
    "ESTP": "치킨 🍗",
    "ESFP": "빙수 🍧",
}

def main():
    st.title("🍴 MBTI 음식 추천 앱")
    st.write("당신의 MBTI를 선택하면 어울리는 음식을 추천해드려요!")

    # MBTI 선택 박스
    mbti = st.selectbox("당신의 MBTI는 무엇인가요?", list(food_recommendations.keys()))

    # 버튼 클릭 시 추천 음식 출력
    if st.button("추천받기"):
        st.success(f"당신에게 어울리는 음식은 👉 {food_recommendations[mbti]} 입니다!")

if __name__ == "__main__":
    main()
