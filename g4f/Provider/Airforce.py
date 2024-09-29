from __future__ import annotations

from aiohttp import ClientSession, ClientResponseError
import json
from ..typing import AsyncResult, Messages
from .base_provider import AsyncGeneratorProvider, ProviderModelMixin
from ..image import ImageResponse
from .helper import format_prompt
from ..errors import ResponseStatusError

class Airforce(AsyncGeneratorProvider, ProviderModelMixin):
    url = "https://api.airforce"
    text_api_endpoint = "https://api.airforce/chat/completions"
    image_api_endpoint = "https://api.airforce/imagine2"
    working = True
    supports_gpt_35_turbo = True
    supports_gpt_4 = True
    supports_stream = True
    supports_system_message = True
    supports_message_history = True
    default_model = 'llama-3-70b-chat'
    text_models = [
        # Open source models
        'llama-2-13b-chat',
        'llama-3-70b-chat',
        'llama-3-70b-chat-turbo',
        'llama-3-70b-chat-lite',
        'llama-3-8b-chat',
        'llama-3-8b-chat-turbo',
        'llama-3-8b-chat-lite',
        'llama-3.1-405b-turbo',
        'llama-3.1-70b-turbo',
        'llama-3.1-8b-turbo',
        'LlamaGuard-2-8b',
        'Llama-Guard-7b',
        'Meta-Llama-Guard-3-8B',
        'Mixtral-8x7B-Instruct-v0.1',
        'Mixtral-8x22B-Instruct-v0.1',
        'Mistral-7B-Instruct-v0.1',
        'Mistral-7B-Instruct-v0.2',
        'Mistral-7B-Instruct-v0.3',
        'Qwen1.5-72B-Chat',
        'Qwen1.5-110B-Chat',
        'Qwen2-72B-Instruct',
        'gemma-2b-it',
        'gemma-2-9b-it',
        'gemma-2-27b-it',
        'dbrx-instruct',
        'deepseek-llm-67b-chat',
        'Nous-Hermes-2-Mixtral-8x7B-DPO',
        'Nous-Hermes-2-Yi-34B',
        'WizardLM-2-8x22B',
        'SOLAR-10.7B-Instruct-v1.0',
        'StripedHyena-Nous-7B',      
        'sparkdesk',
        
        # Other models
        'chatgpt-4o-latest',
        'gpt-4',
        'gpt-4-turbo',
        'gpt-4o-mini-2024-07-18',
        'gpt-4o-mini',
        'gpt-4o',
        'gpt-3.5-turbo',
        'gpt-3.5-turbo-0125',
        'gpt-3.5-turbo-1106',
        'gpt-3.5-turbo-16k',
        'gpt-3.5-turbo-0613',
        'gpt-3.5-turbo-16k-0613',
        'gemini-1.5-flash',
        'gemini-1.5-pro',
    ]
    
    image_models = [
        'flux',
        'flux-realism',
        'flux-anime',
        'flux-3d',
        'flux-disney',
        'flux-pixel',
        'flux-4o',
        'any-dark',
        'dall-e-3',
    ]
    
    models = [
        *text_models,
        *image_models
    ]
    model_aliases = {
        # Open source models
        "llama-2-13b": "llama-2-13b-chat",
        "llama-3-70b": "llama-3-70b-chat",
        "llama-3-70b": "llama-3-70b-chat-turbo",
        "llama-3-70b": "llama-3-70b-chat-lite",
        "llama-3-8b": "llama-3-8b-chat",
        "llama-3-8b": "llama-3-8b-chat-turbo",
        "llama-3-8b": "llama-3-8b-chat-lite",
        "llama-3.1-405b": "llama-3.1-405b-turbo",
        "llama-3.1-70b": "llama-3.1-70b-turbo",
        "llama-3.1-8b": "llama-3.1-8b-turbo",
        "mixtral-8x7b": "Mixtral-8x7B-Instruct-v0.1",
        "mixtral-8x22b": "Mixtral-8x22B-Instruct-v0.1",
        "mistral-7b": "Mistral-7B-Instruct-v0.1",
        "mistral-7b": "Mistral-7B-Instruct-v0.2",
        "mistral-7b": "Mistral-7B-Instruct-v0.3",
        "mixtral-8x7b-dpo": "Nous-Hermes-2-Mixtral-8x7B-DPO",
        "qwen-1.5-72b": "Qwen1.5-72B-Chat",
        "qwen-1.5-110b": "Qwen1.5-110B-Chat",
        "qwen-2-72b": "Qwen2-72B-Instruct",
        "gemma-2b": "gemma-2b-it",
        "gemma-2b-9b": "gemma-2-9b-it",
        "gemma-2b-27b": "gemma-2-27b-it",
        "deepseek": "deepseek-llm-67b-chat",
        "yi-34b": "Nous-Hermes-2-Yi-34B",
        "wizardlm-2-8x22b": "WizardLM-2-8x22B",
        "solar-10-7b": "SOLAR-10.7B-Instruct-v1.0",
        "sh-n-7b": "StripedHyena-Nous-7B",
        "sparkdesk-v1.1": "sparkdesk",
        
        # Other models
        "gpt-4o": "chatgpt-4o-latest",
        "gpt-4o-mini": "gpt-4o-mini-2024-07-18",
        "gpt-3.5-turbo": "gpt-3.5-turbo-0125",
        "gpt-3.5-turbo": "gpt-3.5-turbo-1106",
        "gpt-3.5-turbo": "gpt-3.5-turbo-16k",
        "gpt-3.5-turbo": "gpt-3.5-turbo-0613",
        "gpt-3.5-turbo": "gpt-3.5-turbo-16k-0613",
        "gemini-flash": "gemini-1.5-flash",
        "gemini-pro": "gemini-1.5-pro",
        
        # Image models
        "dalle-3": "dall-e-3",
    }

    @classmethod
    async def create_async_generator(
        cls,
        model: str,
        messages: Messages,
        proxy: str = None,
        **kwargs
    ) -> AsyncResult:
        model = cls.get_model(model)
        
        headers = {
            "accept": "*/*",
            "accept-language": "en-US,en;q=0.9",
            "content-type": "application/json",
            "origin": "https://api.airforce",
            "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36",
            "authorization": "Bearer null",
            "cache-control": "no-cache",
            "pragma": "no-cache",
            "priority": "u=1, i",
            "referer": "https://llmplayground.net/",
            "sec-ch-ua": '"Not;A=Brand";v="24", "Chromium";v="128"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": '"Linux"',
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "cross-site",
        }

        if model in cls.image_models:
            async for item in cls.generate_image(model, messages, headers, proxy, **kwargs):
                yield item
        else:
            async for item in cls.generate_text(model, messages, headers, proxy, **kwargs):
                yield item

    @classmethod
    async def generate_text(cls, model: str, messages: Messages, headers: dict, proxy: str, **kwargs) -> AsyncResult:
        async with ClientSession() as session:
            data = {
                "messages": [{"role": "user", "content": message['content']} for message in messages],
                "model": model,
                "max_tokens": kwargs.get('max_tokens', 4096),
                "temperature": kwargs.get('temperature', 1),
                "top_p": kwargs.get('top_p', 1),
                "stream": True
            }

            try:
                async with session.post(cls.text_api_endpoint, json=data, headers=headers, proxy=proxy) as response:
                    response.raise_for_status()
                    async for line in response.content:
                        if line:
                            line = line.decode('utf-8').strip()
                            if line.startswith("data: "):
                                if line == "data: [DONE]":
                                    break
                                try:
                                    data = json.loads(line[6:])
                                    if 'choices' in data and len(data['choices']) > 0:
                                        delta = data['choices'][0].get('delta', {})
                                        if 'content' in delta:
                                            content = delta['content']
                                            if "One message exceeds the 1000chars per message limit" in content:
                                                raise ResponseStatusError(
                                                    "Message too long",
                                                    400,
                                                    "Please try a shorter message."
                                                )
                                            yield content
                                except json.JSONDecodeError:
                                    continue
            except ResponseStatusError as e:
                raise e
            except Exception as e:
                raise ResponseStatusError(str(e), 500, "An unexpected error occurred")

    @classmethod
    async def generate_image(cls, model: str, messages: Messages, headers: dict, proxy: str, **kwargs) -> AsyncResult:
        prompt = messages[-1]['content'] if messages else ""
        params = {
            "prompt": prompt,
            "size": kwargs.get("size", "1:1"),
            "seed": kwargs.get("seed"),
            "model": model
        }
        params = {k: v for k, v in params.items() if v is not None}

        try:
            async with ClientSession(headers=headers) as session:
                async with session.get(cls.image_api_endpoint, params=params, proxy=proxy) as response:
                    response.raise_for_status()
                    content = await response.read()
                    
                    if response.content_type.startswith('image/'):
                        image_url = str(response.url)
                        yield ImageResponse(image_url, prompt)
                    else:
                        try:
                            text = content.decode('utf-8', errors='ignore')
                            raise ResponseStatusError("Image generation failed", response.status, text)
                        except Exception as decode_error:
                            raise ResponseStatusError("Decoding error", 500, str(decode_error))
        except ClientResponseError as e:
            raise ResponseStatusError(f"HTTP {e.status}", e.status, e.message)
        except Exception as e:
            raise ResponseStatusError("Unexpected error", 500, str(e))