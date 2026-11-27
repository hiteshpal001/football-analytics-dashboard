"""Football Player Performance Analytics Dashboard — entry point.

Run:  streamlit run app.py
"""
import streamlit as st

from utils.data_loader import load_data
from utils.filters import sidebar_filters
from utils.theme import inject_css

st.set_page_config(
    page_title="Football Analytics Dashboard",
    page_icon="⚽",
    layout="wide",
)
inject_css()

df = load_data()
st.session_state["filtered_df"] = sidebar_filters(df)
st.session_state["full_df"] = df

pages = [
    st.Page("views/overview.py", title="Overview", icon="📊", default=True),
    st.Page("views/players.py", title="Player Analysis", icon="👤"),
    st.Page("views/teams.py", title="Team Analysis", icon="🏆"),
    st.Page("views/positions.py", title="Position Analysis", icon="🎽"),
    st.Page("views/awards.py", title="Awards", icon="⭐"),
]
st.navigation(pages).run()
