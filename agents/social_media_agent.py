from langchain_aws import ChatBedrock
from langchain_core.messages import HumanMessage
from langchain_core.tools import tool

_llm = ChatBedrock(model="global.anthropic.claude-haiku-4-5-20251001-v1:0")


@tool
def create_social_media_content(business_name: str, platform: str) -> str:
    """ Create platform-specific social media content for a business. 
    Use this when user asks for social media posts, captions, or content ideas for platforms like Instagram, Twitter, LinkedIn, etc. 
    Always specify the platform in the request. """
   
    response= _llm.invoke([
       HumanMessage(content=(
            f"Create engaging social media content for {platform} for the given business.\n\n"
            f"Include:\n"
            f"- Eye-catching post caption\n"
            f"- Hashtag suggestions\n"
            f"- Post type recommendations (image, video, story, poll, etc.)\n"
            f"- Engagement tips\n"
            f"- Content themes or topics\n\n"
            f"- A clear CTA to encourage audience interaction\n\n"
            f"Business Name: {business_name}\n"
            f"Platform: {platform}\n\n"
            f"Create social media content:"
       )
                    )
    ])
    return response.content
