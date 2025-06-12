from flask import Flask, request, jsonify
import base64
import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

app = Flask(__name__)

def encode_image(image_file):
    return base64.b64encode(image_file.read()).decode("utf-8")

@app.route('/analyze-image', methods=['POST'])
def analyze_image():
    if 'image' not in request.files:
        return jsonify({'error': 'Missing image file'}), 400

    image_file = request.files['image']
    image_data = encode_image(image_file)

    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text":
                                "You are an anomaly detection expert. "
                                "Analyze the attached image and respond with only one of the following: "
                                "'Suspicious' – if the image contains any unusual, dangerous, or contextually abnormal object; "
                                "or 'Not suspicious' – if the scene appears normal and nothing unusual is present. "
                                "Do not provide any explanation. Respond with only one word: 'Suspicious' or 'Not suspicious'."
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{image_data}"
                            }
                        }
                    ]
                }
            ],
            max_tokens=5
        )

        result_text = response.choices[0].message.content.strip()

        is_suspicious = result_text.lower().startswith("suspicious")

        return jsonify({
            'result': result_text,
            'suspicious': is_suspicious
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000)
