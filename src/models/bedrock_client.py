"""
BedrockClient module for interacting with Amazon Bedrock models.
"""

import json
import boto3
import os
import time
import random
from boto3.session import Session
from pathlib import Path
from dotenv import load_dotenv

class BedrockClient:
    """
    Client for interacting with Amazon Bedrock models.
    Handles authentication, model invocation, and response parsing.
    """
    
    def __init__(self, model_id, region_name=None):
        """
        Initialize the Bedrock client.
        
        Args:
            model_id (str): The Bedrock model ID to use
            region_name (str, optional): AWS region name. Defaults to environment variable or 'us-east-1'.
        """
        # Load environment variables if not already loaded
        load_dotenv()
        
        # Set region
        self.region_name = region_name or os.getenv("AWS_REGION", "us-east-1")
        
        # Set model ID
        self.model_id = model_id
        
        # Create a boto3 session using the shared credentials file
        session = Session(region_name=self.region_name)
        
        # Initialize Bedrock client with the session
        self.bedrock_runtime = session.client(
            service_name="bedrock-runtime"
        )
        
        # Store model provider for provider-specific formatting
        if "anthropic" in self.model_id:
            self.provider = "anthropic"
        elif "meta" in self.model_id:
            self.provider = "meta"
        elif "mistral" in self.model_id:
            self.provider = "mistral"
        elif "amazon" in self.model_id:
            self.provider = "amazon"
        else:
            # Default fallback
            self.provider = self.model_id.split(".")[0]
    
    def invoke(self, prompt, system_prompt=None, max_tokens=4096, temperature=0.7):
        """
        Invoke the model with the given prompt.
        
        Args:
            prompt (str): The prompt to send to the model
            system_prompt (str, optional): System prompt for models that support it
            max_tokens (int, optional): Maximum number of tokens to generate
            temperature (float, optional): Temperature for sampling
            
        Returns:
            str: The model's response text
        """
        # Format request body based on provider
        request_body = self._format_request(prompt, system_prompt, max_tokens, temperature)
        
        # Retry parameters
        max_retries = 5
        retry_count = 0
        base_delay = 1  # Start with 1 second delay
        
        while retry_count < max_retries:
            try:
                # Invoke model
                response = self.bedrock_runtime.invoke_model(
                    modelId=self.model_id,
                    body=json.dumps(request_body)
                )
                
                # Parse response based on provider
                return self._parse_response(response)
                
            except self.bedrock_runtime.exceptions.ThrottlingException as e:
                retry_count += 1
                if retry_count >= max_retries:
                    print(f"Maximum retries ({max_retries}) exceeded. Giving up.")
                    raise e
                
                # Calculate exponential backoff with jitter
                delay = base_delay * (2 ** (retry_count - 1)) + (0.1 * random.random())
                print(f"Throttling detected. Retrying in {delay:.2f} seconds... (Attempt {retry_count}/{max_retries})")
                time.sleep(delay)
            
            except Exception as e:
                # For other exceptions, don't retry
                raise e
    
    def _format_request(self, prompt, system_prompt, max_tokens, temperature):
        """
        Format the request body based on the model provider.
        
        Args:
            prompt (str): The prompt to send to the model
            system_prompt (str, optional): System prompt for models that support it
            max_tokens (int): Maximum number of tokens to generate
            temperature (float): Temperature for sampling
            
        Returns:
            dict: Formatted request body
        """
        if self.provider == "anthropic":
            # Claude format
            request = {
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": max_tokens,
                "temperature": temperature,
                "messages": [
                    {"role": "user", "content": prompt}
                ]
            }
            
            if system_prompt:
                request["system"] = system_prompt
                
            return request
            
        elif self.provider == "amazon":
            # Amazon Nova format
            if system_prompt:
                # For Nova, prepend system prompt to the user message
                full_prompt = f"{system_prompt}\n\n{prompt}"
                request = {
                    "messages": [
                        {"role": "user", "content": [{"text": full_prompt}]}
                    ]
                }
            else:
                request = {
                    "messages": [
                        {"role": "user", "content": [{"text": prompt}]}
                    ]
                }
                
            return request
            
        elif self.provider == "meta":
            # Llama format
            # For Llama models, prepend system prompt to the user prompt instead of using system_prompt parameter
            if system_prompt:
                full_prompt = f"{system_prompt}\n\n{prompt}"
            else:
                full_prompt = prompt
                
            request = {
                "prompt": full_prompt,
                "max_gen_len": max_tokens,
                "temperature": temperature
            }
            
            return request
            
        elif self.provider == "mistral":
            # Mistral format
            # For Mistral models, prepend system prompt to the user prompt instead of using system parameter
            if system_prompt:
                full_prompt = f"{system_prompt}\n\n{prompt}"
            else:
                full_prompt = prompt
                
            request = {
                "prompt": full_prompt,
                "max_tokens": max_tokens,
                "temperature": temperature
            }
                
            return request
            
        elif self.provider == "deepseek":
            # DeepSeek format
            request = {
                "prompt": prompt,
                "max_tokens": max_tokens,
                "temperature": temperature
            }
            
            if system_prompt:
                # DeepSeek might use a different format for system prompts
                full_prompt = f"{system_prompt}\n\n{prompt}"
                request["prompt"] = full_prompt
                
            return request
            
        elif self.provider == "ai21":
            # AI21 (Jamba) format
            request = {
                "prompt": prompt,
                "maxTokens": max_tokens,
                "temperature": temperature
            }
            
            if system_prompt:
                # AI21 might use a different format for system prompts
                full_prompt = f"{system_prompt}\n\n{prompt}"
                request["prompt"] = full_prompt
                
            return request
            
        else:
            # Generic format as fallback
            return {
                "prompt": prompt,
                "max_tokens": max_tokens,
                "temperature": temperature
            }
    
    def _parse_response(self, response):
        """
        Parse the response from the model based on the provider.
        
        Args:
            response: The raw response from the Bedrock invoke_model call
            
        Returns:
            str: The extracted text response
        """
        # Parse response body
        response_body = json.loads(response.get("body").read())
        
        if self.provider == "anthropic":
            # Claude response format
            return response_body.get("content", [{}])[0].get("text", "")
            
        elif self.provider == "amazon":
            # Amazon Nova response format
            if "output" in response_body:
                # Extract text from the output array
                output = response_body.get("output", {})
                if "message" in output:
                    message = output.get("message", {})
                    if "content" in message:
                        content = message.get("content", [])
                        for item in content:
                            if "text" in item:
                                return item.get("text", "")
                return str(output)  # Fallback if we can't extract the text
            else:
                return response_body.get("completion", "")
            
        elif self.provider == "meta":
            # Llama response format
            return response_body.get("generation", "")
            
        elif self.provider == "mistral":
            # Mistral response format
            return response_body.get("outputs", [{}])[0].get("text", "")
            
        elif self.provider == "deepseek":
            # DeepSeek response format
            return response_body.get("generation", "")
            
        elif self.provider == "ai21":
            # AI21 (Jamba) response format
            return response_body.get("completions", [{}])[0].get("data", {}).get("text", "")
            
        else:
            # Generic fallback - try common response formats
            if "generation" in response_body:
                return response_body["generation"]
            elif "text" in response_body:
                # Return the whole response body as a string if we can't extract the text
                return str(response_body)
