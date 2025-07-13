from flask import Flask, request, jsonify
import requests
import os
import uuid
import traceback
from bs4 import BeautifulSoup

app = Flask(__name__)

OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
WHISPER_ENDPOINT = "https://api.openai.com/v1/audio/transcriptions"

@app.route("/transcribe", methods=["POST"])
def transcribe():
    try:
        data = request.get_json()
        youtube_url = data.get("url")

        if not youtube_url:
            return jsonify({"error": "Aucune URL fournie"}), 400

        print("🔗 URL YouTube reçue :", youtube_url)

        # 1️⃣ Étape 1 : Obtenir lien MP3
        yt_api_url = f"https://yt-download.org/api/widget/mp3/{youtube_url}"
        yt_html = requests.get(yt_api_url).text
        soup = BeautifulSoup(yt_html, 'html.parser')
        mp3_link = soup.find("a", string="Download MP3")
        if not mp3_link:
            return jsonify({"error": "Impossible de récupérer le MP3"}), 500

        mp3_url = mp3_link.get("href")
        print("🎧 MP3 trouvé :", mp3_url)

        # 2️⃣ Étape 2 : Télécharger le MP3
        filename = f"{uuid.uuid4()}.mp3"
        r = requests.get(mp3_url)
        with open(filename, 'wb') as f:
            f.write(r.content)
        print("✅ MP3 téléchargé :", filename)

        # 3️⃣ Étape 3 : Transcription avec Whisper
        with open(filename, 'rb') as f:
            response = requests.post(
                WHISPER_ENDPOINT,
                headers={"Authorization": f"Bearer {OPENAI_API_KEY}"},
                data={"model": "whisper-1"},
                files={"file": (filename, f, "audio/mp3")}
            )

        os.remove(filename)  # Nettoyage

        if response.status_code != 200:
            return jsonify({"error": "Échec Whisper", "details": response.text}), 500

        transcription = response.json().get("text", "")
        return jsonify({"transcription": transcription})

    except Exception as e:
        print("❌ ERREUR :", traceback.format_exc())
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
