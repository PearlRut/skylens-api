from flask import Flask, request, jsonify
import base64
import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

app = Flask(__name__)

# הפיכת קובץ תמונה ל־base64 string
def encode_image(image_file):
    return base64.b64encode(image_file.read()).decode("utf-8")

@app.route('/analyze-image', methods=['POST'])
def analyze_image():
    # ודא שכל התמונות והנתונים קיימים
    required_files = ['image1', 'image2', 'image3']
    required_fields = ['x', 'y', 'z', 'timestamp']

    if not all(field in request.form for field in required_fields):
        return jsonify({'error': 'Missing one or more required fields: x, y, z, timestamp'}), 400

    if not all(img in request.files for img in required_files):
        return jsonify({'error': 'Missing one or more required image files: image1, image2, image3'}), 400

    # קריאת הנתונים
    x = request.form.get('x')
    y = request.form.get('y')
    z = request.form.get('z')
    timestamp = request.form.get('timestamp')

    try:
        # קידוד שלוש התמונות ל־base64
        images_data = [
            {
                "type": "image_url",
                "image_url": {
                    "url": f"data:image/jpeg;base64,{encode_image(request.files[img])}"
                }
            }
            for img in ['image1', 'image2', 'image3']
        ]

        # ניסוח הפרומפט עם קואורדינטות וזמן
        prompt = (
            f"You are analyzing a real-world scene captured from three different cameras.\n"
            f"The location is X={x}, Y={y}, Z={z} and the time is {timestamp}.\n"
            f"Based on the combined visual evidence, respond in one word:\n"
            f"'Suspicious' – if any of the images or the combined context suggest an unusual, dangerous or out-of-place object/event.\n"
            f"Otherwise, return 'Not suspicious'. Respond with only one word."
        )

        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "user",
                    "content": [{"type": "text", "text": prompt}] + images_data
                }
            ],
            max_tokens=5
        )

        result_text = response.choices[0].message.content.strip()
        is_suspicious = result_text.lower().startswith("suspicious")

        return jsonify({
            'result': result_text,
            'suspicious': is_suspicious,
            'location': {'x': x, 'y': y, 'z': z},
            'timestamp': timestamp
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000)
