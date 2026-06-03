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

    data = data[COLUMNS].copy()

    # st.data_editor와 충돌하지 않도록 날짜는 문자열로 관리합니다.
    data["날짜"] = data["날짜"].astype(str).replace("nan", "")
    data["종류"] = data["종류"].astype(str).replace("nan", "")
    data["지역"] = data["지역"].astype(str).replace("nan", "")
    data["메모"] = data["메모"].astype(str).replace("nan", "")

    data["금액"] = pd.to_numeric(data["금액"], errors="coerce").fillna(0).astype(int)
    data["활동시간(시간)"] = pd.to_numeric(
        data["활동시간(시간)"],
        errors="coerce"
    ).fillna(0.0).astype(float)

    return data


def save_data(data):
    """데이터를 CSV 파일로 저장합니다."""
    data = data.copy()

    for col in COLUMNS:
        if col not in data.columns:
            data[col] = ""

    data = data[COLUMNS].copy()

    data["날짜"] = data["날짜"].astype(str).replace("nan", "")
    data["종류"] = data["종류"].astype(str).replace("nan", "")
    data["지역"] = data["지역"].astype(str).replace("nan", "")
    data["메모"] = data["메모"].astype(str).replace("nan", "")

    data["금액"] = pd.to_numeric(data["금액"], errors="coerce").fillna(0).astype(int)
    data["활동시간(시간)"] = pd.to_numeric(
        data["활동시간(시간)"],
        errors="coerce"
    ).fillna(0.0).astype(float)

    data.to_csv(DATA_FILE, index=False, encoding="utf-8-sig")


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
            save_data(df)

            st.success("기록이 저장되었습니다.")
            st.rerun()

# -----------------------------
# 기록 조회: 수정 / 삭제 가능
# -----------------------------
elif menu == "기록 조회":

    st.header("📋 기록 조회 / 수정 / 삭제")

    if df.empty:
        st.info("등록된 기록이 없습니다.")
    else:
        st.info("표에서 직접 수정하거나 행을 추가할 수 있습니다. 행 삭제는 표의 왼쪽 행 메뉴에서 가능합니다. 수정 후 반드시 '변경사항 저장'을 눌러주세요.")

        edited_df = st.data_editor(
            df,
            use_container_width=True,
            num_rows="dynamic",
            hide_index=True,
            column_config={
                "날짜": st.column_config.TextColumn(
                    "날짜",
                    help="YYYY-MM-DD 형식으로 입력하세요. 예: 2026-06-03"
                ),
                "종류": st.column_config.SelectboxColumn(
                    "종류",
                    options=CATEGORY_OPTIONS,
                    required=True
                ),
                "지역": st.column_config.TextColumn(
                    "지역",
                    required=True
                ),
                "활동시간(시간)": st.column_config.NumberColumn(
                    "활동시간(시간)",
                    min_value=0.0,
                    step=0.5
                ),
                "금액": st.column_config.NumberColumn(
                    "금액",
                    min_value=0,
                    step=1000
                ),
                "메모": st.column_config.TextColumn("메모")
            }
        )

        col1, col2 = st.columns(2)

        with col1:
            if st.button("변경사항 저장"):
                edited_df = edited_df.copy()

                if edited_df["지역"].astype(str).str.strip().eq("").any():
                    st.error("지역/장소가 비어 있는 기록이 있습니다.")
                elif edited_df["종류"].astype(str).str.strip().eq("").any():
                    st.error("종류가 비어 있는 기록이 있습니다.")
                else:
                    save_data(edited_df)
                    st.success("변경사항이 저장되었습니다.")
                    st.rerun()

        with col2:
            if st.button("전체 기록 삭제"):
                empty_df = pd.DataFrame(columns=COLUMNS)
                save_data(empty_df)
                st.success("전체 기록이 삭제되었습니다.")
                st.rerun()

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
            st.info("날짜 형식이 올바른 데이터가 없습니다. 날짜는 YYYY-MM-DD 형식으로 입력해주세요.")
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
