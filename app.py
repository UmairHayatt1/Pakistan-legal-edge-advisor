import streamlit as st
import os
from dotenv import load_dotenv
from pipeline.rag_engine import LegalRAGEngine

load_dotenv()

st.set_page_config(
    page_title="Pakistan Multi-Sector Legal Advisor",
    page_icon="⚖️",
    layout="wide"
)

# Available Sectors matching folder names
SECTORS = [
    "ALL",
    "ARMED FORCES ACT",
    "EDUCATION ACT",
    "ELECTRONICS & MEDIA ACT",
    "EXCISE AND TAX ACT",
    "FINANCE ACT",
    "HEALTHCARE ACT",
    "MINORTIES ACT",
    "PAKISTAN ACT",
    "POLICE RULES",
    "VEHICLES ACT"
]

@st.cache_resource
def load_engine():
    return LegalRAGEngine()

try:
    engine = load_engine()
    db_loaded = True
except Exception as e:
    db_loaded = False
    st.error(f"⚠️ Vector database loading issue: {e}")

# Sidebar Options
st.sidebar.title("⚖️Legal Advisor Settings")

st.sidebar.markdown("### 📂 Select Legal Domain")
selected_sector = st.sidebar.selectbox(
    "Which sector?",
    SECTORS,
    help="Choose a sector to restrict answers to that domain. 'ALL' searches across all sectors."
)

st.sidebar.markdown("### 🎓 Select Mode")
user_mode = st.sidebar.radio(
    "How should I answer?",
    ["Student / Scholar", "General Citizen"],
    help="Student: Strict RAG - answers ONLY from provided materials with exact citations\nGeneral: Can use general knowledge + provided sources"
)

st.sidebar.markdown("---")

# Mode explanation
if "Student" in user_mode:
    st.sidebar.info(
        f"**🎓 STUDENT MODE (Strict RAG)**\n\n"
        f"✅ Answers ONLY from provided legal materials\n"
        f"✅ All claims cite exact Act/Section/Page\n"
        f"❌ No external knowledge\n"
        f"❌ Will say 'not available' if not in sources\n\n"
        f"**Active Sector:** `{selected_sector}`"
    )
else:
    st.sidebar.info(
        f"**💬 GENERAL MODE (Research)**\n\n"
        f"✅ Uses provided sources + general knowledge\n"
        f"✅ Prioritizes official materials\n"
        f"✅ Marks general knowledge vs. official\n"
        f"✅ More conversational & helpful\n\n"
        f"**Active Sector:** `{selected_sector}`"
    )

# Header
st.title("Pakistan's Multi Sector Legal Advisor&nbsp;&nbsp;&nbsp;&nbsp;🇵🇰") 
st.caption("AI Powered Legal Guidance Covering Pakistan's Constitution, Police, Taxation, Education, Healthcare, Transport, and Armed Forces .")

# Mode indicator
col1, col2, col3 = st.columns(3)
with col1:
    mode_badge = "🎓 STUDENT" if "Student" in user_mode else "💬 GENERAL"
    st.metric("Mode", mode_badge)
with col2:
    st.metric("Sector", selected_sector)
with col3:
    mode_desc = "Strict RAG Only" if "Student" in user_mode else "RAG + LLM"
    st.metric("Behavior", mode_desc)

st.markdown("---")

# Main Query Interface
query_input = st.text_input(
    "Ask a legal question:",
    placeholder="e.g., What are the eligibility requirements for teachers in Punjab?"
)

if st.button("🔍 Search & Analyze", use_container_width=True) and query_input:
    if not db_loaded:
        st.error("❌ Database unavailable. Please ensure ingestion is complete.")
    else:
        with st.spinner("⏳ Searching through legal database and retrieving sources..."):
            try:
                mode_key = "Student" if "Student" in user_mode else "General"
                res = engine.query(
                    question=query_input,
                    sector=selected_sector,
                    mode=mode_key
                )

                st.markdown("### 📋 Legal Analysis")
                st.write(res["answer"])

                st.markdown("---")
                
                # Show sources with styling
                with st.expander("📚 View Retrieved Legal Sources", expanded=True):
                    if res.get("context") and len(res["context"]) > 0:
                        st.info(f"Found {len(res['context'])} relevant legal source(s)")
                        for idx, doc in enumerate(res["context"], 1):
                            meta = doc.metadata
                            source = meta.get('source', 'Unknown')
                            doc_sector = meta.get('sector', 'N/A')
                            page = meta.get('page', 'N/A')
                            
                            st.markdown(f"**📄 Source {idx}:** {source}")
                            st.markdown(f"*Sector: {doc_sector} | Page: {page}*")
                            st.caption(doc.page_content[:500] + "..." if len(doc.page_content) > 500 else doc.page_content)
                            st.divider()
                    else:
                        st.warning("⚠️ No sources retrieved for this query. This might mean:")
                        st.markdown("""
                        - The question is outside your selected sector
                        - The information isn't in the provided materials
                        - Try switching sectors or rewording your question
                        """)
            except Exception as e:
                st.error(f"❌ Error during query: {str(e)}")
                st.info("Tip: Make sure your GROQ_API_KEY is set in .env file")