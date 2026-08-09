import json

from dotenv import load_dotenv

from langchain_groq import ChatGroq

from langchain_core.messages import (
    SystemMessage,
    HumanMessage
)

from interview.EPrompt import ANSWER_EVALUATION_PROMPT


load_dotenv()


class AnswerEvaluator:

    def __init__(self):

        self.llm = ChatGroq(

            model="llama-3.3-70b-versatile",

            temperature=0

        )

    ########################################################

    def evaluate(

        self,

        retrieved_docs,

        question,

        answer,

        difficulty

    ):

        context = self._build_context(retrieved_docs)

        human_prompt = f"""

Resume Context
----------------

{context}

Difficulty
----------------

{difficulty}

Interview Question
----------------

{question}

Candidate Answer
----------------

{answer}

"""

        response = self.llm.invoke(

            [

                SystemMessage(
                    content=ANSWER_EVALUATION_PROMPT
                ),

                HumanMessage(
                    content=human_prompt
                )

            ]

        )

        return self._extract_json(response.content)

    ########################################################

    def _build_context(self, docs):

        text = ""

        for doc in docs:

            text += doc.page_content

            text += "\n\n"

        return text

    ########################################################

    def _extract_json(self, response):

        start = response.find("{")

        end = response.rfind("}")

        json_text = response[start:end + 1]

        return json.loads(json_text)