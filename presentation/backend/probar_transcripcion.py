from core.use_cases.audio_processing import AudioProcessingUseCase

if __name__ == "__main__":
    print("✅ El script se está ejecutando correctamente.")  # CONFIRMACIÓN 1

    use_case = AudioProcessingUseCase()
    print("🎙️ Preparado para grabar...")  # CONFIRMACIÓN 2

    transcription = use_case.process_audio()
    print("📝 Texto transcrito:", transcription.text)  # RESULTADO
