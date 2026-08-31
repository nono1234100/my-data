import pandas as pd
import streamlit as st

DATA_URL = "https://raw.githubusercontent.com/greatsong/modudata/main/data/seoul.csv"

st.set_page_config(
    page_title="서울 연평균 기온 변화",
    page_icon="🌡️",
    layout="wide",
)

st.title("서울의 100년 연평균 기온 변화")
st.write("서울 기상 관측 데이터를 바탕으로 연평균 기온의 장기적인 변화를 보여줍니다.")


@st.cache_data
def load_data():
    df = pd.read_csv(DATA_URL, encoding="utf-8-sig")

    df["날짜"] = pd.to_datetime(df["날짜"], errors="coerce")
    df["평균기온"] = pd.to_numeric(df["평균기온"], errors="coerce")

    # 날짜와 평균기온이 모두 있는 데이터만 사용
    df = df.dropna(subset=["날짜", "평균기온"]).copy()
    df["연도"] = df["날짜"].dt.year

    return df


try:
    df = load_data()

    # 연도별 평균기온 계산
    yearly = (
        df.groupby("연도")["평균기온"]
        .mean()
        .reset_index()
        .rename(columns={"평균기온": "연평균기온"})
        .sort_values("연도")
    )

    # 실제 데이터가 존재하는 연도만 사용
    yearly = yearly.dropna(subset=["연평균기온"])

    # 가장 최근 100개 연도
    if len(yearly) > 100:
        yearly = yearly.tail(100).copy()

    # 그래프에서 데이터가 없는 구간을 선으로 연결하지 않도록
    # 실제 존재하는 연도만 인덱스로 사용
    yearly["연도"] = yearly["연도"].astype(str)
    yearly = yearly.set_index("연도")

    st.subheader("연평균 기온 추이")

    st.line_chart(
        yearly["연평균기온"],
        y_label="기온 (℃)",
        x_label="연도",
        use_container_width=True,
    )

    col1, col2, col3 = st.columns(3)

    col1.metric(
        "표시 기간",
        f"{yearly.index[0]} ~ {yearly.index[-1]}"
    )

    col2.metric(
        "가장 낮은 연평균",
        f"{yearly['연평균기온'].min():.1f} ℃"
    )

    col3.metric(
        "가장 높은 연평균",
        f"{yearly['연평균기온'].max():.1f} ℃"
    )

    st.caption(
        "출처: 기상청 서울 관측자료(seoul.csv). "
        "관측값이 없는 연도는 그래프에서 제외했습니다."
    )

except Exception as e:
    st.error("데이터를 불러오는 중 문제가 발생했습니다.")
    st.exception(e)
