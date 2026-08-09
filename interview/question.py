from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage, HumanMessage
from dotenv import load_dotenv

from interview.QPrompt import QUESTION_GENERATION_PROMPT

load_dotenv()


class QuestionGenerator:

    def __init__(self):

        self.llm = ChatGroq(
            model="llama-3.3-70b-versatile",
            temperature=0.3
        )

    ##############################################################

    def generate_question(self, retrieved_docs, state):

        context = self._build_context(retrieved_docs)

        previous_questions = "\n".join(state.asked_questions)

        conversation = self._build_conversation(state.conversation)

        human_prompt = f"""
Resume Context
----------------
{context}

Current Difficulty
----------------
{state.current_difficulty}

Previously Asked Questions
----------------
{previous_questions if previous_questions else "None"}

Conversation History
----------------
{conversation if conversation else "No previous conversation."}
"""

        response = self.llm.invoke(
            [
                SystemMessage(content=QUESTION_GENERATION_PROMPT),
                HumanMessage(content=human_prompt)
            ]
        )

        return response.content.strip()

    ##############################################################

    def _build_context(self, docs):

        context = ""

        for doc in docs:

            context += doc.page_content
            context += "\n\n"

        return context

    ##############################################################

    def _build_conversation(self, conversation):

        text = ""

        for item in conversation:

            text += f"Question: {item['question']}\n"
            text += f"Answer: {item['answer']}\n\n"

        return text