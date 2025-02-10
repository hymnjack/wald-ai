from typing import Dict, Optional, Any, Union
from langchain.tools import BaseTool
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from pydantic import BaseModel, Field, SecretStr
import os
import logging
import time
from functools import wraps
import aiohttp

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Get the API endpoint and key from environment variables
API_ENDPOINT = os.getenv('API_ENDPOINT', 'http://localhost:8080')
API_KEY = os.getenv('SANITIZE_API_KEY')

# Rate limiting configuration
RATE_LIMIT_CALLS = 10
RATE_LIMIT_PERIOD = 60  # in seconds

class RateLimiter:
    def __init__(self, calls: int, period: int):
        self.calls = calls
        self.period = period
        self.timestamps = []

    def __call__(self, func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            now = time.time()
            # Remove timestamps older than the period
            self.timestamps = [t for t in self.timestamps if now - t < self.period]
            
            if len(self.timestamps) >= self.calls:
                sleep_time = self.timestamps[0] + self.period - now
                if sleep_time > 0:
                    logger.warning(f"Rate limit reached. Sleeping for {sleep_time:.2f} seconds")
                    time.sleep(sleep_time)
            
            self.timestamps.append(now)
            return func(*args, **kwargs)
        return wrapper

class HTTPClient:
    def __init__(self):
        self.session = requests.Session()
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504]
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
        
        if not API_KEY:
            logger.warning("API_KEY not set. Authentication will not be possible.")

    def request(self, method: str, url: str, **kwargs) -> requests.Response:
        headers = kwargs.pop('headers', {})
        if API_KEY:
            headers['Authorization'] = f'Bearer {API_KEY}'
        kwargs['headers'] = headers
        
        try:
            response = self.session.request(method, url, **kwargs)
            response.raise_for_status()
            return response
        except requests.exceptions.RequestException as e:
            logger.error(f"Request failed: {str(e)}")
            raise

class SanitizeInput(BaseModel):
    """Input schema for text sanitization."""
    prompt: str = Field(..., description="The text to analyze and sanitize")
    sanitize_engine: Optional[str] = Field(default="GPT4", description="The sanitization engine to use")

class SensitiveInput(BaseModel):
    """Input schema for sensitivity check."""
    prompt: str = Field(..., description="The text to check for sensitivity")

class ImageAnalysisInput(BaseModel):
    """Input schema for image content analysis."""
    prompt: str = Field(..., description="The text to analyze for image content")

class SanitizeResponse(BaseModel):
    """Response schema for sanitization."""
    sanitized_text: str
    confidence_score: Optional[float] = None
    warnings: list[str] = []

class BaseSanitizeTool(BaseTool):
    """Base class for sanitization tools with common functionality."""
    
    def __init__(self):
        super().__init__()
        self.http_client = HTTPClient()

    def _validate_api_key(self):
        """Validate that API key is present."""
        if not API_KEY:
            raise ValueError("API_KEY environment variable must be set")

class SanitizeTool(BaseSanitizeTool):
    name = "sanitize_text"
    description = "Sanitizes text by removing sensitive information and code"
    args_schema = SanitizeInput
    
    @RateLimiter(RATE_LIMIT_CALLS, RATE_LIMIT_PERIOD)
    def _run(self, prompt: str, sanitize_engine: Optional[str] = "GPT4") -> Union[str, Dict[str, Any]]:
        """
        Execute the sanitization.
        
        Args:
            prompt: The text to sanitize
            sanitize_engine: The engine to use for sanitization
            
        Returns:
            Union[str, Dict[str, Any]]: The sanitized text or detailed response
        
        Raises:
            RuntimeError: If the service request fails
            ValueError: If the API key is not set
        """
        self._validate_api_key()
        
        try:
            response = self.http_client.request(
                'POST',
                f"{API_ENDPOINT}/sanitize-prompt",
                json={"text": prompt, "engine": sanitize_engine}
            )
            return response.json()
        except Exception as e:
            logger.error(f"Sanitization failed: {str(e)}")
            raise RuntimeError(f"Sanitization failed: {str(e)}")

    async def _arun(self, prompt: str, sanitize_engine: Optional[str] = "GPT4") -> Dict[str, Any]:
        """
        Async execution of sanitization.
        
        This method provides an asynchronous interface to the sanitization service.
        """
        
        self._validate_api_key()
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{API_ENDPOINT}/sanitize-prompt",
                json={"text": prompt, "engine": sanitize_engine},
                headers={"Authorization": f"Bearer {API_KEY}"}
            ) as response:
                if response.status != 200:
                    raise RuntimeError(f"Service request failed with status {response.status}")
                return await response.json()

class SensitivityCheckTool(BaseSanitizeTool):
    name = "check_sensitivity"
    description = "Checks if text contains sensitive information"
    args_schema = SensitiveInput

    @RateLimiter(RATE_LIMIT_CALLS, RATE_LIMIT_PERIOD)
    def _run(self, prompt: str) -> Dict[str, Any]:
        """Execute the sensitivity check."""
        self._validate_api_key()
        
        try:
            response = self.http_client.request(
                'POST',
                f"{API_ENDPOINT}/is-sensitive",
                json={"prompt": prompt}
            )
            return response.json()
        except Exception as e:
            logger.error(f"Sensitivity check failed: {str(e)}")
            raise RuntimeError(f"Sensitivity check failed: {str(e)}")

    async def _arun(self, prompt: str) -> Dict[str, Any]:
        """Async execution of sensitivity check."""
        
        self._validate_api_key()
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{API_ENDPOINT}/is-sensitive",
                json={"prompt": prompt},
                headers={"Authorization": f"Bearer {API_KEY}"}
            ) as response:
                if response.status != 200:
                    raise RuntimeError(f"Service request failed with status {response.status}")
                return await response.json()

class ImageAnalysisTool(BaseSanitizeTool):
    name = "analyze_image_content"
    description = "Analyzes text for image-related content"
    args_schema = ImageAnalysisInput

    @RateLimiter(RATE_LIMIT_CALLS, RATE_LIMIT_PERIOD)
    def _run(self, prompt: str) -> Dict[str, Any]:
        """Execute the image analysis."""
        self._validate_api_key()
        
        try:
            response = self.http_client.request(
                'POST',
                f"{API_ENDPOINT}/is-image",
                json={"prompt": prompt}
            )
            return response.json()
        except Exception as e:
            logger.error(f"Image analysis failed: {str(e)}")
            raise RuntimeError(f"Image analysis failed: {str(e)}")

    async def _arun(self, prompt: str) -> Dict[str, Any]:
        """Async execution of image analysis."""
        
        self._validate_api_key()
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{API_ENDPOINT}/is-image",
                json={"prompt": prompt},
                headers={"Authorization": f"Bearer {API_KEY}"}
            ) as response:
                if response.status != 200:
                    raise RuntimeError(f"Service request failed with status {response.status}")
                return await response.json()
