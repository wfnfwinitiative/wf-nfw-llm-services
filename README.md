
# 🌿 No Food Waste — Backend API

An AI-powered FastAPI microservice that converts spoken audio (in any language) into an English transcript and extracts structured food donation metadata such as location, food items, quantity, quality, and pickup time.

---

## 🚀 Features

- Accepts audio uploads
- Multilingual speech support
- Speech → English translation
- Metadata extraction using AI
- FastAPI REST API
- JSON responses

---

## 🧱 Tech Stack

- FastAPI
- OpenAI APIs
- Pydantic
- Python

---

## 📁 Project Structure

<img width="358" height="337" alt="image" src="https://github.com/user-attachments/assets/644b7990-c890-4c69-a158-0d40f570a4b1" />


---

## ⚙️ Setup

1. Create virtual environment
python -m venv venv
venv\Scripts\activate

2. Install dependencies
pip install fastapi uvicorn openai python-dotenv python-multipart

3. Add .env file
OPENAI_API_KEY=your_key_here

4. Run server
uvicorn app.main:app --reload

---

## 📡 Endpoint

POST /process-audio?mode=api

Returns transcript + metadata.

---

## 🧾 Example Response

{
  "items": [
    {
      "foodName": "rice packets",
      "quantity": "30 packets",
      "quality": "good"
    },
    {
      "foodName": "pickle packets",
      "quantity": "30 packets",
      "quality": "good"
    },
    {
      "foodName": "sambar",
      "quantity": null,
      "quality": "bad"
    },
    {
      "foodName": "palya",
      "quantity": "enough for 20 people",
      "quality": "bad"
    }
  ]
}
