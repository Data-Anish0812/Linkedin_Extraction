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
            temperature=0.1,
            max_tokens=2000
        )
        
        # Define prompt template
        self.prompt_extract = PromptTemplate.from_template(
            """SCRAPED TEXT FROM WEBSITE:

{clean_data}

SOURCE LINKS:

{
"input_url": "{url}",
"company_url": "{company_url_if_available}"
}

INSTRUCTION:

Text may come from a LinkedIn company page OR job post.

RULE:

If input is a job post, first infer/extract the company and evaluate the company eligibility using the job + company info.

If input is a company page, evaluate directly.

TASK: Check if ALL conditions are met.

INDUSTRY: SaaS, FinTech, HealthTech, RetailTech, EdTech, AI startups, Automation firms, Manufacturing, Automotive AI
COMPANY SIZE: 50–500 employees OR funded startup (Seed–Series C)
LOCATIONS: US(Silicon Valley, Austin, NY, Boston), India(Bangalore, Hyderabad, Gurgaon)
DECISION MAKERS: Founder/Co-Founder, CTO, VP Engineering, Head of AI/Innovation
INTENT: Hiring AI/ML, funding raised, AI features launched, AI adoption/pilots

OUTPUT RULES:

If ALL matched → output ONLY:
yes
Then JSON:
{"industry_segments":[],"company_size":"","locations":[],"key_decision_makers":[],"intent_triggers":[],"company_link":"","job_link":""}

If ANY fail → output ONLY:
wrong

NO explanations, extra text, or formatting outside rules.
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
    
    def analyze_company(self, url):
        """Analyze company from LinkedIn URL"""
        try:
            # Load and clean page
            clean_text = self.load_and_clean_page(url)
            
            # Run analysis
            result = self.chain.invoke({"clean_data": clean_text})
            
            return result.content
        except Exception as e:

            raise Exception(f"Error analyzing company: {str(e)}")

