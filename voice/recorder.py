import os
import time
import queue
import numpy as np
import sounddevice as sd
import soundfile as sf


class AudioRecorder:

    def __init__(
        self,
        sample_rate=16000,
        channels=1,
        silence_threshold=0.015,
        silence_duration=2.0,
        warmup_time=2.5,
        max_duration=60
    ):

        self.sample_rate = sample_rate
        self.channels = channels
        self.silence_threshold = silence_threshold
        self.silence_duration = silence_duration
        self.warmup_time = warmup_time
        self.max_duration = max_duration

    #####################################################################

    def record(self, output_file="audio/answer.wav"):

        os.makedirs(os.path.dirname(output_file), exist_ok=True)

        print("\n🎤 Listening...")
        print(f"You have {self.warmup_time} seconds to prepare...")

        time.sleep(self.warmup_time)

        q = queue.Queue()

        recording = []

        speech_started = False

        silence_counter = 0.0

        start_time = time.time()

        #############################################################

        def callback(indata, frames, time_info, status):

            if status:
                print(status)

            q.put(indata.copy())

        #############################################################

        with sd.InputStream(

            samplerate=self.sample_rate,

            channels=self.channels,

            dtype="float32",

            blocksize=1024,

            callback=callback

        ):

            print("🎙 Waiting for speech...")

            while True:

                audio = q.get()

                volume = np.sqrt(np.mean(audio ** 2))

                # Uncomment once for microphone calibration
                # print(volume)

                #####################################################

                if not speech_started:

                    if volume > self.silence_threshold:

                        speech_started = True

                        print("✅ Speech detected. Recording...")

                        recording.append(audio)

                    if time.time() - start_time > self.max_duration:

                        print("No speech detected.")

                        return None

                    continue

                #####################################################

                recording.append(audio)

                duration = len(audio) / self.sample_rate

                if volume < self.silence_threshold:

                    silence_counter += duration

                else:

                    silence_counter = 0

                if silence_counter >= self.silence_duration:

                    print("🔇 Silence detected.")

                    break

                if time.time() - start_time > self.max_duration:

                    print("Maximum recording time reached.")

                    break

        #############################################################

        audio_data = np.concatenate(recording, axis=0)

        sf.write(

            output_file,

            audio_data,

            self.sample_rate

        )

        print("✅ Recording Saved")

        return output_file