import streamlit as st
import json
from model import CompanyAnalyzer

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="LinkedIn Company Analyzer",
    page_icon="🔍",
    layout="wide"
)

# ---------------- HEADER ----------------
st.title("🔍 LinkedIn Company Analyzer")
st.caption("⚡ Powered by Groq + Llama 3.1 70B")

st.markdown("""
Analyze LinkedIn **company pages and/or job postings** to check eligibility based on:
- Industry segments
- Company size (50–500 or funded startups)
- Locations (US & India tech hubs)
- Decision makers
- AI / ML intent signals
""")

st.divider()

# ---------------- LOAD ANALYZER ----------------
@st.cache_resource
def load_analyzer():
    try:
        return CompanyAnalyzer()
    except Exception as e:
        st.error(f"❌ Analyzer init failed: {e}")
        st.info("Ensure GROQ_API_KEY is configured correctly.")
        st.stop()

analyzer = load_analyzer()

# ---------------- INPUTS ----------------
st.subheader("Enter LinkedIn URLs")

company_url = st.text_input(
    "LinkedIn Company URL",
    placeholder="https://www.linkedin.com/company/example/",
    help="Optional if Job URL is provided"
)

job_url = st.text_input(
    "LinkedIn Job Posting URL",
    placeholder="https://www.linkedin.com/jobs/view/123456789/",
    help="Optional if Company URL is provided"
)

# ---------------- AUTO VALIDATION ----------------
def valid_company_url(url):
    return url.startswith("https://www.linkedin.com/company/")

def valid_job_url(url):
    return url.startswith("https://www.linkedin.com/jobs/")

# ---------------- AUTO ANALYSIS ----------------
# ---------------- AUTO ANALYSIS ----------------
if company_url or job_url:

    if company_url and not valid_company_url(company_url):
        st.warning("⚠️ Invalid LinkedIn company URL")
        st.stop()

    if job_url and not valid_job_url(job_url):
        st.warning("⚠️ Invalid LinkedIn job URL")
        st.stop()

    with st.spinner("🔄 Analyzing..."):
        try:
            result = analyzer.analyze_company(
                company_url=company_url if company_url else None,
                job_url=job_url if job_url else None
            )

            st.divider()
            st.subheader("📊 Analysis Result")

            output = result.strip().lower()

            if output.startswith("yes"):
                st.success("✅ Company meets ALL requirements")

            elif output.startswith("wrong"):
                st.error("❌ Company does NOT meet all requirements")

            else:
                st.warning("⚠️ Unexpected model output")
                st.code(result, language="text")

        except Exception as e:
            st.error(f"❌ Analysis error: {e}")

# ---------------- FOOTER ----------------
st.divider()
st.markdown(
    "<div style='text-align:center;color:gray;font-size:0.85em;'>"
    "⚡ Groq + Llama 3.1 70B • Auto-analysis enabled"
    "</div>",
    unsafe_allow_html=True
)
