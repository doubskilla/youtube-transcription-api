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

        # === 🔽 Bloc qu'on ajoute ici ===
        from pytube import YouTube
        import uuid

        print("⬇️ Téléchargement audio en cours...")
        yt = YouTube(youtube_url)
        stream = yt.streams.filter(only_audio=True).first()
        filename = f"{uuid.uuid4()}.mp4"
        stream.download(filename=filename)
        print("✅ Audio téléchargé :", filename)
        # === 🔼 Fin du bloc ajouté ===

        return jsonify({"message": "Téléchargement réussi", "fichier": filename})

    except Exception as e:
        import traceback
        traceback_str = traceback.format_exc()
        print("❌ ERREUR DÉTAILLÉE :", traceback_str)
        return jsonify({"error": str(e)}), 500
