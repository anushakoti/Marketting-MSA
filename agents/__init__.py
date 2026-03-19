from agents.strategy_agent import create_marketing_strategy
from agents.seo_agent import generate_seo_keywords
from agents.logo_agent import generate_logo
from agents.domain_agent import get_domain_suggestions
from agents.social_media_agent import create_social_media_content
from agents.email_campaign_agent import create_email_campaign
from agents.tagline_agent import generate_taglines
from agents.ad_copy_agent import create_ad_copy

tools = [
    create_marketing_strategy
    , generate_seo_keywords
    , generate_logo
    , get_domain_suggestions        
    , create_social_media_content   
    , create_email_campaign
    , generate_taglines
    , create_ad_copy
    
    ]