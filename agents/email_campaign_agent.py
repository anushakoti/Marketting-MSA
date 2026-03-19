from langchain_aws import ChatBedrock
from langchain_core.messages import HumanMessage
from langchain_core.tools import tool

_llm = ChatBedrock(model="global.anthropic.claude-haiku-4-5-20251001-v1:0")

@tool
def create_email_campaign(business_name: str) -> str:
    """Generate a 3-email marketing sequence for a business.
    Use this tool when the user asks for email campaigns, email marketing,
    drip sequences, newsletter content, or email automation for their business."""
    response = _llm.invoke([
        HumanMessage(content=(
            f"Create a 3-email marketing sequence for the business below.\n\n"
            f"Email 1 — Welcome Email:\n"
            f"- Warm introduction to the brand\n"
            f"- Set expectations for what subscribers will receive\n"
            f"- Soft CTA (explore the website, follow on social media)\n\n"
            f"Email 2 — Value Email:\n"
            f"- Provide genuine value (tips, insights, or a resource)\n"
            f"- Build trust and authority\n"
            f"- Medium CTA (download a guide, read a blog post)\n\n"
            f"Email 3 — Conversion Email:\n"
            f"- Present the core offer or service\n"
            f"- Include social proof or urgency\n"
            f"- Strong CTA (buy now, book a call, sign up)\n\n"
            f"For each email provide:\n"
            f"- Subject line (and a preview text)\n"
            f"- Full email body copy\n"
            f"- CTA button text\n\n"
            f"Business Name: {business_name}\n\n"
            f"Generate the email campaign:"
        ))
    ])
    return response.content