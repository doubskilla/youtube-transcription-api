from flask import Flask, request, jsonify
import os
import uuid
import requests
from pytube import YouTube
import traceback

app = Flask(__name__)

# Récupère ta clé OpenAI depuis les variables d’environnement (Render)
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
OPENAI_WHISPER_ENDPOINT = "https://api.openai.com/v1/audio/transcriptions"

@app.route("/transcribe", methods=["POST"])
def transcribe():
    print("🚀 Requête reçue dans /transcribe")
    
    data = request.get_json()
    youtube_url = data.get("url")
    print("🔗 URL reçue :", youtube_url)

    if not youtube_url:
        return jsonify({"error": "Aucune URL YouTube fournie"}), 400

    try:
        # Téléchargement audio de YouTube
        print("⬇️ Téléchargement audio en cours...")
        yt = YouTube(youtube_url)
        stream = yt.streams.filter(only_audio=True).first()
        filename = f"{uuid.uuid4()}.mp4"
        stream.download(filename=filename)
        print("✅ Audio téléchargé :", filename)

        # Appel à Whisper (OpenAI)
        print("📤 Envoi vers Whisper API...")
        with open(filename, "rb") as f:
            files = {
                "file": (filename, f, "audio/mp4")
            }
            data = {
                "model": "whisper-1"
            }
            headers = {
                "Authorization": f"Bearer {OPENAI_API_KEY}"
            }
            response = requests.post(
                OPENAI_WHISPER_ENDPOINT,
                headers=headers,
                data=data,
                files=files
            )

        os.remove(filename)  # Nettoyage du fichier audio

        if response.status_code != 200:
            print("❌ Whisper API a échoué :", response.text)
            return jsonify({
                "error": "Whisper API a échoué",
                "details": response.text
            }), 500

        transcription = response.json()["text"]
        print("📝 Transcription obtenue !")
        return jsonify({"transcription": transcription})

    except Exception as e:
        print("❌ ERREUR 500 :", str(e))
        print("🧠 Trace complète :")
        print(traceback.format_exc())  # Affiche toute l'erreur dans les logs
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
