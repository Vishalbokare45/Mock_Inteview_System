import asyncio
import edge_tts
import pygame
import os


class TextToSpeech:

    def __init__(self):

        # Natural Microsoft voice
        self.voice = "en-US-AriaNeural"

        pygame.mixer.init()

    ##############################################################

    async def _generate_audio(self, text, output_file):

        communicate = edge_tts.Communicate(
            text=text,
            voice=self.voice
        )

        await communicate.save(output_file)

    ##############################################################

    def speak(self, text):

        if not text:
            return

        print(f"\n🤖 AI Interviewer:\n{text}\n")

        output_file = "temp_tts.mp3"

        asyncio.run(
            self._generate_audio(text, output_file)
        )

        pygame.mixer.music.load(output_file)

        pygame.mixer.music.play()

        while pygame.mixer.music.get_busy():
            pygame.time.Clock().tick(10)

        pygame.mixer.music.unload()

        if os.path.exists(output_file):
            os.remove(output_file)