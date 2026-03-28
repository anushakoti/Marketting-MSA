import base64
import json
import logging
import random
import boto3
from pathlib import Path
from botocore.exceptions import ClientError
from langchain_core.tools import tool
from datetime import datetime
from supabase_client import supabase_mgr

logger = logging.getLogger(__name__)

# --- Supabase Storage Bucket ---
LOGO_BUCKET = "assets"

class ImageError(Exception):
    """Custom exception for errors returned by Amazon Titan Image Generator V2."""
    def __init__(self, message):
        self.message = message


def _generate_image(body: str) -> bytes:
    bedrock = boto3.client(service_name="bedrock-runtime", region_name="us-east-1")
    response = bedrock.invoke_model(
        body=body,
        modelId="amazon.titan-image-generator-v2:0",
        accept="application/json",
        contentType="application/json",
    )
    response_body = json.loads(response.get("body").read())
    finish_reason = response_body.get("error")
    if finish_reason is not None:
        raise ImageError(f"Image generation error. Error is {finish_reason}")
    base64_image = response_body.get("images")[0]
    return base64.b64decode(base64_image.encode("ascii"))


@tool
def generate_logo(business_name: str) -> str:
    """Generate a professional logo for a business using Amazon Titan Image Generator.
    Use this tool when the user asks for logo creation, visual branding,
    brand identity design, or any image/logo generation for their business."""
    prompt = (
        f"Professional modern logo for {business_name} company, "
        f"clean minimalist design, corporate branding, vector style"
    )
    body = json.dumps({
        "taskType": "TEXT_IMAGE",
        "textToImageParams": {"text": prompt},
        "imageGenerationConfig": {
            "numberOfImages": 1,
            "height": 512,
            "width": 512,
            "cfgScale": 8.0,
            "seed": random.randint(0, 2147483647),
        },
    })
    try:
        image_bytes = _generate_image(body)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        unique_id = random.randint(1000, 9999)
        file_name = f"{timestamp}_{unique_id}.png"
        file_path = f"logos/{file_name}"
 
        try:
            supabase_mgr.client.storage.from_(LOGO_BUCKET).upload(
                path=file_path, 
                file=image_bytes, 
                file_options={"content-type": "image/png"}
            )
            
            public_url = supabase_mgr.client.storage.from_(LOGO_BUCKET).get_public_url(file_path)
            
            logger.info("Successfully generated logo for %s and uploaded to Supabase", business_name)
            return json.dumps({
                "message": f"Logo generated successfully for {business_name}!",
                "image_url": public_url,
                "business_name": business_name
            })
        except Exception as e:
            logger.error("Error uploading to Supabase: %s", str(e))
            return f"Error uploading to cloud storage: {str(e)}"

    except (ClientError, ImageError) as e:
        msg = e.message if isinstance(e, ImageError) else e.response["Error"]["Message"]
        logger.error("Error generating logo: %s", msg)
        return f"Error generating logo: {msg}"
