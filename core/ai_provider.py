import base64
import io
import json
import urllib.error
import urllib.request
from typing import Any

from PIL import Image

import config


PROVIDER_ORDER = ("gemini", "openai", "anthropic", "openrouter", "ollama")
TEXT_ONLY_PROVIDERS = set()


def _split_models(value: str) -> list[str]:
    return [model.strip() for model in value.split(",") if model.strip()]


def _provider_has_config(provider: str) -> bool:
    if provider == "gemini":
        return bool(config.GEMINI_API_KEY)
    if provider == "openai":
        return bool(config.OPENAI_API_KEY)
    if provider == "anthropic":
        return bool(config.ANTHROPIC_API_KEY)
    if provider == "openrouter":
        return bool(config.OPENROUTER_API_KEY)
    if provider == "ollama":
        return bool(config.OLLAMA_MODEL)
    return False


def get_active_provider() -> str | None:
    """Return the configured provider, or the first available provider in auto mode."""
    requested = config.AI_PROVIDER or "auto"
    if requested != "auto":
        return requested if _provider_has_config(requested) else None

    for provider in PROVIDER_ORDER:
        if _provider_has_config(provider):
            return provider

    return None


def is_ai_configured() -> bool:
    return get_active_provider() is not None


def is_vision_configured() -> bool:
    provider = get_active_provider()
    return provider is not None and provider not in TEXT_ONLY_PROVIDERS


def describe_ai_status() -> str:
    provider = get_active_provider()
    if provider:
        return f"{provider} provider is configured."

    requested = config.AI_PROVIDER or "auto"
    if requested == "auto":
        return "No AI provider is configured. Add at least one provider API key or set OLLAMA_MODEL."

    return f"AI_PROVIDER is set to {requested}, but its required key or model is missing."


def _http_json(url: str, headers: dict[str, str], payload: dict[str, Any]) -> dict[str, Any]:
    body = json.dumps(payload).encode("utf-8")
    request = urllib.request.Request(url, data=body, headers=headers, method="POST")

    try:
        with urllib.request.urlopen(request, timeout=90) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"HTTP {exc.code}: {detail}") from exc
    except urllib.error.URLError as exc:
        raise RuntimeError(str(exc.reason)) from exc


def _image_to_data_url(image: Image.Image) -> str:
    buffer = io.BytesIO()
    image.save(buffer, format="PNG")
    encoded = base64.b64encode(buffer.getvalue()).decode("ascii")
    return f"data:image/png;base64,{encoded}"


def _image_to_base64(image: Image.Image) -> str:
    buffer = io.BytesIO()
    image.save(buffer, format="PNG")
    return base64.b64encode(buffer.getvalue()).decode("ascii")


def _extract_openai_text(data: dict[str, Any]) -> str:
    output_text = data.get("output_text")
    if isinstance(output_text, str) and output_text.strip():
        return output_text.strip()

    for item in data.get("output", []):
        if item.get("type") != "message":
            continue
        for content in item.get("content", []):
            if content.get("type") in {"output_text", "text"}:
                text = content.get("text", "")
                if text:
                    return text.strip()

    raise RuntimeError("OpenAI response did not include output text.")


def _extract_chat_completion_text(data: dict[str, Any]) -> str:
    choices = data.get("choices", [])
    if not choices:
        raise RuntimeError("Chat completion response did not include choices.")

    content = choices[0].get("message", {}).get("content", "")
    if isinstance(content, str):
        return content.strip()

    if isinstance(content, list):
        parts = []
        for item in content:
            if isinstance(item, dict) and item.get("type") in {"text", "output_text"}:
                parts.append(item.get("text", ""))
        text = "\n".join(part for part in parts if part)
        if text:
            return text.strip()

    raise RuntimeError("Chat completion response did not include text content.")


def _extract_anthropic_text(data: dict[str, Any]) -> str:
    parts = []
    for item in data.get("content", []):
        if item.get("type") == "text" and item.get("text"):
            parts.append(item["text"])
    if parts:
        return "\n".join(parts).strip()

    raise RuntimeError("Anthropic response did not include text content.")


def _gemini_text(prompt: str, system_prompt: str, models: list[str]) -> str:
    from google import genai

    client = genai.Client(api_key=config.GEMINI_API_KEY)
    last_error = None

    for model_name in models:
        try:
            response = client.models.generate_content(
                model=model_name,
                contents=prompt,
                config=genai.types.GenerateContentConfig(
                    system_instruction=system_prompt,
                ),
            )
            if response.text:
                return response.text.strip()
        except Exception as exc:
            last_error = exc
            print(f"[AI:gemini] {model_name} failed: {exc}")

    raise RuntimeError(f"Gemini failed for all configured models: {last_error}")


def _gemini_vision(prompt: str, image: Image.Image, system_prompt: str, models: list[str]) -> str:
    from google import genai

    client = genai.Client(api_key=config.GEMINI_API_KEY)
    last_error = None

    for model_name in models:
        try:
            response = client.models.generate_content(
                model=model_name,
                contents=[image, prompt],
                config=genai.types.GenerateContentConfig(
                    system_instruction=system_prompt,
                ),
            )
            if response.text:
                return response.text.strip()
        except Exception as exc:
            last_error = exc
            print(f"[AI:gemini] {model_name} vision failed: {exc}")

    raise RuntimeError(f"Gemini vision failed for all configured models: {last_error}")


def _openai_text(prompt: str, system_prompt: str, model: str) -> str:
    data = _http_json(
        "https://api.openai.com/v1/responses",
        {
            "Authorization": f"Bearer {config.OPENAI_API_KEY}",
            "Content-Type": "application/json",
        },
        {
            "model": model,
            "instructions": system_prompt,
            "input": prompt,
        },
    )
    return _extract_openai_text(data)


def _openai_vision(prompt: str, image: Image.Image, system_prompt: str, model: str) -> str:
    data = _http_json(
        "https://api.openai.com/v1/responses",
        {
            "Authorization": f"Bearer {config.OPENAI_API_KEY}",
            "Content-Type": "application/json",
        },
        {
            "model": model,
            "instructions": system_prompt,
            "input": [
                {
                    "role": "user",
                    "content": [
                        {"type": "input_text", "text": prompt},
                        {"type": "input_image", "image_url": _image_to_data_url(image), "detail": "auto"},
                    ],
                }
            ],
        },
    )
    return _extract_openai_text(data)


def _anthropic_text(prompt: str, system_prompt: str, model: str) -> str:
    data = _http_json(
        "https://api.anthropic.com/v1/messages",
        {
            "x-api-key": config.ANTHROPIC_API_KEY,
            "anthropic-version": "2023-06-01",
            "Content-Type": "application/json",
        },
        {
            "model": model,
            "max_tokens": 1024,
            "system": system_prompt,
            "messages": [{"role": "user", "content": prompt}],
        },
    )
    return _extract_anthropic_text(data)


def _anthropic_vision(prompt: str, image: Image.Image, system_prompt: str, model: str) -> str:
    data = _http_json(
        "https://api.anthropic.com/v1/messages",
        {
            "x-api-key": config.ANTHROPIC_API_KEY,
            "anthropic-version": "2023-06-01",
            "Content-Type": "application/json",
        },
        {
            "model": model,
            "max_tokens": 1024,
            "system": system_prompt,
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image",
                            "source": {
                                "type": "base64",
                                "media_type": "image/png",
                                "data": _image_to_base64(image),
                            },
                        },
                        {"type": "text", "text": prompt},
                    ],
                }
            ],
        },
    )
    return _extract_anthropic_text(data)


def _openrouter_text(prompt: str, system_prompt: str, model: str) -> str:
    data = _http_json(
        "https://openrouter.ai/api/v1/chat/completions",
        {
            "Authorization": f"Bearer {config.OPENROUTER_API_KEY}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://github.com/AbuBakar223200/Friday",
            "X-Title": "Friday Voice Assistant",
        },
        {
            "model": model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt},
            ],
        },
    )
    return _extract_chat_completion_text(data)


def _openrouter_vision(prompt: str, image: Image.Image, system_prompt: str, model: str) -> str:
    data = _http_json(
        "https://openrouter.ai/api/v1/chat/completions",
        {
            "Authorization": f"Bearer {config.OPENROUTER_API_KEY}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://github.com/AbuBakar223200/Friday",
            "X-Title": "Friday Voice Assistant",
        },
        {
            "model": model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {"type": "image_url", "image_url": {"url": _image_to_data_url(image)}},
                    ],
                },
            ],
        },
    )
    return _extract_chat_completion_text(data)


def _ollama_text(prompt: str, system_prompt: str, model: str) -> str:
    data = _http_json(
        f"{config.OLLAMA_BASE_URL}/api/generate",
        {"Content-Type": "application/json"},
        {
            "model": model,
            "prompt": f"{system_prompt}\n\nUser: {prompt}",
            "stream": False,
        },
    )
    text = data.get("response", "")
    if not text:
        raise RuntimeError("Ollama response did not include text.")
    return text.strip()


def _ollama_vision(prompt: str, image: Image.Image, system_prompt: str, model: str) -> str:
    data = _http_json(
        f"{config.OLLAMA_BASE_URL}/api/generate",
        {"Content-Type": "application/json"},
        {
            "model": model,
            "prompt": f"{system_prompt}\n\nUser: {prompt}",
            "images": [_image_to_base64(image)],
            "stream": False,
        },
    )
    text = data.get("response", "")
    if not text:
        raise RuntimeError("Ollama response did not include text.")
    return text.strip()


def generate_text(prompt: str, system_prompt: str) -> str:
    provider = get_active_provider()
    if provider is None:
        return "I'm sorry, my AI brain is not configured. Add an API key in .env or set up Ollama."

    print(f"[AI] Using {provider} for text.")
    try:
        if provider == "gemini":
            return _gemini_text(prompt, system_prompt, _split_models(config.GEMINI_TEXT_MODELS))
        if provider == "openai":
            return _openai_text(prompt, system_prompt, config.OPENAI_TEXT_MODEL)
        if provider == "anthropic":
            return _anthropic_text(prompt, system_prompt, config.ANTHROPIC_TEXT_MODEL)
        if provider == "openrouter":
            return _openrouter_text(prompt, system_prompt, config.OPENROUTER_TEXT_MODEL)
        if provider == "ollama":
            return _ollama_text(prompt, system_prompt, config.OLLAMA_MODEL)
    except Exception as exc:
        print(f"[AI:{provider}] text failed: {exc}")

    return "I encountered an error while thinking. Please check the configured AI provider and try again."


def generate_vision(prompt: str, image: Image.Image, system_prompt: str) -> str:
    provider = get_active_provider()
    if provider is None:
        return "My vision systems are not configured. Add an API key in .env or set up Ollama."

    print(f"[AI] Using {provider} for vision.")
    try:
        if provider == "gemini":
            return _gemini_vision(prompt, image, system_prompt, _split_models(config.GEMINI_VISION_MODELS))
        if provider == "openai":
            return _openai_vision(prompt, image, system_prompt, config.OPENAI_VISION_MODEL)
        if provider == "anthropic":
            return _anthropic_vision(prompt, image, system_prompt, config.ANTHROPIC_VISION_MODEL)
        if provider == "openrouter":
            return _openrouter_vision(prompt, image, system_prompt, config.OPENROUTER_VISION_MODEL)
        if provider == "ollama":
            return _ollama_vision(prompt, image, system_prompt, config.OLLAMA_MODEL)
    except Exception as exc:
        print(f"[AI:{provider}] vision failed: {exc}")

    return "I encountered an error while trying to process the image on your screen."
