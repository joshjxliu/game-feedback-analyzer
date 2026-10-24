import pandas as pd
import streamlit as st
from src.pipeline import load_feedback, analyze_dataframe, build_summary

st.set_page_config(page_title="Game Feedback Analyzer", page_icon="🎮", layout="wide")
st.title("🎮 Game Feedback Analyzer")
st.caption("Multilingual player feedback -> structured product insights")

uploaded = st.sidebar.file_uploader("Upload feedback CSV", type=["csv"])
batch_size = st.sidebar.slider("LLM batch size", 1, 25, 10)

if uploaded:
    df = load_feedback(uploaded)
else:
    df = load_feedback("data/sample_feedback.csv")
    st.info("Using synthetic demo data. Upload real public feedback for actual analysis.")

if st.button("Run AI analysis", type="primary"):
    with st.spinner("Analyzing feedback..."):
        try:
            st.session_state["result"] = analyze_dataframe(df, batch_size)
        except Exception as e:
            st.error(str(e))

result = st.session_state.get("result")
if result is None:
    st.dataframe(df, use_container_width=True)
    st.stop()

summary = build_summary(result)
a,b,c,d = st.columns(4)
a.metric("Comments", summary["total_feedback"])
b.metric("High severity", summary["high_severity_count"])
c.metric("Localization issues", summary["localization_issue_count"])
d.metric("Negative", summary["sentiment"].get("negative", 0))

st.subheader("Sentiment")
st.bar_chart(result["sentiment"].value_counts())

st.subheader("Issue categories")
st.bar_chart(result["issue_category"].value_counts())

st.subheader("AI-analyzed feedback")
cols = ["id","text","language","sentiment","issue_category","severity",
        "localization_issue","summary","actionable_insight"]
st.dataframe(result[cols], use_container_width=True)
