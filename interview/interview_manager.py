from interview.state import InterviewState
from voice.tts import TextToSpeech
from voice.recorder import AudioRecorder
from voice.speechtotext import SpeechToText


class InterviewManager:

    def __init__(
        self,
        retriever,
        question_generator,
        evaluator,
        knowledge_units
    ):

        self.retriever = retriever
        self.question_generator = question_generator
        self.evaluator = evaluator
        self.tts = TextToSpeech()

        self.recorder = AudioRecorder()

        self.stt = SpeechToText()

        self.state = InterviewState()

        self.topics = self._extract_topics(knowledge_units)

        self.current_topic_index = 0

    ##################################################################

    def start_interview(self):

        print("\n" + "=" * 80)
        print("AI POWERED MOCK INTERVIEW")
        print("=" * 80)

        while self.current_topic_index < len(self.topics):

            topic = self.topics[self.current_topic_index]

            print("\n")
            print("=" * 80)
            print(f"CURRENT TOPIC : {topic}")
            print("=" * 80)

            self.state.set_topic(topic)
            self.state.set_difficulty("Easy")
            self.state.reset_attempts()

            self._interview_topic()

            self.state.complete_current_topic()

            self.current_topic_index += 1

        print("\nInterview Completed Successfully.")

    ##################################################################

    def _interview_topic(self):

        while True:

            docs = self.retriever.invoke(self.state.current_topic)

            question = self.question_generator.generate_question(
                retrieved_docs=docs,
                state=self.state
            )

            print("\n")
            print("-" * 80)
            # print(question)
            self.tts.speak(question)

            print("-" * 80)

            # answer = input("\nYour Answer : ")
            audio_path = self.recorder.record()
            answer = self.stt.transcribe(audio_path)

            print("\nCandidate Answer:")
            print(answer)

            result = self.evaluator.evaluate(

                retrieved_docs=docs,

                question=question,

                answer=answer,

                difficulty=self.state.current_difficulty

            )

            self.state.add_question(question)

            self.state.add_conversation(
                question,
                answer
            )

            self.state.add_evaluation(result)

            print("\nEvaluation")
            print(result)

            action = self._next_action(result)

            if action == "NEXT_TOPIC":
                break

    ##################################################################

    def _next_action(self, result):

        score = result["score"]

        difficulty = self.state.current_difficulty

        ##############################################################

        if difficulty == "Easy":

            if score >= 4:

                print("\nEasy Cleared")

                self.state.set_difficulty("Medium")

                return "CONTINUE"

            else:

                self.state.increase_attempt()

                if self.state.current_topic_attempts >= 2:

                    print("\nEasy failed twice.")

                    return "NEXT_TOPIC"

                print("\nRepeating Easy Question")

                return "CONTINUE"

        ##############################################################

        elif difficulty == "Medium":

            if score >= 4:

                print("\nMedium Cleared")

                self.state.set_difficulty("Hard")

                return "CONTINUE"

            else:

                self.state.increase_attempt()

                if self.state.current_topic_attempts >= 2:

                    print("\nMedium failed twice.")

                    return "NEXT_TOPIC"

                print("\nGoing back to Easy")

                self.state.set_difficulty("Easy")

                return "CONTINUE"

        ##############################################################

        elif difficulty == "Hard":

            if score >= 6:

                print("\nTopic Completed.")

                return "NEXT_TOPIC"

            else:

                self.state.increase_attempt()

                if self.state.current_topic_attempts >= 2:

                    print("\nHard failed twice.")

                    return "NEXT_TOPIC"

                print("\nReturning to Easy")

                self.state.set_difficulty("Easy")
   
                return "CONTINUE"

    ##################################################################

    def _extract_topics(self, knowledge_units):

        priority = [

            "projects",

            "experience",

            "technical_skills",

            "education"

        ]

        topics = []

        for section in priority:

            for unit in knowledge_units:

                if unit["type"] == section:

                    topics.append(unit["title"])

        return topics