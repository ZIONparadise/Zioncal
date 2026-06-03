import streamlit as st
import pandas as pd
import os

DATA_FILE = "hobby_records.csv"

COLUMNS = [
    "날짜",
    "종류",
    "지역",
    "활동시간(시간)",
    "금액",
    "메모"
]

CATEGORY_OPTIONS = ["연습", "파3", "라운드", "스크린"]

st.set_page_config(
    page_title="골프 로그",
    page_icon="⛳",
    layout="wide"
)

st.title("⛳ 골프 로그")
st.subheader("연습, 파3, 라운드, 스크린 기록 및 분석")


def load_data():
    """CSV 파일을 불러오고, 필요한 컬럼이 없으면 자동으로 추가합니다."""
    if os.path.exists(DATA_FILE):
        data = pd.read_csv(DATA_FILE)
    else:
        data = pd.DataFrame(columns=COLUMNS)

    for col in COLUMNS:
        if col not in data.columns:
            data[col] = ""

    data = data[COLUMNS]

    data["금액"] = pd.to_numeric(data["금액"], errors="coerce").fillna(0)
    data["활동시간(시간)"] = pd.to_numeric(
        data["활동시간(시간)"],
        errors="coerce"
    ).fillna(0)

    return data


df = load_data()

menu = st.sidebar.selectbox(
    "메뉴 선택",
    ["기록 추가", "기록 조회", "월별 통계"]
)

# -----------------------------
# 기록 추가
# -----------------------------
if menu == "기록 추가":

    st.header("📝 기록 추가")

    record_date = st.date_input("날짜")

    category = st.selectbox(
        "종류",
        CATEGORY_OPTIONS
    )

    region = st.text_input(
        "지역/장소",
        placeholder="예: 수원, 이천 Silk Valley, 동네 스크린골프장"
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
            new_row = pd.DataFrame([{
                "날짜": record_date.strftime("%Y-%m-%d"),
                "종류": category,
                "지역": region.strip(),
                "활동시간(시간)": float(duration),
                "금액": int(amount),
                "메모": memo.strip()
            }])

            df = pd.concat([df, new_row], ignore_index=True)
            df = df[COLUMNS]
            df.to_csv(DATA_FILE, index=False, encoding="utf-8-sig")

            st.success("기록이 저장되었습니다.")

# -----------------------------
# 기록 조회
# -----------------------------
elif menu == "기록 조회":

    st.header("📋 기록 조회")

    if df.empty:
        st.info("등록된 기록이 없습니다.")
    else:
        view_df = df.copy()
        view_df["금액"] = view_df["금액"].astype(int)

        st.dataframe(
            view_df[["날짜", "종류", "지역", "활동시간(시간)", "금액", "메모"]],
            use_container_width=True
        )

# -----------------------------
# 월별 통계
# -----------------------------
elif menu == "월별 통계":

    st.header("📊 월별 통계")

    if df.empty:
        st.info("등록된 데이터가 없습니다.")
    else:
        stats_df = df.copy()
        stats_df["날짜"] = pd.to_datetime(stats_df["날짜"], errors="coerce")
        stats_df = stats_df.dropna(subset=["날짜"])

        if stats_df.empty:
            st.info("날짜 형식이 올바른 데이터가 없습니다.")
        else:
            stats_df["월"] = stats_df["날짜"].dt.strftime("%Y-%m")

            selected_month = st.selectbox(
                "월 선택",
                sorted(stats_df["월"].unique(), reverse=True)
            )

            month_df = stats_df[stats_df["월"] == selected_month]

            total_count = len(month_df)
            total_amount = month_df["금액"].sum()
            total_hours = month_df["활동시간(시간)"].sum()

            col1, col2, col3 = st.columns(3)

            col1.metric("활동 횟수", f"{total_count}회")
            col2.metric("총 지출", f"{int(total_amount):,}원")
            col3.metric("총 활동시간", f"{total_hours:.1f}시간")

            st.subheader("월별 기록")

            display_df = month_df[
                ["날짜", "종류", "지역", "활동시간(시간)", "금액", "메모"]
            ].copy()
            display_df["날짜"] = display_df["날짜"].dt.strftime("%Y-%m-%d")
            display_df["금액"] = display_df["금액"].astype(int)

            st.dataframe(display_df, use_container_width=True)

            st.subheader("종류별 통계")

            category_stats = (
                month_df
                .groupby("종류")
                .agg(
                    횟수=("종류", "count"),
                    총금액=("금액", "sum"),
                    총활동시간=("활동시간(시간)", "sum")
                )
                .reset_index()
            )

            category_stats["총금액"] = category_stats["총금액"].astype(int)

            st.dataframe(category_stats, use_container_width=True)

            st.subheader("지역별 방문 횟수")

            region_stats = (
                month_df["지역"]
                .value_counts()
                .reset_index()
            )

            region_stats.columns = ["지역", "횟수"]

            st.dataframe(region_stats, use_container_width=True)
