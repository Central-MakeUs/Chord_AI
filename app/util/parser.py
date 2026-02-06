import json

def parse_guide(response: str) -> dict:
    cleaned = response.strip()
    if cleaned.startswith("```json"):
        cleaned = cleaned[7:]
    if cleaned.startswith("```"):
        cleaned = cleaned[3:]
    if cleaned.endswith("```"):
        cleaned = cleaned[:-3]
    cleaned = cleaned.strip()

    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        pass

    result = {}
    current_key = None
    current_value = []

    for line in cleaned.split("\n"):
        if ":" in line:
            if current_key:
                result[current_key] = "\n".join(current_value).strip()
            key, value = line.split(":", 1)
            current_key = key.strip()
            current_value = [value.strip()]
        else:
            if current_key:
                current_value.append(line.strip())

    if current_key:
        result[current_key] = "\n".join(current_value).strip()

    return result