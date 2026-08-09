from faster_whisper import WhisperModel


class SpeechToText:

    def __init__(
        self,
        model_size="base",
        device="cpu",
        compute_type="int8"
    ):

        print("Loading Whisper Model...")

        self.model = WhisperModel(
            model_size,
            device=device,
            compute_type=compute_type
        )

        print("Whisper Loaded Successfully.")

    ########################################################

    def transcribe(self, audio_path):

        print("\nTranscribing Audio...\n")

        segments, info = self.model.transcribe(
    audio_path,
    beam_size=5,
    language="en",
    vad_filter=True
)

              
        text = ""

        for segment in segments:
            text += segment.text + " "

        text = text.strip()

        print("Candidate Answer:")
        print(text)

        return text