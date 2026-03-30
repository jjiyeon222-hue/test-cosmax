import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

st.set_page_config(
    page_title="코스맥스 시제품 분석 대시보드",
    page_icon="🧴",
    layout="wide"
)

st.title("🧴 코스맥스 시제품 분석 대시보드")

# 파일 업로드
uploaded_file = st.file_uploader("Excel 파일을 업로드하세요", type=["xlsx", "xls"])

if uploaded_file is None:
    st.info("📂 위에서 cosmax_day3_dummy_data.xlsx 파일을 업로드해주세요.")
    st.stop()

# 데이터 로드
@st.cache_data
def load_data(file):
    df_product = pd.read_excel(file, sheet_name="시제품정보")
    df_test = pd.read_excel(file, sheet_name="안정성테스트결과")
    df_product["작성일"] = pd.to_datetime(df_product["작성일"])
    df_test["측정일"] = pd.to_datetime(df_test["측정일"])
    return df_product, df_test

df_product, df_test = load_data(uploaded_file)

# ── KPI 요약 ──────────────────────────────────────────────
st.subheader("📊 전체 현황")
col1, col2, col3, col4, col5 = st.columns(5)

total_products = len(df_product)
total_tests = len(df_test)
pass_count = (df_test["판정결과"] == "적합").sum()
pass_rate = pass_count / total_tests * 100
unique_teams = df_product["담당팀"].nunique()
final_review = (df_product["개발단계"] == "최종검토").sum()

col1.metric("시제품 수", f"{total_products}개")
col2.metric("안정성 테스트 수", f"{total_tests}건")
col3.metric("적합 판정률", f"{pass_rate:.1f}%")
col4.metric("담당 팀 수", f"{unique_teams}팀")
col5.metric("최종검토 단계", f"{final_review}개")

st.divider()

# ── 탭 구성 ──────────────────────────────────────────────
tab1, tab2, tab3 = st.tabs(["🧪 시제품 현황", "📈 안정성 테스트 분석", "🔍 시제품별 상세"])

# ════════════════════════════════════════════════
# TAB 1: 시제품 현황
# ════════════════════════════════════════════════
with tab1:
    col_a, col_b = st.columns(2)

    with col_a:
        # 제품유형 분포
        fig1 = px.pie(
            df_product,
            names="제품유형",
            title="제품유형 분포",
            color_discrete_sequence=px.colors.qualitative.Pastel,
            hole=0.4
        )
        fig1.update_traces(textposition="inside", textinfo="percent+label")
        st.plotly_chart(fig1, use_container_width=True)

    with col_b:
        # 개발단계 분포
        stage_order = ["초기", "중간", "최종검토"]
        stage_counts = df_product["개발단계"].value_counts().reindex(stage_order, fill_value=0).reset_index()
        stage_counts.columns = ["개발단계", "count"]
        fig2 = px.bar(
            stage_counts,
            x="개발단계",
            y="count",
            title="개발단계별 시제품 수",
            color="개발단계",
            color_discrete_sequence=["#a8d8ea", "#f8c8d4", "#b5ead7"],
            text="count"
        )
        fig2.update_traces(textposition="outside")
        fig2.update_layout(showlegend=False)
        st.plotly_chart(fig2, use_container_width=True)

    col_c, col_d = st.columns(2)

    with col_c:
        # 담당팀별 시제품 수
        team_counts = df_product["담당팀"].value_counts().reset_index()
        team_counts.columns = ["담당팀", "count"]
        fig3 = px.bar(
            team_counts,
            x="count",
            y="담당팀",
            orientation="h",
            title="담당팀별 시제품 수",
            color="count",
            color_continuous_scale="Blues",
            text="count"
        )
        fig3.update_traces(textposition="outside")
        fig3.update_layout(coloraxis_showscale=False)
        st.plotly_chart(fig3, use_container_width=True)

    with col_d:
        # 목표피부타입 분포
        skin_counts = df_product["목표피부타입"].value_counts().reset_index()
        skin_counts.columns = ["목표피부타입", "count"]
        fig4 = px.pie(
            skin_counts,
            names="목표피부타입",
            values="count",
            title="목표 피부타입 분포",
            color_discrete_sequence=px.colors.qualitative.Set3,
            hole=0.4
        )
        fig4.update_traces(textposition="inside", textinfo="percent+label")
        st.plotly_chart(fig4, use_container_width=True)

    # 시제품 상세 테이블
    st.subheader("시제품 목록")
    st.dataframe(df_product, use_container_width=True, hide_index=True)

# ════════════════════════════════════════════════
# TAB 2: 안정성 테스트 분석
# ════════════════════════════════════════════════
with tab2:
    # 필터
    with st.expander("🔧 필터 설정", expanded=True):
        f_col1, f_col2 = st.columns(2)
        with f_col1:
            selected_condition = st.multiselect(
                "테스트 조건",
                options=df_test["테스트조건"].unique(),
                default=df_test["테스트조건"].unique()
            )
        with f_col2:
            selected_products = st.multiselect(
                "시제품 코드",
                options=df_test["시제품코드"].unique(),
                default=df_test["시제품코드"].unique()
            )

    filtered = df_test[
        df_test["테스트조건"].isin(selected_condition) &
        df_test["시제품코드"].isin(selected_products)
    ]

    # 판정결과 분포
    col_a, col_b = st.columns(2)

    with col_a:
        result_counts = filtered["판정결과"].value_counts().reset_index()
        result_counts.columns = ["판정결과", "count"]
        color_map = {"적합": "#2ecc71", "경미변화": "#f39c12", "부적합": "#e74c3c"}
        fig5 = px.bar(
            result_counts,
            x="판정결과",
            y="count",
            title="판정결과 분포",
            color="판정결과",
            color_discrete_map=color_map,
            text="count"
        )
        fig5.update_traces(textposition="outside")
        fig5.update_layout(showlegend=False)
        st.plotly_chart(fig5, use_container_width=True)

    with col_b:
        # 테스트 조건별 적합률
        cond_result = filtered.groupby(["테스트조건", "판정결과"]).size().reset_index(name="count")
        fig6 = px.bar(
            cond_result,
            x="테스트조건",
            y="count",
            color="판정결과",
            title="테스트 조건별 판정결과",
            color_discrete_map=color_map,
            barmode="stack",
            text="count"
        )
        fig6.update_traces(textposition="inside")
        st.plotly_chart(fig6, use_container_width=True)

    # pH 및 점도 추이
    st.subheader("보관기간에 따른 물성 변화")
    col_c, col_d = st.columns(2)

    with col_c:
        ph_avg = filtered.groupby(["보관기간_주", "테스트조건"])["pH"].mean().reset_index()
        fig7 = px.line(
            ph_avg,
            x="보관기간_주",
            y="pH",
            color="테스트조건",
            markers=True,
            title="보관기간별 평균 pH 변화",
            labels={"보관기간_주": "보관기간 (주)"}
        )
        fig7.update_layout(xaxis=dict(tickmode="linear", dtick=1))
        st.plotly_chart(fig7, use_container_width=True)

    with col_d:
        vis_avg = filtered.groupby(["보관기간_주", "테스트조건"])["점도_cP"].mean().reset_index()
        fig8 = px.line(
            vis_avg,
            x="보관기간_주",
            y="점도_cP",
            color="테스트조건",
            markers=True,
            title="보관기간별 평균 점도(cP) 변화",
            labels={"보관기간_주": "보관기간 (주)", "점도_cP": "점도 (cP)"}
        )
        fig8.update_layout(xaxis=dict(tickmode="linear", dtick=1))
        st.plotly_chart(fig8, use_container_width=True)

    # 색상변화 & 이상 발생 현황
    st.subheader("이상 발생 현황")
    col_e, col_f = st.columns(2)

    with col_e:
        color_avg = filtered.groupby("시제품코드")["색상변화등급"].mean().reset_index()
        color_avg.columns = ["시제품코드", "평균색상변화등급"]
        fig9 = px.bar(
            color_avg.sort_values("평균색상변화등급", ascending=False),
            x="시제품코드",
            y="평균색상변화등급",
            title="시제품별 평균 색상변화 등급",
            color="평균색상변화등급",
            color_continuous_scale="Reds",
            text=color_avg.sort_values("평균색상변화등급", ascending=False)["평균색상변화등급"].round(2)
        )
        fig9.update_traces(textposition="outside")
        st.plotly_chart(fig9, use_container_width=True)

    with col_f:
        # 향변화 & 분리현상 발생률
        issue_data = pd.DataFrame({
            "이상유형": ["향 변화", "분리 현상"],
            "발생건수": [
                (filtered["향변화여부"] == "Y").sum(),
                (filtered["분리현상여부"] == "Y").sum()
            ]
        })
        fig10 = px.bar(
            issue_data,
            x="이상유형",
            y="발생건수",
            title="이상 발생 건수",
            color="이상유형",
            color_discrete_sequence=["#e17055", "#74b9ff"],
            text="발생건수"
        )
        fig10.update_traces(textposition="outside")
        fig10.update_layout(showlegend=False)
        st.plotly_chart(fig10, use_container_width=True)

    # 테스트 상세 데이터
    st.subheader("안정성 테스트 상세 데이터")
    st.dataframe(filtered, use_container_width=True, hide_index=True)

# ════════════════════════════════════════════════
# TAB 3: 시제품별 상세
# ════════════════════════════════════════════════
with tab3:
    selected_code = st.selectbox("시제품 선택", options=df_product["시제품코드"].tolist())

    product_info = df_product[df_product["시제품코드"] == selected_code].iloc[0]
    product_tests = df_test[df_test["시제품코드"] == selected_code]

    # 시제품 기본정보
    st.subheader(f"📋 {selected_code} 기본 정보")
    info_col1, info_col2 = st.columns(2)

    with info_col1:
        st.markdown(f"""
| 항목 | 내용 |
|------|------|
| **제품유형** | {product_info['제품유형']} |
| **제형** | {product_info['제형']} |
| **개발단계** | {product_info['개발단계']} |
| **목표피부타입** | {product_info['목표피부타입']} |
""")
    with info_col2:
        st.markdown(f"""
| 항목 | 내용 |
|------|------|
| **주요컨셉** | {product_info['주요컨셉']} |
| **담당팀** | {product_info['담당팀']} |
| **작성일** | {product_info['작성일'].strftime('%Y-%m-%d')} |
""")

    st.subheader(f"📈 {selected_code} 안정성 테스트 결과")

    if product_tests.empty:
        st.warning("테스트 데이터가 없습니다.")
    else:
        # pH & 점도 시계열
        fig_detail = make_subplots(
            rows=1, cols=2,
            subplot_titles=("pH 변화", "점도(cP) 변화")
        )
        for condition in product_tests["테스트조건"].unique():
            subset = product_tests[product_tests["테스트조건"] == condition].sort_values("보관기간_주")
            fig_detail.add_trace(
                go.Scatter(x=subset["보관기간_주"], y=subset["pH"], mode="lines+markers", name=f"{condition} - pH"),
                row=1, col=1
            )
            fig_detail.add_trace(
                go.Scatter(x=subset["보관기간_주"], y=subset["점도_cP"], mode="lines+markers", name=f"{condition} - 점도"),
                row=1, col=2
            )
        fig_detail.update_layout(height=400, title_text=f"{selected_code} 물성 변화 추이")
        fig_detail.update_xaxes(title_text="보관기간 (주)", tickmode="linear", dtick=1)
        st.plotly_chart(fig_detail, use_container_width=True)

        # 판정결과 요약
        result_summary = product_tests["판정결과"].value_counts().reset_index()
        result_summary.columns = ["판정결과", "건수"]
        color_map = {"적합": "#2ecc71", "경미변화": "#f39c12", "부적합": "#e74c3c"}
        fig_summary = px.pie(
            result_summary,
            names="판정결과",
            values="건수",
            title="판정결과 비율",
            color="판정결과",
            color_discrete_map=color_map,
            hole=0.4
        )
        st.plotly_chart(fig_summary, use_container_width=True)

        st.dataframe(product_tests, use_container_width=True, hide_index=True)
