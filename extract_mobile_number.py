import openai

# Replace 'your-api-key' with your actual OpenAI API key
openai.api_key = "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"

def extract_mobile_number(text):
    # Define the prompt
    prompt = f"Extract the mobile number from the following text: {text}"

    # Make the API call
    response = openai.Completion.create(
        engine="text-davinci-003",  # You can use other engines like "gpt-3.5-turbo"
        prompt=prompt,
        max_tokens=50,
        n=1,
        stop=None,
        temperature=0.5,
    )

    # Extract the mobile number from the response
    mobile_number = response.choices[0].text.strip()

    return mobile_number

# Example usage
text = "You can contact me at 123-456-7890 for more details."
mobile_number = extract_mobile_number(text)
print(f"Extracted mobile number: {mobile_number}")
