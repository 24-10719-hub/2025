# app.py
# -*- coding: utf-8 -*-
import re
import unicodedata
from typing import List, Dict, Tuple

import numpy as np
import pandas as pd
import streamlit as st

st.set_page_config(page_title="간호진단 추천 데모", page_icon="🩺", layout="wide")

# ---------------------------
# 유틸 함수
# ---------------------------
def normalize_text(s: str) -> str:
    """한글 정규화 + 소문자화 + 불필요 공백 제거"""
    if not s:
        return ""
    s = unicodedata.normalize("NFKC", s)
    s = s.lower()
    # 특수문자 -> 공백
    s = re.sub(r"[^0-9a-zA-Z가-힣\s]", " ", s)
    # 다중 공백 정리
    s = re.sub(r"\s+", " ", s).strip()
    return s

def keyword_hit_count(text: str, keywords: List[str]) -> Tuple[int, List[str]]:
    """텍스트에서 키워드 일치 개수와 매칭된 키워드 목록 반환"""
    hits = []
    for kw in keywords:
        # 완전 단어 매칭 우선, 없으면 부분 매칭
        kw_norm = normalize_text(kw)
        # 완전 단어 경계 탐색
        if re.search(rf"\b{re.escape(kw_norm)}\b", text):
            hits.append(kw)
        else:
            # 한글/영어 혼용 대비 부분 매칭도 허용
            if kw_norm in text:
                hits.append(kw)
    return len(set(hits)), sorted(set(hits))

def score_diagnosis(input_text: str, item: Dict) -> Dict:
    """
    단순 가중치 점수:
      - 정의 특성(defining characteristics) 키워드 2점
      - 관련 요인(related factors) 키워드 1점
    """
    dc_hits_n, dc_hits = keyword_hit_count(input_text, item["defining_keywords"])
    rf_hits_n, rf_hits = keyword_hit_count(input_text, item["related_keywords"])
    score = dc_hits_n * 2 + rf_hits_n * 1
    return {
        "diagnosis": item["diagnosis"],
        "diagnosis_en": item["diagnosis_en"],
        "definition": item["definition"],
        "score": score,
        "dc_hits": dc_hits,
        "rf_hits": rf_hits,
    }

# ---------------------------
# 예시 데이터셋 (축약/교육용)
# 실제 과제에서는 CSV/DB로 확장 가능
# ---------------------------
DIAGNOSES = [
    {
        "diagnosis": "급성 통증",
        "diagnosis_en": "Acute Pain",
        "definition": "실제적 또는 잠재적 조직손상과 관련된 갑작스럽고 단기간의 통증 경험.",
        "defining_keywords": [
            "통증", "아픔", "aching", "sharp pain", "찌르는 듯", "얼굴 찡그림",
            "보호적 자세", "guarding", "진땀", "발한", "고통 호소", "통증 척도 상승"
        ],
        "related_keywords": ["수술 후", "외상", "염증", "절개", "근육 긴장"]
    },
    {
        "diagnosis": "가스교환 장애",
        "diagnosis_en": "Impaired Gas Exchange",
        "definition": "폐포-모세혈관 수준에서 산소/이산화탄소 교환에 장애가 있는 상태.",
        "defining_keywords": [
            "산소포화도 저하", "spo2 저하", "저산소증", "저산소", "cyanosis", "청색증",
            "호흡곤란", "dyspnea", "빈호흡", "tachypnea", "co2 상승", "혼돈", "의식저하"
        ],
        "related_keywords": ["폐렴", "copd", "천식", "흉부감염", "흡인", "폐부종"]
    },
    {
        "diagnosis": "비효율적 기도청결",
        "diagnosis_en": "Ineffective Airway Clearance",
        "definition": "기도에서 분비물이나 폐쇄물을 제거·유지하는 능력이 저하된 상태.",
        "defining_keywords": [
            "객담", "가래", "기침 비효율", "wheezing", "천명", "거친 호흡음",
            "호흡곤란", "분비물 증가", "무기폐"
        ],
        "related_keywords": ["흡연", "상기도 감염", "천식", "기관지염", "운동 무력감", "진정제"]
    },
    {
        "diagnosis": "낙상 위험성",
        "diagnosis_en": "Risk for Falls",
        "definition": "낙상으로 손상을 입을 위험이 증가된 상태.",
        "defining_keywords": [
            "불안정 보행", "어지러움", "현기증", "기립성 저혈압", "근력 저하",
            "보행 보조기 사용", "균형 장애"
        ],
        "related_keywords": ["야뇨", "수면제", "진정제", "환경 위험", "시야 장애", "고령"]
    },
    {
        "diagnosis": "체액 부족",
        "diagnosis_en": "Deficient Fluid Volume",
        "definition": "체액 손실이 섭취보다 커서 혈액량이 감소된 상태.",
        "defining_keywords": [
            "점막 건조", "피부 탄력 저하", "저혈압", "빈맥", "집중력 저하",
            "소변량 감소", "탈수", "갈증"
        ],
        "related_keywords": ["구토", "설사", "발열", "이뇨제", "출혈", "과도한 발한"]
    },
    {
        "diagnosis": "불안",
        "diagnosis_en": "Anxiety",
        "definition": "모호한 위협에 대한 불쾌한 정서적 반응으로 긴장과 초조가 동반.",
        "defining_keywords": [
            "불안", "초조", "긴장", "안절부절", "불면", "심계항진", "호흡 가빠짐",
            "집중곤란", "걱정", "두려움"
        ],
        "related_keywords": ["시술 전", "수술 전", "진단 대기", "통증", "정보 부족", "과거 트라우마"]
    },
    {
        "diagnosis": "피부 통합성 장애",
        "diagnosis_en": "Impaired Skin Integrity",
        "definition": "피부의 표면이 손상되거나 파괴된 상태.",
        "defining_keywords": [
            "욕창", "발적", "열감", "개방성 상처", "삼출물", "피부 파열", "수포"
        ],
        "related_keywords": ["부동", "영양불량", "압박", "습윤", "고혈당", "고령"]
    },
    {
        "diagnosis": "감염 위험성",
        "diagnosis_en": "Risk for Infection",
        "definition": "감염에 취약한 상태로 병원체 침입 가능성이 증가.",
        "defining_keywords": [
            "발열", "오한", "백혈구 증가", "상처 발적", "농성 분비물", "악취"
        ],
        "related_keywords": ["면역저하", "도뇨관", "정맥 카테터", "수술 상처", "영양결핍", "고혈당"]
    },
    {
        "diagnosis": "영양 불균형: 요구량보다 낮음",
        "diagnosis_en": "Imbalanced Nutrition: Less than Body Requirements",
        "definition": "대사 요구량을 충족하기에 불충분한 영양 섭취 상태.",
        "defining_keywords": [
            "체중감소", "식욕부진", "쇠약", "저알부민", "근육 소모", "피로"
        ],
        "related_keywords": ["오심", "구토", "연하곤란", "우울", "경제적 어려움", "미각 변화"]
    },
]

# ---------------------------
# 사이드바: 안내 & 예시
# ---------------------------
st.sidebar.header("📝 사용 가이드")
st.sidebar.markdown(
    """
**입력 예시(붙여넣기):**
- 환자가 **호흡곤란**과 **spo2 저하**, **청색증** 보이며 **폐렴** 진단 받음.
- 수술 후 **심한 통증** 호소, **얼굴 찡그림**과 **보호적 자세** 관찰.
- **어지러움** 및 **불안정 보행**, **수면제** 복용력 있음.
"""
)

preset_examples = {
    "호흡곤란 + SpO2 저하 + 폐렴": "환자가 호흡곤란을 호소하고, 산소포화도(SPO2)가 88%로 저하됨. 청색증 약간 관찰되며 폐렴 진단 하에 항생제 투여 중.",
    "수술 후 통증": "복부 수술 후 날카로운 통증을 8/10으로 호소. 얼굴 찡그림, 보호적 자세 보이고 진땀이 남.",
    "어지러움 + 수면제 복용": "밤에 자주 소변 보러 일어나며 어지러움을 느낌. 보행 시 불안정하고 최근 수면제 복용 시작."
}
choice = st.sidebar.selectbox("예시 불러오기", ["직접 입력"] + list(preset_examples.keys()))
if choice != "직접 입력":
    example_text = preset_examples[choice]
else:
    example_text = ""

st.sidebar.markdown("---")
st.sidebar.caption("⚠️ 본 도구는 교육용 데모입니다. 실제 임상 판단을 대체하지 않습니다.")

# ---------------------------
# 메인 UI
# ---------------------------
st.title("🩺 간호진단 추천기 (데모)")
st.write("증상/소견/배경을 자유롭게 입력하면 가능한 간호진단 후보를 점수로 정렬해 보여줍니다.")

user_input = st.text_area(
    "환자 상태를 입력하세요 (증상, 징후, 검사결과, 배경 포함)",
    value=example_text,
    height=160,
    placeholder="예) 수술 후 심한 통증 호소, 얼굴 찡그림, 보호적 자세, 발한 관찰됨..."
)

col1, col2, col3 = st.columns([1,1,1])
with col1:
    top_k = st.number_input("표시 개수 (Top-K)", min_value=1, max_value=10, value=5, step=1)
with col2:
    show_details = st.checkbox("매칭된 키워드 상세 보기", value=True)
with col3:
    weight_dc2 = st.checkbox("정의특성 2배 가중치(기본)", value=True)

if not weight_dc2:
    st.info("가중치 변경: 정의특성=1점, 관련요인=1점으로 계산합니다.")

# ---------------------------
# 추천 로직
# ---------------------------
if st.button("진단 추천 실행", use_container_width=True):
    norm_text = normalize_text(user_input)

    results = []
    for item in DIAGNOSES:
        res = score_diagnosis(norm_text, item)
        if not weight_dc2:
            # 가중치 1:1로 재계산
            dc_hits_n = len(res["dc_hits"])
            rf_hits_n = len(res["rf_hits"])
            res["score"] = dc_hits_n + rf_hits_n
        results.append(res)

    df = pd.DataFrame(results).sort_values(["score", "diagnosis"], ascending=[False, True])
    df_top = df.head(int(top_k)).reset_index(drop=True)

    st.subheader("🔎 추천 결과")
    if df_top["score"].max() == 0:
        st.warning("매칭된 키워드가 없습니다. 더 구체적인 증상·소견을 입력해 보세요.")
    else:
        # 간단한 색상 하이라이트
        def _style(val):
            if val >= df_top["score"].max():
                return "font-weight:bold"
            return ""
        st.dataframe(
            df_top[["diagnosis", "diagnosis_en", "definition", "score"]],
            use_container_width=True,
            hide_index=True
        )

        if show_details:
            st.markdown("#### 매칭 상세")
            for i, row in df_top.iterrows():
                with st.expander(f"{row['diagnosis']} ({row['diagnosis_en']}) · 점수 {row['score']}"):
                    col_a, col_b = st.columns(2)
                    with col_a:
                        st.markdown("**정의특성 매칭 키워드**")
                        if row["dc_hits"]:
                            st.write(", ".join(row["dc_hits"]))
                        else:
                            st.write("—")
                    with col_b:
                        st.markdown("**관련요인 매칭 키워드**")
                        if row["rf_hits"]:
                            st.write(", ".join(row["rf_hits"]))
                        else:
                            st.write("—")

    st.markdown("---")
    st.caption("참고: 키워드 기반의 단순 스코어링으로, 실제 NANDA-I 전체 정의/특성/관련요인 범위를 포괄하지 않습니다.")

# ---------------------------
# 확장 팁 섹션
# ---------------------------
with st.expander("📦 데이터 확장/개선 팁"):
    st.markdown(
        """
- **데이터 소스 분리:** `diagnoses.csv`로 분리해 유지보수 용이(열: diagnosis, diagnosis_en, definition, defining_keywords, related_keywords).
- **동의어 사전 추가:** '호흡곤란=숨참, 가쁘다, 숨 가쁨' 등 동의어 매핑 dict로 전처리.
- **언어 처리 개선:** 형태소 분석기(예: KoNLPy)나 간단한 lemmatization으로 잡음 감소.
- **가중치 조정:** 임상 중요도에 따라 정의특성/관련요인/위험요인 가중치 튜닝.
- **UI 개선:** 매칭 근거 하이라이트, PDF 리포트 내보내기, 진단별 간호중재 템플릿 연결 등.
        """
    )

