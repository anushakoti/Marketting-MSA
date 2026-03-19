from langchain_aws import ChatBedrock
from langchain_core.messages import HumanMessage
from langchain_core.tools import tool

_llm = ChatBedrock(model="global.anthropic.claude-haiku-4-5-20251001-v1:0")

@tool
def generate_taglines(business_name: str) -> str:
    """Generate brand taglines, slogans, and elevator pitches for a business.
    Use this tool when the user asks for taglines, slogans, brand messaging,
    elevator pitches, or catchy phrases for their business."""
    
    response= _llm.invoke([
       HumanMessage(content=(
            f"Generate 10 unique brand taglines/slogans for the business below.\n\n"
            f"For each tagline provide:\n"
            f"- The tagline itself\n"
            f"- Tone (e.g., professional, playful, bold, inspirational)\n"
            f"- Best use context (e.g., website header, social media bio, ad campaign, business card)\n\n"
            f"Also include:\n"
            f"- 1 elevator pitch (30 seconds / ~75 words) that captures the brand essence\n"
            f"- 1 brand positioning statement\n\n"
            f"Make taglines memorable, concise, and distinct from each other.\n\n"
            f"Business Name: {business_name}\n\n"
            f"Generate taglines:"
       ))
    ])      
    return response.content