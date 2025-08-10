import requests

API_KEY = "d2aefeac9dc661bc98eebd6cc12f0b82"


def translate_text(text, from_lang, to_lang):
    url = 'https://web-api.itranslateapp.com/v3/texts/translate'
    payload = {
        "source": {
            "dialect": from_lang,
            "text": text,
            "with": ["synonyms"]
        },
        "target": {
            "dialect": to_lang
        }
    }
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "API-KEY": API_KEY
    }
    try:
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()
        data = response.json()
        return data['target']['text']
    except Exception as e:
        return ""