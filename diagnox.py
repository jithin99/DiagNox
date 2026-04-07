import requests
import json
import time

# =========================
# 🔷 LOAD PROMPT
# =========================
def load_prompt(user_input):
    with open("prompt.txt", "r") as file:
        template = file.read()

    return template.format(
        age="Unknown",
        gender="Unknown",
        symptoms=user_input,
        duration="Unknown",
        severity="Unknown",
        history="None",
        medications="None",
        vitals="None",
        labs="None"
    )


# =========================
# 🔷 JSON CLEANER (ROBUST)
# =========================
def clean_json(response_text):
    try:
        start = response_text.find('{')
        end = response_text.rfind('}')

        if start == -1 or end == -1:
            raise ValueError("No JSON found")

        json_text = response_text[start:end+1]

        # Fix common LLM issues
        json_text = json_text.replace("\n", " ")
        json_text = json_text.replace("\t", " ")

        # Remove trailing commas
        import re
        json_text = re.sub(r',\s*}', '}', json_text)
        json_text = re.sub(r',\s*]', ']', json_text)

        parsed = json.loads(json_text)

        return json.dumps(parsed)

    except Exception:
        return None


# =========================
# 🔷 FALLBACK RESPONSE
# =========================
def failsafe():
    return json.dumps({
        "error": "Invalid or unstructured response from model",
        "confidence": 0.0
    })


# =========================
# 🔷 MAIN FUNCTION
# =========================
def diagnox_chat(user_input):

    prompt = load_prompt(user_input)

    try:
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": "llama3",
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0,
                    "top_p": 0.1,
                    "repeat_penalty": 1.2
                }
            },
            timeout=60
        )

        result = response.json().get("response", "")

        # =========================
        # 🔁 TRY CLEANING
        # =========================
        cleaned = clean_json(result)

        if cleaned:
            return cleaned

        # =========================
        # 🔁 RETRY ONCE (VERY IMPORTANT)
        # =========================
        time.sleep(1)

        retry_response = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": "llama3",
                "prompt": prompt + "\n\nReturn ONLY valid JSON. No text.",
                "stream": False,
                "options": {
                    "temperature": 0
                }
            },
            timeout=60
        )

        retry_result = retry_response.json().get("response", "")
        cleaned_retry = clean_json(retry_result)

        if cleaned_retry:
            return cleaned_retry

        # =========================
        # ❌ FINAL FAILSAFE
        # =========================
        return failsafe()

    except Exception:
        return failsafe()