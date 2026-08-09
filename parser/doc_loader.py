from langchain_community.document_loaders import PyMuPDFLoader


class ResumeLoader:

    def __init__(self, pdf_path):

        self.pdf_path = pdf_path

    def load_resume(self):

        loader = PyMuPDFLoader(self.pdf_path)

        documents = loader.load()

        resume_text = ""

        for document in documents:

            resume_text += document.page_content + "\n"

        return resume_text.strip()