from openai import OpenAI
client = OpenAI(api_key="sk-proj-fXy0YRmdNuRlrCsP6FqIT3BlbkFJ4ObGV3NWySlfoNmatLur")

# audio_file= open("_assets/Recording2.mp3", "rb")
# transcription = client.audio.transcriptions.create(
#   model="whisper-1", 
#   file=audio_file
# )
# print(transcription.text)


# from openai import OpenAI
# client = OpenAI()

response = client.chat.completions.create(
  model="gpt-3.5-turbo-0125",
  response_format={ "type": "json_object" },
  messages=[
    {"role": "system", "content": "You are a helpful assistant designed to output JSON."},
    {"role": "user", "content": "Who won the world series in 2020?"}
  ]
)
print(response.choices[0].message.content)