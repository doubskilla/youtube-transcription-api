from flask import Flask, request, jsonify
import os
import uuid
import whisper
from pytube import YouTube

app = Flask(__name__)

@app.route("/transcribe", methods=["POST"])
def transcribe():
    data = request.get_json()
    youtube_url = data.get("url")
    print("Reçu :", youtube_url)

    if not youtube_url:
        return jsonify({"error": "No YouTube URL provided"}), 400

    try:
        # Télécharger la vidéo YouTube
        yt = YouTube(youtube_url)
        stream = yt.streams.filter(only_audio=True).first()
        filename = f"{uuid.uuid4()}.mp4"
        stream.download(filename=filename)

        # Transcription avec Whisper
        model = whisper.load_model("tiny", device="cpu")
        result = model.transcribe(filename)

        os.remove(filename)

        return jsonify({"transcription": result["text"]})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
