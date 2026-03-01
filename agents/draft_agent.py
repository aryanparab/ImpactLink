"""
agents/draft_agent.py
Multi-section proposal drafting agent.
Takes a parsed proposal + target grant, writes a complete funder-specific proposal.
Streams section by section.
"""

import json
import re
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from dotenv import load_dotenv

load_dotenv()

llm = ChatGroq(model="llama-3.3-70b-versatile", temperature=0.3)

# Each section is drafted separately for quality + streaming
SECTIONS = [
    {
        "key": "executive_summary",
        "title": "Executive Summary",
        "instructions": "Write a compelling 2-paragraph executive summary. Lead with the problem, then introduce the organization and solution. Tailor the language to match this funder's priorities.",
    },
    {
        "key": "problem_statement",
        "title": "Problem Statement",
        "instructions": "Write a 3-paragraph problem statement with specific data points. Define the problem clearly, show its scale, and explain why this community is uniquely affected. Reference the geographic focus.",
    },
    {
        "key": "proposed_solution",
        "title": "Proposed Solution & Activities",
        "instructions": "Describe the project activities in detail. For each key activity, explain what will happen, who will be involved, and what the expected outcome is. Show clear cause-effect logic.",
    },
    {
        "key": "target_beneficiaries",
        "title": "Target Beneficiaries",
        "instructions": "Describe who will benefit, how many people, and how they will be selected. Be specific. Include demographic details if available.",
    },
    {
        "key": "organizational_capacity",
        "title": "Organizational Capacity",
        "instructions": "Describe why this organization is uniquely positioned to execute this project. Reference past work, partnerships, and team expertise.",
    },
    {
        "key": "evaluation_plan",
        "title": "Evaluation & Impact Measurement",
        "instructions": "Describe how success will be measured. List 3-5 specific, measurable KPIs. Explain data collection methods and reporting timeline.",
    },
    {
        "key": "budget_narrative",
        "title": "Budget Narrative",
        "instructions": "Write a budget justification for each budget category. Explain why each cost is necessary and reasonable. Ensure total aligns with the requested amount.",
    },
    {
        "key": "sustainability",
        "title": "Sustainability Plan",
        "instructions": "Explain how the project will continue after grant funding ends. Reference diversified funding, community ownership, or earned income strategies.",
    },
]

SECTION_PROMPT = ChatPromptTemplate.from_messages([
    ("system", """You are an expert grant writer with 20 years of experience writing winning proposals for NGOs.
You write in a clear, evidence-based, and compelling style tailored to each funder.

Your task is to write ONE specific section of a grant proposal.
- Tailor every sentence to match the funder's stated priorities
- Reference the organization's actual mission and activities
- Be specific — avoid vague claims
- Write in professional grant language
- Length: 200-350 words for this section

Return ONLY the section text, no headers, no JSON."""),
    ("user", """Write the "{section_title}" section for this grant proposal.

SECTION INSTRUCTIONS:
{instructions}

ORGANIZATION PROFILE:
{proposal}

TARGET GRANT / FUNDER:
{grant}

Write the section now:""")
])


def draft_proposal(proposal: dict, grant: dict) -> dict:
    """
    Drafts a complete proposal for a specific grant.
    Returns dict with all sections + metadata.
    """
    chain = SECTION_PROMPT | llm
    sections = {}

    for section in SECTIONS:
        response = chain.invoke({
            "section_title": section["title"],
            "instructions":  section["instructions"],
            "proposal":      json.dumps(proposal, indent=2),
            "grant":         json.dumps({
                "title":       grant.get("title", ""),
                "agency":      grant.get("agency", ""),
                "description": grant.get("description", ""),
                "focus_areas": grant.get("focus_areas", ""),
                "eligibility": grant.get("eligibility", []),
            }, indent=2),
        })
        sections[section["key"]] = {
            "title":   section["title"],
            "content": response.content.strip(),
        }

    return {
        "grant_id":    grant.get("grant_id", ""),
        "grant_title": grant.get("title", ""),
        "agency":      grant.get("agency", ""),
        "org_name":    proposal.get("organization_name", ""),
        "sections":    sections,
        "section_order": [s["key"] for s in SECTIONS],
    }


def draft_proposal_stream(proposal: dict, grant: dict):
    """
    Generator — yields section drafts one at a time as they complete.
    Used by the streaming FastAPI endpoint.
    Each yield is a JSON string the frontend can parse.
    """
    chain = SECTION_PROMPT | llm

    for section in SECTIONS:
        response = chain.invoke({
            "section_title": section["title"],
            "instructions":  section["instructions"],
            "proposal":      json.dumps(proposal, indent=2),
            "grant":         json.dumps({
                "title":       grant.get("title", ""),
                "agency":      grant.get("agency", ""),
                "description": grant.get("description", ""),
                "focus_areas": grant.get("focus_areas", ""),
                "eligibility": grant.get("eligibility", []),
            }, indent=2),
        })

        yield json.dumps({
            "key":     section["key"],
            "title":   section["title"],
            "content": response.content.strip(),
            "done":    False,
        }) + "\n"

    # Final signal
    yield json.dumps({"done": True}) + "\n"