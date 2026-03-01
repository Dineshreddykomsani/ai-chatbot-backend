import os
from openai import OpenAI


def build_prompt(messages):
    prompt = [
        {"role": "system", "content": "You are a helpful AI assistant."}
    ]

    for msg in messages:
        prompt.append({
            "role": msg.role,
            "content": msg.content
        })

    return prompt


def call_llm(prompt):
    try:
        client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=prompt,
            timeout=10
        )
        return response.choices[0].message.content

    except Exception:
        return "Sorry, I'm currently unavailable. Please try again later."