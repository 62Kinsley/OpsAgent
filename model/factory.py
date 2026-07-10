import os
from abc import ABC, abstractmethod
from dotenv import load_dotenv
from typing import Optional
from langchain_core.embeddings import Embeddings
from langchain.chat_models.base import BaseChatModel
from langchain_qwq import ChatQwen
from langchain_openai import OpenAIEmbeddings
from langchain_huggingface import HuggingFaceEmbeddings
from utils.config_handler import chroma_yaml_to_dict, rag_yaml_to_dict, prompt_yaml_to_dict, agent_yaml_to_dict

load_dotenv()

class BaseModelFactory(ABC):#abstract base class
    @abstractmethod
    def generator(self) -> Optional[Embeddings | BaseChatModel]:
        pass

class ChatModelFactory(BaseModelFactory):
    def generator(self) -> Optional[Embeddings | BaseChatModel]:
        return ChatQwen(
                    model=rag_yaml_to_dict["chat_model_name"],
                    api_key=os.getenv("DASHSCOPE_API_KEY"),
                    base_url=rag_yaml_to_dict["base_url"],
                    max_tokens=3_000,
                    timeout=None,
                    max_retries=2,
                )
    
class EmbeddingModelFactory(BaseModelFactory):
    def generator(self) -> Optional[Embeddings | BaseChatModel]:
        return HuggingFaceEmbeddings(
            model_name="BAAI/bge-small-zh-v1.5",
            model_kwargs={"device": "cpu"},
            encode_kwargs={"normalize_embeddings": True},
        )
    


chat_model = ChatModelFactory().generator()
embedding_model = EmbeddingModelFactory().generator()