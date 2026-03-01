import json
from pydantic import BaseModel, Field
from typing import List, Literal
from langchain_ollama import ChatOllama
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from config import USE_GROQ, GROQ_API_KEY, LOCAL_LLM_MODEL

# 1. Force the SLM to output the exact types we need
class ScoringResult(BaseModel):
    clarity_score: int = Field(description="Score 0-100", ge=0, le=100)
    impact_score: int = Field(description="Score 0-100", ge=0, le=100)
    budget_score: int = Field(description="Score 0-100", ge=0, le=100)
    locality_alignment: int = Field(description="Score 0-100", ge=0, le=100)
    beneficiary_definition: int = Field(description="Score 0-100", ge=0, le=100)
    strengths: List[str] = Field(description="3 things the proposal does well")
    weaknesses: List[str] = Field(description="3 things that could get it rejected")
    recommendations: List[str] = Field(description="3 specific improvements")
    funder_readiness: Literal["strong", "moderate", "needs_work"]

# 2. Configure Ollama for JSON and sufficient context
def get_scoring_llm():
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
            num_ctx=4096 
        )
    
SCORING_PROMPT = ChatPromptTemplate.from_messages([
    ("system", """You are an expert grant evaluator with 20 years of experience reviewing NGO proposals.
You understand what funders look for and what makes proposals succeed or fail.

Score the proposal on the following dimensions (0-100 each):

1. clarity_score: How clearly are goals and activities defined?
2. impact_score: Is the expected impact measurable and realistic?
3. budget_score: Does the budget seem realistic for the locality and activities?
4. locality_alignment: Is the geographic focus clear and appropriate?
5. beneficiary_definition: Are target beneficiaries specific and well-defined?
6. overall_score: Weighted average of above scores

Also provide:
- strengths: list of 3 things the proposal does well
- weaknesses: list of 3 things that could get it rejected
- recommendations: list of 3 specific improvements before submitting
- funder_readiness: "strong" | "moderate" | "needs_work"

Return ONLY valid JSON, nothing else.

FUTURE SCOPE NOTE: In future versions, this agent will compare against a database 
of historically successful grants to give data-driven scoring."""),
    ("human", """Score this NGO proposal:

{proposal_json}""")
])

def score_proposal(proposal: dict) -> dict:
    mode_name = "Groq" if USE_GROQ else "Local Ollama"
    print(f"⚖️ Scoring proposal via {mode_name}...")
    
    llm = get_scoring_llm()
    structured_llm = llm.with_structured_output(ScoringResult)
    chain = SCORING_PROMPT | structured_llm
    
    try:
        # Step 1: LLM Reasoning
        result = chain.invoke({"proposal_json": json.dumps(proposal, indent=2)})
        scored = result.model_dump()
        
        # Step 2: Deterministic Math (Don't let LLMs do average/weighted math)
        score_values = [
            scored["clarity_score"], 
            scored["impact_score"], 
            scored["budget_score"], 
            scored["locality_alignment"], 
            scored["beneficiary_definition"]
        ]
        # Calculate overall score in Python for 100% accuracy
        scored["overall_score"] = int(sum(score_values) / len(score_values))
        
        scored["agent"] = f"scoring_agent_{'groq' if USE_GROQ else 'local'}"
        return scored
        
    except Exception as e:
        print(f"❌ Scoring Error: {e}")
        return {"error": "Failed to score proposal", "details": str(e)}