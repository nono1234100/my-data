import streamlit as st
import pandas as pd

DATA_URL = "https://raw.githubusercontent.com/greatsong/modudata/main/data/seoul.csv"

st.set_page_config(
    page_title="서울 연평균 기온 변화",
    page_icon="🌡️",
    layout="wide",
)

st.title("🌡️ 서울의 100년 연평균 기온 변화")
st.write("1900년대 초부터 현재까지 서울의 연평균 기온이 어떻게 변해 왔는지 살펴봅니다.")

@st.cache_data
def load_data():
    df = pd.read_csv(DATA_URL, encoding="utf-8-sig")

    df["날짜"] = pd.to_datetime(df["날짜"], errors="coerce")
    df["평균기온"] = pd.to_numeric(df["평균기온"], errors="coerce")

    df = df.dropna(subset=["날짜", "평균기온"]).copy()
    df["연도"] = df["날짜"].dt.year

    return df


try:
    df = load_data()

    # 연도별 평균기온 계산
    annual = (
        df.groupby("연도", as_index=False)["평균기온"]
        .mean()
        .rename(columns={"평균기온": "연평균기온"})
    )

    # 100년 단위로 표시할 수 있도록 최근 100년을 기본으로 선택
    max_year = int(annual["연도"].max())
    min_year = max_year - 99

    annual_100 = annual[
        (annual["연도"] >= min_year) &
        (annual["연도"] <= max_year)
    ].copy()

    st.subheader(f"{min_year}년~{max_year}년 연평균 기온")

    st.line_chart(
        annual_100.set_index("연도"),
        y="연평균기온",
        x_label="연도",
        y_label="연평균 기온 (℃)",
    )

    # 요약 정보
    col1, col2, col3 = st.columns(3)

    first_temp = annual_100.iloc[0]["연평균기온"]
    last_temp = annual_100.iloc[-1]["연평균기온"]
    change = last_temp - first_temp

    with col1:
        st.metric(
            "시작 연도 평균기온",
            f"{first_temp:.1f} ℃",
            f"{int(annual_100.iloc[0]['연도'])}년",
        )

    with col2:
        st.metric(
            "최근 연도 평균기온",
            f"{last_temp:.1f} ℃",
            f"{int(annual_100.iloc[-1]['연도'])}년",
        )

    with col3:
        st.metric(
            "100년간 변화",
            f"{change:+.1f} ℃",
        )

    st.caption(
        "※ 연평균 기온은 해당 연도의 일평균 기온을 평균하여 계산했습니다. "
        "관측 자료가 없는 날짜가 있는 경우 해당 연도의 실제 관측값만으로 계산됩니다."
    )

except Exception as e:
    st.error("데이터를 불러오는 중 문제가 발생했습니다.")
    st.exception(e)
