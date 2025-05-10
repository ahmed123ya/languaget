from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

# Replace this with your Hugging Face token
HUGGINGFACE_API_TOKEN = "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"

# Language code map (Dialogflow name to model suffix)
lang_map = {
    "French": "fr",
    "German": "de",
    "Hindi": "hi",
    "Spanish": "es",
    "Urdu": "ur",
    "Italian": "it",
    "Russian": "ru"
}

# Hugging Face model name (using Helsinki-NLP models)
def get_model_name(target_lang_code):
    return f"Helsinki-NLP/opus-mt-en-{target_lang_code}"

# Translation function
def translate_text(text, target_lang):
    lang_code = lang_map.get(target_lang.capitalize())

    if not lang_code:
        return f"Language '{target_lang}' not supported."

    model = get_model_name(lang_code)
    url = f"https://api-inference.huggingface.co/models/{model}"

    headers = {
        "Authorization": f"Bearer {HUGGINGFACE_API_TOKEN}"
    }

    payload = {
        "inputs": text
    }

    response = requests.post(url, headers=headers, json=payload)

    if response.status_code == 200:
        try:
            return response.json()[0]["translation_text"]
        except:
            return "Translation error in response."
    elif response.status_code == 503:
        return "Model is loading. Please try again in a few seconds."
    else:
        return f"API Error: {response.status_code} - {response.text}"

@app.route("/webhook", methods=["POST"])
def webhook():
    req = request.get_json()
    print("Received request:", req)

    try:
        text = req["queryResult"]["parameters"]["text_to_translate"]
        target_lang = req["queryResult"]["parameters"]["target_language"]

        result = translate_text(text, target_lang)
        print("Translation result:", result)

        return jsonify({
            "fulfillmentText": result
        })

    except Exception as e:
        return jsonify({
            "fulfillmentText": f"Error: {str(e)}"
        })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
