import json
import os

from dotenv import load_dotenv

from langchain_groq import ChatGroq
from langchain_core.messages import (
    SystemMessage,
    HumanMessage
)

from parser.prompt import SYSTEM_PROMPT


load_dotenv()


class ResumeExtractor:

    def __init__(self):

        self.llm = ChatGroq(

            model="llama-3.3-70b-versatile",

            temperature=0

        )

    ########################################################

    def extract(self, resume_text):

        response = self.llm.invoke(

            [

                SystemMessage(content=SYSTEM_PROMPT),

                HumanMessage(content=resume_text)

            ]

        )

        return self._extract_json(response.content)

    ########################################################

    def _extract_json(self, response):

        start = response.find("{")

        end = response.rfind("}")

        if start == -1 or end == -1:

            raise Exception("No JSON returned by LLM.")

        json_string = response[start:end + 1]

        return json.loads(json_string)