# AI Providers

Friday can use different AI providers through `.env` settings. The default mode is:

```text
AI_PROVIDER=auto
```

In auto mode, Friday uses the first configured provider in this order:

1. Gemini
2. OpenAI
3. Anthropic
4. OpenRouter
5. Ollama

Keep `.env` private. Never commit real API keys.

## Gemini

Gemini is the current easiest option because the project already installs `google-genai`.

```text
AI_PROVIDER=auto
GEMINI_API_KEY=your_key_here
GEMINI_TEXT_MODELS=gemini-2.5-flash-lite,gemini-2.5-flash,gemini-2.0-flash
GEMINI_VISION_MODELS=gemini-2.5-flash,gemini-2.0-flash
```

## OpenAI

```text
AI_PROVIDER=openai
OPENAI_API_KEY=your_key_here
OPENAI_TEXT_MODEL=gpt-5
OPENAI_VISION_MODEL=gpt-5
```

API billing is separate from ChatGPT subscriptions.

## Anthropic

```text
AI_PROVIDER=anthropic
ANTHROPIC_API_KEY=your_key_here
ANTHROPIC_TEXT_MODEL=claude-sonnet-4-20250514
ANTHROPIC_VISION_MODEL=claude-sonnet-4-20250514
```

## OpenRouter

OpenRouter is useful when you want many models behind one key.

```text
AI_PROVIDER=openrouter
OPENROUTER_API_KEY=your_key_here
OPENROUTER_TEXT_MODEL=openrouter/auto
OPENROUTER_VISION_MODEL=openrouter/auto
```

You can replace `openrouter/auto` with a specific OpenRouter model slug.

## Ollama

Ollama runs local models on your machine and does not need an API key.

```text
AI_PROVIDER=ollama
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llava
```

Use a vision-capable local model if you want `debug my screen` to work.

## Screen Debugging

`Friday, debug my screen` sends the current screenshot to the selected provider. The screenshot is captured only after an explicit command and is not saved by Friday.

Before using screen debugging, hide sensitive content such as passwords, keys, private chats, and account pages.
