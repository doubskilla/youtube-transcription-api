from flask import Flask, request, jsonify
import traceback

app = Flask(__name__)

@app.route("/transcribe", methods=["POST"])
def transcribe():
    try:
        print("🚀 La fonction /transcribe a bien démarré")
        data = request.get_json()
        youtube_url = data.get("url")
        print("🔗 URL reçue :", youtube_url)

        if not youtube_url:
            print("❌ Pas d’URL dans la requête")
            return jsonify({"error": "Aucune URL fournie"}), 400

        return jsonify({"message": "URL bien reçue", "url": youtube_url})

    except Exception as e:
        traceback_str = traceback.format_exc()
        print("❌ ERREUR DÉTAILLÉE :", traceback_str)
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    import os
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
