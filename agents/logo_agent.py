import base64
import json
import logging
import random
import boto3
from botocore.exceptions import ClientError
from langchain_core.tools import tool

logger = logging.getLogger(__name__)


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
        output_path = "logo.png"
        with open(output_path, "wb") as f:
            f.write(image_bytes)
        logger.info("Successfully generated logo for %s", business_name)
        return f"Logo generated successfully for {business_name}! The logo is saved to {output_path}."
    except (ClientError, ImageError) as e:
        msg = e.message if isinstance(e, ImageError) else e.response["Error"]["Message"]
        logger.error("Error generating logo: %s", msg)
        return f"Error generating logo: {msg}"
