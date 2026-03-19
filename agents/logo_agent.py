import base64
import io
import json
import logging
import boto3
import random
from botocore.exceptions import ClientError
from langchain_core.tools import tool

logger = logging.getLogger(__name__)

class ImageError(Exception):
    """Custom exception for image generation errors."""
    def __init__(self, message):
        super().__init__(message)
        self.message = message


def _generate_image(body:str)-> bytes:
    """Generate image from bedrock model and return image bytes."""
    bedrock = boto3.client(service_name='bedrock-runtime')
    response = bedrock.invoke_model(
        modelId="amazon.titan-image-generator-v2:0",
        content_type="application/json",
        accept="application/json",
        body={

        }
    )
    response_body = json.loads(response.get("body").read())

    finish_reason = response_body.get("error")
    if finish_reason is not None:
        raise ImageError(f"Image generation failed: {finish_reason}")
    base64_image = response_body.get("image")[0]
    return base64.b64decode(base64_image.encode("ascii"))

@tool
def generate_logo(business_name: str) -> str:
    """Generate a professional logo for a business using Amazon Titan Image Generator.
    Use this tool when the user asks for logo creation, visual branding,
    brand identity design, or any image/logo generation for their business."""

    prompt = (f"Create a professional logo for a business named '{business_name}'. "
              "The logo should be visually appealing, unique, and reflect the essence of the business."
              " Consider using relevant symbols, colors, and typography that align with the business name and industry. "
              "The logo should be suitable for use on websites, social media, and marketing materials.")
    

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
