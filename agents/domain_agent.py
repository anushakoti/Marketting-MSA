from langchain_aws import ChatBedrock
from langchain_core.messages import HumanMessage
from langchain_core.tools import tool

_llm = ChatBedrock(model="global.anthropic.claude-haiku-4-5-20251001-v1:0")

@tool
def get_domain_suggestions(business_name: str )-> str:
    """Generate 10 unique domain name suggestions for a business.
    Use this tool when the user asks for domain name ideas, URL suggestions,
    or anything related to choosing a web address for their business. """
    
    response= _llm.invoke([
       HumanMessage(content=(
             f"Generate 10 unique domain names based on the business name provided.\n\n"
            f"Requirements:\n"
            f"- Use the exact business name (if available as .com)\n"
            f"- Add common business suffixes: app, hub, pro, tech, online, digital, solutions, services\n"
            f"- Use abbreviations or shortened versions of the business name\n"
            f"- Focus primarily on .com domains, with some .net, .org, or .io alternatives\n"
            f"- Output a numbered list of exactly 10 domain names\n\n"
            f"Business Name: {business_name}\n\n"
            f"Generate 10 domain names:"
       ))
    ])      
    return (
        f" Here are 10 unique domain name suggestions for your business '{business_name}':\n\n {response.content}\n\n"
        f"Please review the following domain name suggestions and let me know if you would like more options or if you have any specific preferences:\n\n"
    )    