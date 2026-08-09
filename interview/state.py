from dataclasses import dataclass, field


@dataclass
class InterviewState:

    # Current topic being discussed
    current_topic: str = ""

    # Easy / Medium / Hard
    current_difficulty: str = "Easy"

    # Current question number
    question_number: int = 1

    # Number of attempts on current topic
    current_topic_attempts: int = 0

    # Topics already completed
    covered_topics: list = field(default_factory=list)

    # Previously asked questions
    asked_questions: list = field(default_factory=list)

    # Conversation memory
    conversation: list = field(default_factory=list)

    # Evaluation results
    evaluation_history: list = field(default_factory=list)

    ######################################################

    def set_topic(self, topic):

        self.current_topic = topic

    ######################################################

    def set_difficulty(self, difficulty):

        self.current_difficulty = difficulty

    ######################################################

    def increase_attempt(self):

        self.current_topic_attempts += 1

    ######################################################

    def reset_attempts(self):

        self.current_topic_attempts = 0

    ######################################################

    def next_question(self):

        self.question_number += 1

    ######################################################

    def add_question(self, question):

        self.asked_questions.append(question)

    ######################################################

    def add_conversation(self, question, answer):

        self.conversation.append(
            {
                "question": question,
                "answer": answer
            }
        )

    ######################################################

    def add_evaluation(self, evaluation):

        self.evaluation_history.append(evaluation)

    ######################################################

    def complete_current_topic(self):

        if self.current_topic not in self.covered_topics:

            self.covered_topics.append(self.current_topic)

        self.current_topic = ""
        self.current_difficulty = "Easy"
        self.current_topic_attempts = 0