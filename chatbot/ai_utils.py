import google.generativeai as genai
from meal_system import settings

# Configure Gemini API with your key from .env
# Make sure .env includes: GOOGLE_API_KEY=your_key_here
genai.configure(api_key=settings.env.str("GOOGLE_API_KEY", None))


def gemini_generate(prompt, model_name="gemini-2.0-flash", temperature=0.4):
    """
    Generate an AI response using Google's Gemini model.
    Automatically handles missing API key, errors, or connection issues.
    """

    if not settings.env.str("GOOGLE_API_KEY", None):
        print("⚠️ GOOGLE_API_KEY missing in .env — please add it to enable Gemini API.")
        return "⚠️ AI assistant is currently unavailable."

    try:
        # Initialize Gemini model
        model = genai.GenerativeModel(model_name)

        # Generate response
        response = model.generate_content(
            prompt,
            generation_config={
                "temperature": temperature,
                "max_output_tokens": 300,
            },
        )

        # Return clean text response
        return response.text.strip() if response.text else "⚠️ No response generated."

    except Exception as e:
        print("[Gemini API Error]", e)
        return "⚠️ AI assistant is currently unavailable."
