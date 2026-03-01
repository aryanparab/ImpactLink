import json
from config import USE_GROQ  # Import the flag
from services.parser import parse_proposal
from agents.scoring_agent import score_proposal
from services.vector_store import find_similar_grants

PDF_PATH = "data/p1.pdf"

print("=" * 50)
print(f"PIPELINE STARTING (Mode: {'GROQ' if USE_GROQ else 'LOCAL'})")
print("=" * 50)

# ── STEP 1: Parse ────────────────────────────────────────
print("\nSTEP 1: Parsing Proposal PDF...")
with open(PDF_PATH, "rb") as f:
    file_bytes = f.read()

proposal = parse_proposal(file_bytes, "p1.pdf")
# print(json.dumps(proposal, indent=2)) # Commented for brevity

# ── STEP 2: Score ────────────────────────────────────────
print("\nSTEP 2: Scoring Proposal...")
scoring = score_proposal(proposal)

# ── STEP 3: RAG Match ────────────────────────────────────
print(f"\nSTEP 3: Finding Grants with {'Groq Cloud' if USE_GROQ else 'Local LLM'}...")
# find_similar_grants will now use the flag internally 
matches = find_similar_grants(proposal, top_k=5)

for i, match in enumerate(matches):
    print(f"\n#{i+1} — {match['title']}")
    print(f"   Score:      {match['similarity_score']}% | Fit: {match['fit_level'].upper()}")
    print(f"   Why match:  {match['match_explanation']}")
    print(f"   💡 Tip:     {match['application_tip']}")

print("\n" + "=" * 50)
print("PIPELINE COMPLETE")
print("=" * 50)