import re
import os
import toml
from langchain_community.document_loaders import WebBaseLoader
from langchain_core.prompts import PromptTemplate
from langchain_groq import ChatGroq

class CompanyAnalyzer:
    def __init__(self):
        """Initialize the analyzer with Groq API key"""
        self.api_key = None
        
        # Try multiple sources for API key
        try:
            # 1. Try environment variable
            if 'GROQ_API_KEY' in os.environ:
                self.api_key = os.environ.get('GROQ_API_KEY')
            
            # 2. Try GROQ_API_KEY.toml file
            elif os.path.exists('GROQ_API_KEY.toml'):
                config = toml.load('GROQ_API_KEY.toml')
                self.api_key = config.get('GROQ_API_KEY')
            
            if not self.api_key:
                raise ValueError("GROQ_API_KEY not found")
                
        except Exception as e:
            raise Exception(f"Error loading API key: {str(e)}")
        
        # Initialize Groq LLM with Llama 3.1 70B
        self.llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    api_key=self.api_key,
    temperature=0.0,
    max_tokens=800
)

        
        # Define prompt template
        self.prompt_extract = PromptTemplate.from_template(
    """INPUT:
SCRAPED TEXT:
{clean_data}

ROLE:
You are a STRICT rule-based validator.
You must NOT infer, estimate, paraphrase, or assume.
Accept ONLY what is explicitly stated in the input text.

If ANY rule fails, output "wrong".
Only if ALL rules pass, output "yes".

--------------------------------
INDUSTRY (REQUIRED — AT LEAST ONE):

The input text must contain AT LEAST ONE of the following
EXACT, CASE-INSENSITIVE KEYWORDS:

Software
IT Services
SaaS
Technology
FinTech
HealthTech
AI
Automation
E-commerce

--------------------------------
COMPANY SIZE (MANDATORY — HARD RULE):

ACCEPT ONLY IF AT LEAST ONE of the following EXACT PHRASES appears:

- "51–200 employees"
- "201–500 employees"
- "501–1000 employees"
- "funded startup"
- "Seed"
- "Series A"
- "Series B"
- "VC-backed"

IMMEDIATE REJECTION IF ANY of the following appear:

- "1000+ employees"
- "5000+ employees"
- "10k+"
- "enterprise"
- "multinational"
- "MNC"
- "global workforce"
- "large enterprise"

If neither acceptance nor rejection evidence is present → REJECT.

--------------------------------
LOCATION (REQUIRED — AT LEAST ONE):

The input text must explicitly mention AT LEAST ONE of:

US:
CA, TX, NY, MA, FL

India:
Bengaluru, Hyderabad, Pune, Gurgaon, Chennai, Mumbai, NCR

Exact text match required. No inference.

-----------------------------
INTENT SIGNALS (MANDATORY):
The input text must explicitly contain AT LEAST ONE keyword related to
ServiceNow, AI/ML, or Web Development (e.g., "ServiceNow", "AI engineer",
"machine learning", "Web developer", "Full stack developer").
Generic hiring terms or unrelated automation references are NOT valid.
No inference or assumption is allowed.

Valid examples:
- Company website
- LinkedIn com
"""
)

        
        # Create chain
        self.chain = self.prompt_extract | self.llm
    
    def load_and_clean_page(self, url):
        """Load webpage and clean the text content"""
        try:
            loader = WebBaseLoader(url)
            page_data = loader.load().pop().page_content
            
            # Clean text
            clean_text = re.sub(r'[ ]{2,}', ' ', page_data)
            clean_text = re.sub(r'[\n\r]{2,}', '\n', clean_text)
            clean_text = clean_text.replace("\t", "")
            clean_text = "\n".join(line.strip() for line in clean_text.splitlines())
            clean_text = "\n".join(line for line in clean_text.splitlines() if line.strip())
            
            return clean_text
        except Exception as e:
            raise Exception(f"Error loading webpage: {str(e)}")
    
    def analyze_company(self, company_url=None, job_url=None):
        try:
            texts = []

            if company_url:
                texts.append(self.load_and_clean_page(company_url))

            if job_url:
                texts.append(self.load_and_clean_page(job_url))

            if not texts:
                raise ValueError("No valid URL provided")

            clean_text = "\n\n".join(texts)

            result = self.chain.invoke({"clean_data": clean_text})
            return result.content

        except Exception as e:
            raise Exception(f"Error analyzing company: {str(e)}")
