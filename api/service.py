import uuid
from dataclasses import dataclass

from knowledge.knowledge_unit import KnowledgeUnitGenerator
from interview.evaluator import AnswerEvaluator
from interview.question import QuestionGenerator
from interview.state import InterviewState
from parser.doc_loader import ResumeLoader
from parser.resume_parser import ResumeExtractor
from vectorstore.chromadb import ChromaVectorStore


@dataclass
class InterviewSession:
    interview_id: str
    user_id: str
    filename: str
    knowledge_units: list
    retriever: object
    question_generator: QuestionGenerator
    evaluator: AnswerEvaluator
    state: InterviewState
    topics: list[str]
    current_topic_index: int = 0


class InterviewService:
    def __init__(self) -> None:
        self.sessions: dict[str, InterviewSession] = {}
        self.resume_extractor = ResumeExtractor()
        self.knowledge_generator = KnowledgeUnitGenerator()

    def create_session(
        self,
        pdf_path: str,
        filename: str,
        user_id: str,
        interview_id: str | None = None,
    ) -> InterviewSession:
        # This is the expensive AI/RAG preparation stage. It runs when the
        # user uploads the resume, so clicking Start Interview is fast.
        resume_text = ResumeLoader(pdf_path).load_resume()
        resume_json = self.resume_extractor.extract(resume_text)
        knowledge_units = self.knowledge_generator.generate(resume_json)

        vector_store = ChromaVectorStore()
        vector_store.create_vector_store(knowledge_units)
        retriever = vector_store.get_retriever()

        topics = self._extract_topics(knowledge_units)
        if not topics:
            raise ValueError("No interview topics could be generated from the resume.")

        session = InterviewSession(
            interview_id=interview_id or str(uuid.uuid4()),
            user_id=user_id,
            filename=filename,
            knowledge_units=knowledge_units,
            retriever=retriever,
            question_generator=QuestionGenerator(),
            evaluator=AnswerEvaluator(),
            state=InterviewState(),
            topics=topics,
        )
        self.sessions[session.interview_id] = session
        return session

    def get_session(self, interview_id: str) -> InterviewSession:
        session = self.sessions.get(interview_id)
        if session is None:
            raise KeyError("Interview session not found")
        return session

    def start(self, interview_id: str, user_id: str) -> tuple[str, str, str]:
        session = self.get_session(interview_id)
        self._check_owner(session, user_id)
        self._set_current_topic(session)
        question = self._generate_question(session)
        return session.state.current_topic, session.state.current_difficulty, question

    def answer(self, interview_id: str, user_id: str, question: str, answer: str) -> dict:
        session = self.get_session(interview_id)
        self._check_owner(session, user_id)
        state = session.state
        docs = session.retriever.invoke(state.current_topic)
        result = session.evaluator.evaluate(
            retrieved_docs=docs,
            question=question,
            answer=answer,
            difficulty=state.current_difficulty,
        )

        state.add_question(question)
        state.add_conversation(question, answer)
        state.add_evaluation(result)
        state.next_question()

        action = self._next_action(session, result)
        if action == "NEXT_TOPIC":
            state.complete_current_topic()
            session.current_topic_index += 1
            if session.current_topic_index >= len(session.topics):
                return {"evaluation": result, "completed": True}
            self._set_current_topic(session)

        next_question = self._generate_question(session)
        return {
            "evaluation": result,
            "completed": False,
            "next_topic": state.current_topic,
            "next_difficulty": state.current_difficulty,
            "next_question": next_question,
        }

    def _generate_question(self, session: InterviewSession) -> str:
        docs = session.retriever.invoke(session.state.current_topic)
        return session.question_generator.generate_question(
            retrieved_docs=docs,
            state=session.state,
        )

    def _set_current_topic(self, session: InterviewSession) -> None:
        topic = session.topics[session.current_topic_index]
        session.state.set_topic(topic)
        session.state.set_difficulty("Easy")
        session.state.reset_attempts()

    @staticmethod
    def _check_owner(session: InterviewSession, user_id: str) -> None:
        if session.user_id != user_id:
            raise PermissionError("You do not own this interview")

    def _next_action(self, session: InterviewSession, result: dict) -> str:
        score = result["score"]
        difficulty = session.state.current_difficulty

        if difficulty == "Easy":
            if score >= 4:
                session.state.set_difficulty("Medium")
                return "CONTINUE"
            session.state.increase_attempt()
            if session.state.current_topic_attempts >= 2:
                return "NEXT_TOPIC"
            return "CONTINUE"

        if difficulty == "Medium":
            if score >= 4:
                session.state.set_difficulty("Hard")
                return "CONTINUE"
            session.state.increase_attempt()
            if session.state.current_topic_attempts >= 2:
                return "NEXT_TOPIC"
            session.state.set_difficulty("Easy")
            return "CONTINUE"

        if score >= 6:
            return "NEXT_TOPIC"
        session.state.increase_attempt()
        if session.state.current_topic_attempts >= 2:
            return "NEXT_TOPIC"
        session.state.set_difficulty("Easy")
        return "CONTINUE"

    @staticmethod
    def _extract_topics(knowledge_units: list) -> list[str]:
        priority = ["projects", "experience", "technical_skills", "education"]
        return [
            unit["title"]
            for section in priority
            for unit in knowledge_units
            if unit["type"] == section
        ]
