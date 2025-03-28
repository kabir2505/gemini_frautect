from flask import Flask, request, jsonify, render_template
import json
import time
import enum
from pydantic import BaseModel
from google import genai
import os

app = Flask(__name__)

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")


class Type(enum.Enum):
    FRAUD = "fraud"
    GENUINE = "genuine"

class Output(BaseModel):
    type: Type
    reason: str


client=genai.Client(api_key=GOOGLE_API_KEY)

#
# def fetch_app_data(app_id):
#     return {"app_id": app_id, "name": "Sample App", "downloads": 10000, "reviews": 500, "category": "Finance"}

# Function to classify an app using Gemini API
def classify_app(app_data):
    time.sleep(3)  
    
    prompt = f"""
    Analyze the following app metadata and classify it as 'fraud' or 'genuine'.
    Provide a reason for your classification in 300 characters or less.
    Think about the answer carefully and give a well-reasoned answer.
    These could be some signs to assist you: Unknown or fake developer, poor grammar, exaggerated claims, 
    mismatched category, hidden charges, low-quality or stolen images, 
    fake reviews, excessive permissions, outdated or overly frequent updates, and suspicious website links.

    App Data:
    {json.dumps(app_data, indent=2)}
    """
    print(prompt)
    client=genai.Client(api_key=GOOGLE_API_KEY)
    response=client.models.generate_content(
    model="gemini-2.0-flash",
    contents=prompt,
    config={
        'response_mime_type': 'application/json',
        'response_schema': Output
    }
)
    
    try:
        result = json.loads(response.text)
        return result["type"], result["reason"]
    except:
        return "error", "Invalid response from Gemini"



# API Endpoint
@app.route("/classify", methods=["POST"])
def classify():
    data = request.json
    
    app_id = data.get("app_id")
    print('app_id',app_id)
    if not app_id:
        return jsonify({"error": "Missing app_id"}), 400

    app_data = app_id
    fraud_label, reason = classify_app(app_data)

    return jsonify({"app_id": app_id, "prediction": fraud_label, "reason": reason})


@app.route("/")
def index():
    return render_template("index.html")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))