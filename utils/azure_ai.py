"""
Azure OpenAI integration for calendar event extraction from images.
Uses GPT-4 Vision model with managed identity for secure authentication.
"""

import os
import json
import logging
import base64
from typing import Dict, List, Optional, Union
from PIL import Image
import io
import streamlit as st
from openai import AzureOpenAI
from azure.identity import DefaultAzureCredential, ManagedIdentityCredential
from azure.core.exceptions import HttpResponseError, ClientAuthenticationError

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AzureOpenAICalendarExtractor:
    """
    Azure OpenAI-powered calendar event extractor from images using GPT-4 Vision.
    Supports both key-based and managed identity authentication.
    """
    
    def __init__(self):
        """Initialize the Azure OpenAI client with secure authentication."""
        self.client = None
        self.endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
        self.api_key = os.getenv("AZURE_OPENAI_API_KEY")
        self.api_version = os.getenv("AZURE_OPENAI_API_VERSION", "2024-02-01")
        self.deployment_name = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME", "gpt-4o")
        
        # Initialize client with appropriate authentication
        self._initialize_client()
    
    def _initialize_client(self) -> None:
        """
        Initialize Azure OpenAI client with secure authentication.
        Prefers managed identity in production, falls back to key-based auth.
        """
        if not self.endpoint:
            logger.error("AZURE_OPENAI_ENDPOINT environment variable not set")
            return
        
        try:
            # Try managed identity first (production best practice)
            if not self.api_key:
                logger.info("Using managed identity authentication for Azure OpenAI")
                # For managed identity, we'll use the token credential
                credential = DefaultAzureCredential()
                token = credential.get_token("https://cognitiveservices.azure.com/.default")
                
                self.client = AzureOpenAI(
                    azure_endpoint=self.endpoint,
                    api_version=self.api_version,
                    azure_ad_token=token.token
                )
            else:
                # Fall back to key-based authentication (development)
                logger.info("Using key-based authentication for Azure OpenAI")
                self.client = AzureOpenAI(
                    azure_endpoint=self.endpoint,
                    api_key=self.api_key,
                    api_version=self.api_version
                )
                
            logger.info("Azure OpenAI client initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize Azure OpenAI client: {str(e)}")
            self.client = None
    
    def is_configured(self) -> bool:
        """Check if the Azure OpenAI service is properly configured."""
        return self.client is not None and self.endpoint is not None
    
    def _encode_image_to_base64(self, image: Union[Image.Image, bytes]) -> str:
        """
        Convert image to base64 string for API submission.
        
        Args:
            image: PIL Image object or image bytes
            
        Returns:
            Base64 encoded image string
        """
        if isinstance(image, Image.Image):
            # Convert PIL Image to bytes
            img_buffer = io.BytesIO()
            # Convert to RGB if necessary (remove alpha channel)
            if image.mode in ('RGBA', 'LA'):
                background = Image.new('RGB', image.size, (255, 255, 255))
                background.paste(image, mask=image.split()[-1] if image.mode == 'RGBA' else None)
                image = background
            image.save(img_buffer, format='JPEG', quality=85)
            image_bytes = img_buffer.getvalue()
        else:
            image_bytes = image
        
        return base64.b64encode(image_bytes).decode('utf-8')
    
    def extract_calendar_events_from_image(self, image: Union[Image.Image, bytes]) -> List[Dict[str, str]]:
        """
        Extract calendar events from an image using Azure OpenAI GPT-4 Vision.
        
        Args:
            image: PIL Image object or image bytes
            
        Returns:
            List of parsed calendar event dictionaries
        """
        if not self.is_configured():
            logger.error("Azure OpenAI client not configured")
            return []
        
        try:
            # Encode image to base64
            base64_image = self._encode_image_to_base64(image)
            
            # Create the prompt for calendar event extraction
            system_prompt = """You are an AI assistant specialized in extracting calendar events from images. 
            Analyze the provided image and extract any calendar events, meetings, appointments, or scheduled activities you can identify.
            
            For each event you find, extract the following information:
            - title: The name or description of the event
            - date: The date in a readable format (e.g., "2025-06-08", "June 8, 2025", "Monday, June 8")
            - time: The time if specified (e.g., "2:00 PM", "14:00", "2:00-3:00 PM")
            - location: The location or venue if mentioned
            - description: Any additional details about the event
            
            Return your response as a JSON array of objects. Each object should have the keys: title, date, time, location, description.
            If any field is not available, use an empty string for that field.
            
            Example response format:
            [
                {
                    "title": "Team Meeting",
                    "date": "2025-06-08",
                    "time": "2:00 PM",
                    "location": "Conference Room A",
                    "description": "Weekly team sync"
                },
                {
                    "title": "Doctor Appointment",
                    "date": "June 10, 2025",
                    "time": "10:30 AM",
                    "location": "Medical Center",
                    "description": "Annual checkup"
                }
            ]
            
            If no calendar events are found in the image, return an empty array: []"""
            
            user_prompt = "Please analyze this image and extract any calendar events, appointments, or scheduled activities you can find. Return the results as a JSON array."
            
            # Make the API call
            response = self.client.chat.completions.create(
                model=self.deployment_name,
                messages=[
                    {
                        "role": "system",
                        "content": system_prompt
                    },
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": user_prompt
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{base64_image}",
                                    "detail": "high"
                                }
                            }
                        ]
                    }
                ],
                max_tokens=2000,
                temperature=0.1  # Low temperature for consistent, factual extraction
            )
            
            # Parse the response
            response_text = response.choices[0].message.content.strip()
            logger.info(f"Received response from Azure OpenAI: {len(response_text)} characters")
            
            # Store the raw response for debugging
            self._last_response = response_text
            
            # Try to parse as JSON
            try:
                # Clean up the response if it has markdown formatting
                if response_text.startswith("```json"):
                    response_text = response_text.replace("```json", "").replace("```", "").strip()
                elif response_text.startswith("```"):
                    response_text = response_text.replace("```", "").strip()
                
                events = json.loads(response_text)
                
                # Validate that it's a list
                if not isinstance(events, list):
                    logger.warning("Response is not a list, trying to extract from object")
                    return []
                
                # Clean up and validate events
                cleaned_events = []
                for event in events:
                    if isinstance(event, dict) and event.get("title"):
                        cleaned_event = {
                            "title": str(event.get("title", ""))[:100],  # Limit title length
                            "date": str(event.get("date", "")),
                            "time": str(event.get("time", "")),
                            "location": str(event.get("location", "")),
                            "description": str(event.get("description", ""))[:500]  # Limit description length
                        }
                        cleaned_events.append(cleaned_event)
                
                logger.info(f"Successfully extracted {len(cleaned_events)} calendar events from image")
                return cleaned_events
                
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse JSON response: {str(e)}")
                logger.error(f"Raw response: {response_text}")
                return []
            
        except Exception as e:
            logger.error(f"Error in calendar event extraction: {str(e)}")
            return []
    
    def get_last_response(self) -> str:
        """Get the last raw response from the API for debugging."""
        return getattr(self, '_last_response', '')


@st.cache_resource
def get_azure_openai_extractor() -> AzureOpenAICalendarExtractor:
    """Get cached Azure OpenAI extractor instance."""
    return AzureOpenAICalendarExtractor()


def validate_azure_openai_configuration() -> Dict[str, Union[bool, str]]:
    """
    Validate Azure OpenAI configuration and return status information.
    
    Returns:
        Dictionary with configuration status and messages
    """
    endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
    api_key = os.getenv("AZURE_OPENAI_API_KEY")
    deployment = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME", "gpt-4o")
    
    status = {
        "configured": False,
        "has_endpoint": bool(endpoint),
        "has_api_key": bool(api_key),
        "deployment_name": deployment,
        "auth_method": "none",
        "message": ""
    }
    
    if not endpoint:
        status["message"] = "❌ AZURE_OPENAI_ENDPOINT not configured"
        return status
    
    if api_key:
        status["auth_method"] = "api_key"
        status["configured"] = True
        status["message"] = "✅ Configured with API key authentication"
    else:
        status["auth_method"] = "managed_identity"
        status["configured"] = True
        status["message"] = "✅ Configured with managed identity authentication"
    
    return status
