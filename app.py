import streamlit as st
import sys

# 1. PAGE CONFIG MUST BE FIRST
st.set_page_config(page_title="GitHub Recommender", layout="wide", page_icon="🚀")

# --- CUSTOM CSS FOR STYLING ---
st.markdown("""
<style>
    /* GitHub Dark Mode Background */
    .stApp {
        background-color: #0d1117;
    }
    
    /* Main Title - GitHub Text Color */
    .main-title {
        font-family: -apple-system,BlinkMacSystemFont,"Segoe UI",Helvetica,Arial,sans-serif,"Apple Color Emoji","Segoe UI Emoji";
        font-size: 3.5rem;
        font-weight: 600;
        text-align: center;
        color: #c9d1d9;
        margin-bottom: 0;
    }
    /* Subtitle - GitHub Secondary Text Color */
    .subtitle {
        font-family: -apple-system,BlinkMacSystemFont,"Segoe UI",Helvetica,Arial,sans-serif,"Apple Color Emoji","Segoe UI Emoji";
        font-size: 1.2rem;
        text-align: center;
        color: #8b949e;
        margin-bottom: 3rem;
    }
    
    /* Result Card - GitHub Box Style */
    .result-card {
        background-color: #161b22;
        padding: 20px;
        border-radius: 6px;
        margin-bottom: 15px;
        border: 1px solid #30363d;
    }
    
    /* Repository Title in Card */
    .result-card h3 {
        margin: 0;
        color: #58a6ff; /* GitHub Link Blue */
        font-weight: 600;
        font-size: 1.3rem;
    }
    
    /* Stats Text in Card */
    .result-card .stats {
        font-size: 0.9em;
        color: #8b949e;
        margin-top: 5px;
    }
    
    /* Description/Libraries Text in Card */
    .result-card .desc {
        margin-top: 10px;
        color: #c9d1d9;
        line-height: 1.5;
        font-family: monospace; /* Monospace font for libraries looks better */
        background-color: rgba(110, 118, 129, 0.1); /* Subtle code block bg */
        padding: 5px;
        border-radius: 4px;
    }
    
    /* Search Bar Container Clean Up */
    div[data-baseweb="input"] {
        background-color: transparent !important;
        border: none !important;
        box-shadow: none !important;
    }

    /* Search Input Styling - GitHub Input Style */
    .stTextInput input {
        text-align: center;
        background-color: #0d1117 !important;
        color: #c9d1d9 !important;
        border: 1px solid #30363d !important;
        padding: 1rem !important;
        font-size: 1.1rem !important;
        border-radius: 6px !important;
    }

    /* Focus State */
    .stTextInput input:focus {
        border-color: #58a6ff !important;
        box-shadow: 0 0 0 3px rgba(88, 166, 255, 0.3) !important;
    }

    .stTextInput input::placeholder {
        color: #8b949e;
    }
</style>
""", unsafe_allow_html=True)

# --- SAFE IMPORTS ---
try:
    from neo4j import GraphDatabase
    from llm_helper import get_cypher_query
except ImportError as e:
    st.error(f"❌ Library Error: {e}")
    st.stop()

# --- DATABASE CONNECTION ---
# ⚠️ Ensure this matches your Neo4j Desktop Port
NEO4J_URI = "bolt://127.0.0.1:7687"
NEO4J_USER = "neo4j"
NEO4J_PASSWORD = "database"

def run_neo4j_query(cypher_query):
    try:
        driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))
        with driver.session() as session:
            result = session.run(cypher_query)
            results = []
            for record in result:
                row = record.data()
                clean_row = {k.split('.')[-1]: v for k, v in row.items()}
                results.append(clean_row)
        driver.close()
        return results
    except Exception as e:
        return str(e)

# --- SIDEBAR ---
with st.sidebar:
    st.header("⚙️ Settings")
    try:
        driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))
        driver.verify_connectivity()
        st.success("🟢 Neo4j Online")
        driver.close()
    except:
        st.error("🔴 Neo4j Offline")

    st.success("🟢 AI Agent Online")
    st.divider()
    show_cypher = st.toggle("Show Thinking (Debug)", value=True)

# --- MAIN CONTENT ---

# 1. Title Section
st.markdown('<h1 class="main-title">GitHub Recommender</h1>', unsafe_allow_html=True)
st.markdown('<p class="subtitle">Find the perfect open-source project using Knowledge Graphs & AI</p>', unsafe_allow_html=True)

# 2. Search Bar (Centered)
col_spacer_l, col_search, col_spacer_r = st.columns([1, 2, 1])

with col_search:
    query = st.text_input(
        "Search",
        placeholder="What are you looking for?",
        label_visibility="collapsed"
    )

# 3. Logic & Results
if query:
    st.divider()

    with st.spinner("Hmmmmmmmmmmmmm interesting..."):
        cypher_query = get_cypher_query(query)

    if cypher_query:
        if show_cypher:
            with st.expander("View AI Reasoning"):
                st.code(cypher_query, language="cypher")

        with st.spinner("⚡ Checking Database..."):
            projects = run_neo4j_query(cypher_query)

        if isinstance(projects, str):
            st.error("🚨 Database Error")
            st.warning(f"Details: {projects}")
        elif projects:
            st.success(f"Found {len(projects)} projects:")

            # Custom Card Layout
            for proj in projects:
                name = proj.get('name', 'Unknown')
                stars = proj.get('stars', 0)
                # Switched from description to libraries
                libraries = proj.get('libraries', 'No libraries listed')
                owner = proj.get('owner', 'N/A')

                with st.container():
                    st.markdown(f"""
                    <div class="result-card">
                        <h3>{name}</h3>
                        <p class="stats">⭐ {stars} stars | 👤 {owner}</p>
                        <p class="desc">Libraries: {libraries}</p>
                    </div>
                    """, unsafe_allow_html=True)
        else:
            st.warning("No results found. Try a broader query.")
    else:
        st.error("❌ AI Error: The assistant returned nothing.")