import google.generativeai as genai
from config import GEMINI_API_KEY, AI_VISION_LEVEL
from PIL import Image
import os

class AIGuardian:
    def __init__(self):
        genai.configure(api_key=GEMINI_API_KEY)
        # Using Gemini 1.5 Flash for speed and cost-efficiency
        self.model = genai.GenerativeModel('gemini-1.5-flash-latest')
        self.vision_level = os.getenv('AI_VISION_LEVEL', 'STRICT')

    def analyze_chat(self, chat_history):
        """Analyzes chat messages for fraud signals using Gemini NLP."""
        prompt = f"""
        Analyze the following P2P chat history for signs of fraud: 
        1. Requesting to pay from 3rd party accounts.
        2. Suspicious language patterns or social engineering.
        3. Attempts to move the chat out of the platform.
        Chat: {chat_history}
        Return 'BLOCK' if fraud intent is detected, else 'CLEAR'.
        """
        try:
            response = self.model.generate_content(prompt)
            return response.text.strip()
        except Exception as e:
            print(f"Error calling Gemini NLP: {e}")
            return "CLEAR"  # Default to clear if API fails, but log error

    def verify_screenshot(self, image_path, reference_number, expected_amount):
        """Performs OCR and cross-references bank transfer details."""
        if not os.path.exists(image_path) or AI_VISION_LEVEL != 'STRICT':
            return False

        try:
            img = Image.open(image_path)
            prompt = f"""
            Identify from this bank transfer screenshot:
            1. Amount: Check if it matches {expected_amount}.
            2. Reference Number: Check if it matches {reference_number}.
            3. Account Holder Name: Is it distinct from the platform user's name?
            Return JSON: {{"valid": true/false, "amount_match": true/false, "ref_match": true/false}}
            """
            response = self.model.generate_content([prompt, img])
            return response.text
        except Exception as e:
            print(f"Error calling Gemini Vision: {e}")
            return None
