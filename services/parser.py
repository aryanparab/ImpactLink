import os
import tempfile
from typing import List, Optional
from pydantic import BaseModel, Field
# Added TextLoader for handling non-PDFs gracefully
from langchain_community.document_loaders import PyPDFLoader, TextLoader 
from langchain_core.prompts import ChatPromptTemplate
from langchain_ollama import ChatOllama
from langchain_groq import ChatGroq
from config import USE_GROQ, GROQ_API_KEY, LOCAL_LLM_MODEL

# --- Pydantic Model (structured output) ---

class ProposalFeatures(BaseModel):
    organization_name: str = Field(description="Official name of the NGO or organization")
    project_title: str = Field(description="The name of the specific project or initiative")
    primary_mission: str = Field(description="A concise 2-3 sentence summary of the project's core goal")
    target_beneficiaries: List[str] = Field(description="Who receives help (e.g., 'At-risk youth', 'Rural farmers')")
    geographic_focus: List[str] = Field(description="Specific cities, regions, or countries where the project takes place")
    sdg_alignment: List[str] = Field(description="Which UN Sustainable Development Goals fit best (e.g., 'Goal 1: No Poverty')")
    requested_amount: Optional[int] = Field(description="Total budget requested in USD, if mentioned. Return null if not found.")
    budget_breakdown: List[str] = Field(description="High-level budget categories mentioned (e.g., 'Labor', 'Equipment', 'Travel')")
    cause_area: str = Field(description="Primary cause area (e.g., 'education', 'healthcare', 'climate', 'women empowerment')")
    key_activities: List[str] = Field(description="Main project activities listed in the proposal")


# --- Chain Builder ---
def get_extraction_llm():
    if USE_GROQ:
        return ChatGroq(
            model="llama-3.3-70b-versatile", 
            temperature=0, 
            groq_api_key=GROQ_API_KEY
        )
    else:
        return ChatOllama(
            model=LOCAL_LLM_MODEL, 
            temperature=0, 
            format="json",
            num_ctx=8192  # Essential for long PDF context
        )

def build_extraction_chain():
    llm = get_extraction_llm()
    structured_llm = llm.with_structured_output(ProposalFeatures)

    prompt = ChatPromptTemplate.from_messages([
        ("system", """You are an expert grant reviewer. Extract metadata from the NGO proposal.
If information is missing, infer from context or leave blank.
CRITICAL: Return ONLY a valid JSON object matching the requested schema."""),
        ("user", "Here is the proposal text:\n\n{text}")
    ])

    return prompt | structured_llm

# --- Main Parse Function (called by FastAPI) ---

def parse_proposal(file_bytes: bytes, filename: str) -> dict:
    is_pdf = filename.lower().endswith(".pdf")
    suffix = ".pdf" if is_pdf else ".txt"

    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        tmp.write(file_bytes)
        tmp_path = tmp.name

    try:
        if is_pdf:
            loader = PyPDFLoader(tmp_path)
        else:
            loader = TextLoader(tmp_path, encoding="utf-8")
            
        pages = loader.load()
        # Grab the first 10 pages to balance context and speed
        combined_text = "\n".join([page.page_content for page in pages[:10]])

        mode_name = "Groq" if USE_GROQ else "Local Ollama"
        print(f"🧠 Extracting features using {mode_name}...")
        
        chain = build_extraction_chain()
        result = chain.invoke({"text": combined_text})

        return result.model_dump()

    except Exception as e:
        print(f"❌ Extraction Error: {e}")
        return {"error": "Failed to parse document", "details": str(e)}
    finally:
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)