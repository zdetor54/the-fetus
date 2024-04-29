from openai import OpenAI


# openai.api_key = "sk-proj-fXy0YRmdNuRlrCsP6FqIT3BlbkFJ4ObGV3NWySlfoNmatLur"
client = OpenAI()

audio_file= open("_assets/Recording2.mp3", "rb")
transcription = client.audio.transcriptions.create(
  model="whisper-1", 
  file=audio_file
)
print(transcription.text)

# sk-proj-fXy0YRmdNuRlrCsP6FqIT3BlbkFJ4ObGV3NWySlfoNmatLur

# setx OPENAI_API_KEY "sk-proj-fXy0YRmdNuRlrCsP6FqIT3BlbkFJ4ObGV3NWySlfoNmatLur"