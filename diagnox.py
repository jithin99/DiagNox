import requests
import json
import re

# =========================
# 🔍 EXTRACT VITALS FROM INPUT
# =========================
def extract_vitals(text):
    vitals = {}

    try:
        hr = re.search(r'HR\s*(\d+)', text, re.IGNORECASE)
        bp = re.search(r'BP\s*(\d+/\d+)', text, re.IGNORECASE)
        spo2 = re.search(r'SpO2\s*(\d+)', text, re.IGNORECASE)
        temp = re.search(r'(Temp|Temperature)\s*([\d\.]+)', text, re.IGNORECASE)

        if hr:
            vitals["heart_rate"] = int(hr.group(1))
        if bp:
            vitals["blood_pressure"] = bp.group(1)
        if spo2:
            vitals["spo2"] = int(spo2.group(1))
        if temp:
            vitals["temperature"] = float(temp.group(2))

    except:
        pass

    return vitals


# =========================
# 📄 LOAD PROMPT
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
        vitals="Extract from input",
        labs="Extract from input"
    )


# =========================
# 🧹 CLEAN JSON (ROBUST)
# =========================
def clean_json(response_text):
    try:
        start = response_text.find('{')
        end = response_text.rfind('}')

        if start != -1 and end != -1:
            json_text = response_text[start:end+1]
            parsed = json.loads(json_text)
            return parsed
        else:
            return {
                "error": "No JSON found",
                "confidence": 0.0
            }

    except Exception:
        return {
            "error": "Invalid JSON format",
            "confidence": 0.0
        }


# =========================
# 🤖 MAIN FUNCTION
# =========================
def diagnox_chat(user_input):

    # 🔹 Extract vitals BEFORE sending to model
    extracted_vitals = extract_vitals(user_input)

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

        parsed = clean_json(result)

        # =========================
        # 🔥 MERGE EXTRACTED VITALS INTO OUTPUT
        # =========================
        if isinstance(parsed, dict):
            parsed["extracted_vitals"] = extracted_vitals

        return json.dumps(parsed)

    except Exception as e:
        return json.dumps({
            "error": "Model request failed",
            "details": str(e),
            "confidence": 0.0
        })