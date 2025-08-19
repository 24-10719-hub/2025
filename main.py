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
        """
        <style>
        body {
            background: linear-gradient(135deg, #ff9a9e 0%, #fad0c4 100%);
            color: white;
        }
        h1 {
            font-size: 70px !important;
            text-align: center;
            background: -webkit-linear-gradient(45deg, #ff6ec4, #7873f5);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        .food-card {
            padding: 30px;
            border-radius: 25px;
            background: linear-gradient(135deg, #f6d365 0%, #fda085 100%);
            color: white;
            font-size: 28px;
            font-weight: bold;
            text-align: center;
            box-shadow: 0px 4px 30px rgba(0,0,0,0.3);
            margin-top: 20px;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    # 타이틀
    st.markdown(
        f"<h1>🍴 MBTI 음식 추천 앱 {random_effect(10)}</h1>", 
        unsafe_allow_html=True
    )
    st.write(f"당신의 MBTI를 선택하면 {random_effect(8)} 어울리는 음식을 추천해드려요! {random_effect(8)}")

    # MBTI 선택
    mbti = st.selectbox("👉 당신의 MBTI는 무엇인가요?", list(food_recommendations.keys()))

    # 버튼 클릭 시 추천
    if st.button("🌟✨ 추천받기 GO! ✨🌟"):
        # 랜덤 이벤트 효과
        if random.choice([True, False]):
            st.balloons()
        else:
            st.snow()

        st.markdown(
            f"""
            <div class="food-card">
                {random_effect(8)} <br>
                당신({mbti})에게 어울리는 음식은... <br><br>
                <span style="font-size:40px;">{food_recommendations[mbti]}</span> <br><br>
                {random_effect(8)}
            </div>
            """,
            unsafe_allow_html=True
        )

        st.markdown(
            f"<h3 style='text-align:center; margin-top:40px;'>{random_effect(12)} 오늘도 반짝이는 하루 되세요! {random_effect(12)}</h3>",
            unsafe_allow_html=True
        )

if __name__ == "__main__":
    main()
