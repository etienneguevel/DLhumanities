import os
from io import BytesIO

import pytesseract
import requests
import torch
from PIL import Image
from transformers import AutoModelForSpeechSeq2Seq, AutoProcessor, pipeline


def extract_text_from_image(image_url):
    response = requests.get(image_url)
    if response.status_code == 200:
        image = Image.open(BytesIO(response.content))
        text = pytesseract.image_to_string(image)
        return text
    
    else:
        print("Failer to download image. HTTP status code:", response.status_code)
        return None

def load_model(model_id):
    model = AutoModelForSpeechSeq2Seq.from_pretrained(model_id)
    processor = AutoProcessor.from_pretrained(model_id)
    return model, processor


def extract_text_from_audio(model_id, audio_path):
    model, processor = load_model(model_id)
    pipe = pipeline(
        task="automatic-speech-recognition",
        model=model,
        tokenizer=processor.tokenizer,
        feature_extractor=processor.feature_extractor,
    )
    
    result = pipe(audio_path)

    return result["text"]

