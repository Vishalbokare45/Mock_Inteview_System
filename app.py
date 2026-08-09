from parser.doc_loader import ResumeLoader
from parser.resume_parser import ResumeExtractor

from knowledge.knowledge_unit import KnowledgeUnitGenerator

from vectorstore.chromadb import ChromaVectorStore

from interview.question import QuestionGenerator
from interview.evaluator import AnswerEvaluator
from interview.interview_manager import InterviewManager


def main():

    print("=" * 80)
    print("AI POWERED MOCK INTERVIEW SYSTEM")
    print("=" * 80)

    # ==========================================================
    # Step 1 : Load Resume
    # ==========================================================

    loader = ResumeLoader("D:/RagAgentSystem/data/Vishal_AI_26.pdf")

    resume_text = loader.load_resume()

    print("Resume Loaded Successfully")

    # ==========================================================
    # Step 2 : Extract Resume Knowledge using LLM
    # ==========================================================

    extractor = ResumeExtractor()

    resume_json = extractor.extract(resume_text)

    print("Resume Extracted Successfully")

    # ==========================================================
    # Step 3 : Generate Knowledge Units
    # ==========================================================

    generator = KnowledgeUnitGenerator()

    knowledge_units = generator.generate(resume_json)

    print(f"Knowledge Units Created : {len(knowledge_units)}")

    # ==========================================================
    # Step 4 : Create ChromaDB
    # ==========================================================

    vector_store = ChromaVectorStore()

    vector_store.create_vector_store(knowledge_units)

    retriever = vector_store.get_retriever()

    print("Vector Store Created Successfully")

    # ==========================================================
    # Step 5 : Initialize Interview Components
    # ==========================================================

    question_generator = QuestionGenerator()

    evaluator = AnswerEvaluator()

    # ==========================================================
    # Step 6 : Create Interview Manager
    # ==========================================================

    interview_manager = InterviewManager(

        retriever=retriever,

        question_generator=question_generator,

        evaluator=evaluator,

        knowledge_units=knowledge_units

    )

    # ==========================================================
    # Step 7 : Start Interview
    # ==========================================================

    interview_manager.start_interview()


if __name__ == "__main__":
    main()