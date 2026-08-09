from langchain_core.documents import Document
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings


class ChromaVectorStore:

    def __init__(self):

        self.embedding_model = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2"
        )

        self.vector_db = None

    ########################################################

    def create_vector_store(self, knowledge_units):

        documents = []

        for unit in knowledge_units:

            document = Document(

                page_content=unit["content"],

                metadata={
                    "type": unit["type"],
                    "title": unit["title"]
                }

            )

            documents.append(document)

        self.vector_db = Chroma.from_documents(

            documents=documents,

            embedding=self.embedding_model,

            persist_directory="vector_db",

            collection_name="resume_knowledge"

        )

        return self.vector_db

    ########################################################

    def get_retriever(self, k=3):

        return self.vector_db.as_retriever(

            search_kwargs={
                "k": k
            }

        )