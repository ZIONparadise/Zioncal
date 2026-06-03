import streamlit as st
import pandas as pd
import os

DATA_FILE = "hobby_records.csv"

st.set_page_config(
    page_title="로그",
    page_icon="🎯",
    layout="wide"
)

st.title("🎯 로그")
st.subheader("활동 기록 및 분석")

# 데이터 로드
if os.path.exists(DATA_FILE):
    df = pd.read_csv(DATA_FILE)
else:
    df = pd.DataFrame(columns=[
        "날짜",
        "지역",
        "활동시간(시간)",
        "금액",
        "메모"
    ])

menu = st.sidebar.selectbox(
    "메뉴 선택",
    ["기록 추가", "기록 조회", "월별 통계"]
)

# -----------------------------
# 기록 추가
# -----------------------------
if menu == "기록 추가":

    st.header("📝 기록 추가")

    hobby_date = st.date_input("날짜")

    region = st.text_input(
        "지역/장소",
        placeholder="예: 수원"
    )

    duration = st.number_input(
        "총 소요 시간 (시간)",
        min_value=1.0,
        step=0.5
    )

    amount = st.number_input(
        "사용 금액(원)",
        min_value=10000,
        step=1000
    )

    memo = st.text_area("메모")

    if st.button("저장"):

        if not region.strip():
            st.error("지역/장소를 입력해주세요.")
        else:
            new_row = {
                "날짜": hobby_date,
                "지역": region,
                "활동시간(시간)": duration,
                "금액": amount,
                "메모": memo
            }

            df = pd.concat(
                [df, pd.DataFrame([new_row])],
                ignore_index=True
            )

            df.to_csv(DATA_FILE, index=False)

            st.success("기록이 저장되었습니다.")

# -----------------------------
# 기록 조회
# -----------------------------
elif menu == "기록 조회":

    st.header("📋 기록 조회")

    if len(df) == 0:
        st.info("등록된 기록이 없습니다.")
    else:
        st.dataframe(df, use_container_width=True)

# -----------------------------
# 월별 통계
# -----------------------------
elif menu == "월별 통계":

    st.header("📊 월별 통계")

    if len(df) == 0:
        st.info("등록된 데이터가 없습니다.")

    else:
        df["날짜"] = pd.to_datetime(df["날짜"])
        df["월"] = df["날짜"].dt.strftime("%Y-%m")

        selected_month = st.selectbox(
            "월 선택",
            sorted(df["월"].unique(), reverse=True)
        )

        month_df = df[df["월"] == selected_month]

        total_count = len(month_df)
        total_amount = month_df["금액"].sum()
        total_hours = month_df["활동시간(시간)"].sum()

        col1, col2, col3 = st.columns(3)

        col1.metric("활동 횟수", f"{total_count}회")
        col2.metric("총 지출", f"{int(total_amount):,}원")
        col3.metric("총 활동시간", f"{total_hours:.1f}시간")

        st.subheader("월별 기록")

        st.dataframe(
            month_df[["날짜", "지역", "활동시간(시간)", "금액", "메모"]],
            use_container_width=True
        )

        st.subheader("지역별 방문 횟수")

        region_stats = (
            month_df["지역"]
            .value_counts()
            .reset_index()
        )

        region_stats.columns = ["지역", "횟수"]

        st.dataframe(region_stats, use_container_width=True)
