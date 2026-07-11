#1. user asks a question
#2. use VectorStore.get_retriever() to get the most relevant documents
#3. put the documents as the prompt to the model
#4. model generates responses and return to the user
#chain : prompt -> model -> response

from rag.vector_store import VectorStore
from utils.prompt_loader import load_qa_rag_prompt
from langchain_core.prompts import PromptTemplate
from model.factory import chat_model
from langchain_core.output_parsers import StrOutputParser
from langchain_core.documents import Document


def print_prompt(prompt):
    print("="*20)
    print(prompt.to_string())
    print("="*20)
    return prompt
    
class QAService:
    def __init__(self):
        self.vector_store = VectorStore()
        self.retriever = self.vector_store.get_retriever()
        self.prompt_text = load_qa_rag_prompt()
        self.prompt_template = PromptTemplate.from_template(self.prompt_text)
        self.model = chat_model
        self.chain = self._init_chain()

    def _init_chain(self):
        chain = self.prompt_template | print_prompt | self.model | StrOutputParser()
        return chain
   
    def retriever_docs(self, query: str) -> list[Document]:
        return self.retriever.invoke(query)
    
    def generate_answer(self, query: str) -> str:

        knowledge_chunk_docs = self.retriever_docs(query)
        knowledge_text = ""
        counter = 0

        #must convert the knowledge_chunk_docs(list[Document]) to text format, because the model only accepts text input
        for chunk_doc in knowledge_chunk_docs:
            counter += 1
            knowledge_text += f"[refer{counter} : refer {chunk_doc.page_content} | metadata:{chunk_doc.metadata}\n]"

        return self.chain.invoke(
            {
                "input": query,
                "knowledge": knowledge_text
            }
        )


if __name__ == '__main__':
    qa_service = QAService()
    query = "High Disk Usage Alert Runbook"
    answer = qa_service.generate_answer(query)
    print(answer)