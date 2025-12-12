import streamlit as st
import json
from model import CompanyAnalyzer

# Page config
st.set_page_config(
    page_title="Company Analyzer",
    page_icon="🔍",
    layout="wide"
)

# Title and description
st.title("🔍 LinkedIn Company Analyzer")
st.caption("⚡ Powered by Groq + Llama 3.1 70B")
st.markdown("""
This tool analyzes LinkedIn company pages to determine if they meet specific requirements for:
- Industry segments (SaaS, FinTech, HealthTech, etc.)
- Company size (50-500 employees or funded startups)
- Locations (US & India tech hubs)
- Key decision makers
- Intent triggers (AI/ML hiring, funding, etc.)
""")

st.divider()

# Initialize analyzer
@st.cache_resource
def load_analyzer():
    try:
        return CompanyAnalyzer()
    except Exception as e:
        st.error(f"❌ Error initializing analyzer: {str(e)}")
        st.info("💡 Make sure you have:\n- Created `config.toml` with your GROQ_API_KEY (local)\n- Added GROQ_API_KEY to Streamlit secrets (cloud)\n\nGet your free API key at: https://console.groq.com")
        st.stop()

analyzer = load_analyzer()

# Input section
st.subheader("Enter LinkedIn Company URL")
url = st.text_input(
    "LinkedIn URL",
    placeholder="https://www.linkedin.com/company/example/",
    help="Enter the full LinkedIn company page URL"
)

# Analyze button
if st.button("🚀 Analyze Company", type="primary", use_container_width=True):
    if not url:
        st.warning("⚠️ Please enter a LinkedIn URL")
    elif not url.startswith("https://www.linkedin.com/company/"):
        st.warning("⚠️ Please enter a valid LinkedIn company URL")
    else:
        with st.spinner("🔄 Analyzing company page..."):
            try:
                # Analyze company
                result = analyzer.analyze_company(url)
                
                # Display result
                st.divider()
                st.subheader("📊 Analysis Result")
                
                # Check if company meets requirements
                if result.strip().lower().startswith("yes"):
                    st.success("✅ Company meets ALL requirements!")
                    
                    # Try to parse JSON details
                    try:
                        # Extract JSON part
                        json_start = result.find("{")
                        if json_start != -1:
                            json_str = result[json_start:]
                            details = json.loads(json_str)
                            
                            # Display details in columns
                            col1, col2 = st.columns(2)
                            
                            with col1:
                                st.markdown("**🏢 Industry Segments:**")
                                for segment in details.get("industry_segments", []):
                                    st.markdown(f"- {segment}")
                                
                                st.markdown("**👥 Company Size:**")
                                st.markdown(f"- {details.get('company_size', 'N/A')}")
                                
                                st.markdown("**📍 Locations:**")
                                for location in details.get("locations", []):
                                    st.markdown(f"- {location}")
                            
                            with col2:
                                st.markdown("**🎯 Key Decision Makers:**")
                                for maker in details.get("key_decision_makers", []):
                                    st.markdown(f"- {maker}")
                                
                                st.markdown("**💡 Intent Triggers:**")
                                for trigger in details.get("intent_triggers", []):
                                    st.markdown(f"- {trigger}")
                        else:
                            st.info("✅ Company qualifies but detailed breakdown not available")
                            st.code(result, language="text")
                    except json.JSONDecodeError:
                        st.info("✅ Company qualifies but detailed breakdown not available")
                        st.code(result, language="text")
                
                elif result.strip().lower().startswith("wrong"):
                    st.error("❌ Company does NOT meet all requirements")
                    st.info("The company may be missing one or more of the required criteria.")
                
                else:
                    st.warning("⚠️ Unexpected response format")
                    st.code(result, language="text")
                
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")
                st.info("Please check the URL and try again.")

# Footer
st.divider()
st.markdown("""
<div style='text-align: center; color: gray; font-size: 0.9em;'>
    <p>⚡ Powered by Groq + Llama 3.1 70B & LangChain</p>
    <p style='font-size: 0.8em;'>Ultra-fast inference • 300+ tokens/second</p>
</div>
""", unsafe_allow_html=True)