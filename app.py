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
This tool analyzes LinkedIn **company pages or job posts** to determine eligibility based on:
- Industry segments
- Company size (50–500 or funded startups)
- Locations (US & India tech hubs)
- Key decision makers
- AI / ML intent signals
""")

st.divider()

# ---------------- LOAD ANALYZER ----------------
@st.cache_resource
def load_analyzer():
    try:
        return CompanyAnalyzer()
    except Exception as e:
        st.error(f"❌ Failed to initialize analyzer: {e}")
        st.info(
            "Ensure GROQ_API_KEY is set in config.toml or Streamlit secrets.\n"
            "Get a key at https://console.groq.com"
        )
        st.stop()

analyzer = load_analyzer()

# ---------------- INPUT SECTION ----------------
st.subheader("Enter LinkedIn URL")

input_type = st.radio(
    "URL Type",
    ["Company Page", "Job Post"],
    horizontal=True
)

company_url = ""
job_url = ""

if input_type == "Company Page":
    company_url = st.text_input(
        "LinkedIn Company URL",
        placeholder="https://www.linkedin.com/company/example/",
        help="Only LinkedIn company page URLs are allowed"
    )
else:
    job_url = st.text_input(
        "LinkedIn Job URL",
        placeholder="https://www.linkedin.com/jobs/view/123456789/",
        help="Only LinkedIn job post URLs are allowed"
    )

# ---------------- ANALYZE BUTTON ----------------
if st.button("🚀 Analyze", type="primary", use_container_width=True):

    # -------- VALIDATION --------
    if input_type == "Company Page":
        if not company_url:
            st.warning("⚠️ Please enter a LinkedIn company URL")
            st.stop()
        if not company_url.startswith("https://www.linkedin.com/company/"):
            st.warning("⚠️ Invalid LinkedIn company URL")
            st.stop()

    if input_type == "Job Post":
        if not job_url:
            st.warning("⚠️ Please enter a LinkedIn job URL")
            st.stop()
        if not job_url.startswith("https://www.linkedin.com/jobs/"):
            st.warning("⚠️ Invalid LinkedIn job URL")
            st.stop()

    # -------- ANALYSIS --------
    with st.spinner("🔄 Analyzing..."):
        try:
            result = analyzer.analyze_company(
                company_url=company_url if company_url else None,
                job_url=job_url if job_url else None
            )

            st.divider()
            st.subheader("📊 Analysis Result")

            # -------- RESULT HANDLING --------
            if result.strip().lower().startswith("yes"):
                st.success("✅ Company meets ALL requirements")

                try:
                    json_start = result.find("{")
                    if json_start != -1:
                        details = json.loads(result[json_start:])

                        col1, col2 = st.columns(2)

                        with col1:
                            st.markdown("**🏢 Industry Segments**")
                            for v in details.get("industry_segments", []):
                                st.markdown(f"- {v}")

                            st.markdown("**👥 Company Size**")
                            st.markdown(details.get("company_size", "N/A"))

                            st.markdown("**📍 Locations**")
                            for v in details.get("locations", []):
                                st.markdown(f"- {v}")

                        with col2:
                            st.markdown("**🎯 Decision Makers**")
                            for v in details.get("key_decision_makers", []):
                                st.markdown(f"- {v}")

                            st.markdown("**💡 Intent Triggers**")
                            for v in details.get("intent_triggers", []):
                                st.markdown(f"- {v}")

                        st.markdown("**🔗 Links**")
                        st.markdown(f"- Company: {details.get('company_link', 'N/A')}")
                        st.markdown(f"- Job: {details.get('job_link', 'N/A')}")
                    else:
                        st.code(result, language="text")

                except Exception:
                    st.code(result, language="text")

            elif result.strip().lower().startswith("wrong"):
                st.error("❌ Company does NOT meet all requirements")

            else:
                st.warning("⚠️ Unexpected response format")
                st.code(result, language="text")

        except Exception as e:
            st.error(f"❌ Error during analysis: {e}")

# ---------------- FOOTER ----------------
st.divider()
st.markdown(
    "<div style='text-align:center;color:gray;font-size:0.85em;'>"
    "⚡ Groq + Llama 3.1 70B • Ultra-fast inference"
    "</div>",
    unsafe_allow_html=True
)
