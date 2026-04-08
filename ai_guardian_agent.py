import warnings
import google.generativeai as genai

# Suppress Deprecation Warnings for cleaner Tactical Logs
warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", message=".*google.generativeai.*")

from config import GEMINI_API_KEY, SAFETY_MODE
import time
from PIL import Image
import os

class AIGuardianAgent:
    def __init__(self):
        genai.configure(api_key=GEMINI_API_KEY)
        self.model = genai.GenerativeModel('gemini-1.5-flash-latest')
        self.vision_model = genai.GenerativeModel('gemini-1.5-flash-latest')

    def automate_chat_response(self, customer_name, chat_history):
        """Unified Chat Automation: Replies to customers and sends payment details."""
        prompt = f"""
        Platform: P2P USDT/ILS (Bybit/Binance/OKX/MEXC)
        Customer Name: {customer_name}
        Chat History: {chat_history}
        Task: 
        1. Greet the customer and thank them for buying.
        2. Send them the payment details: "Bank Hapoalim, Branch 612, Account 123456789".
        3. ADD MANDATORY SECURITY: "Please confirm that the name on the bank account is EXACTLY the same as your platform name."
        4. If customer says "I pay for my friend", warn them: "We only allow same-name transfers for security."
        Return the exact message to send.
        """
        try:
            response = self.model.generate_content(prompt)
            return response.text.strip()
        except Exception as e:
            print(f"Error calling Gemini NLP: {e}")
            return "Please provide a valid payment name match."

    def verify_payment_proof(self, image_path, expected_amount, reference_code):
        """OCR Proof Verification: Cross-references bank screenshot details."""
        if not os.path.exists(image_path) or not SAFETY_MODE:
            return None

        try:
            img = Image.open(image_path)
            prompt = f"""
            Identify from this bank transfer screenshot:
            1. Amount: Check if it matches {expected_amount} ILS.
            2. Reference Code: Check if it matches {reference_code}.
            3. Account Holder: Check if it matches the name.
            Return 'VERIFIED' or 'SUSPICIOUS' with reasoning.
            """
            response = self.vision_model.generate_content([prompt, img])
            return response.text
        except Exception as e:
            print(f"Error calling Gemini Vision: {e}")
            return "OCR Verification Error"

if __name__ == "__main__":
    # Test Block
    print("🧪 Testing AI Guardian Agent...")
    guardian = AIGuardianAgent()
    
    test_chat = "Hi, I just bought 100 USDT. Can I pay you from my brother's account?"
    print(f"\n[Input Chat]: {test_chat}")
    
    response = guardian.automate_chat_response("TestUser", test_chat)
    print(f"\n[AI Response]:\n{response}")
