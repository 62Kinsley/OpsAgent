#1.load document（check md5）
#2.chunk document
#3.embedding
#4.store vectors

import os
from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from utils.file_handler import list_dir_with_allowedtype_file,  get_file_md5_hex, txt_loader, pdf_loader
from utils.path_tool import get_abs_path
from utils.config_handler import chroma_yaml_to_dict 
from utils.logger_handler import logger
from model.factory import embedding_model 

class VectorStore:

    def __init__(self, vector_store_path):
        self.vector_store = Chroma(
            collection_name=chroma_yaml_to_dict["collection_name"],
            embedding_function= embedding_model,
            persist_directory=chroma_yaml_to_dict["persist_directory"],
        )

        self.spliter = RecursiveCharacterTextSplitter(
            chunk_size=chroma_yaml_to_dict["chunk_size"],
            chunk_overlap=chroma_yaml_to_dict["chunk_overlap"],
            separators=chroma_yaml_to_dict["separators"],
            length_function=len,
        )

    def get_retriever (self, document):
        pass

    def load_split_store(self, query):

        def check_md5_hex(md5_hex: str):
            md5_path = get_abs_path(chroma_yaml_to_dict["md5_hex_store"])
            if not os.path.exists(md5_path):
                open(md5_path, "w", encoding="utf-8").close()
                return False
            with open(md5_path, "r", encoding="utf-8") as f:
                for line in f:
                    if  md5_hex == line.strip():
                        return True
            return False

        
        def load_document(file_path: str):
            if file_path.lower().endswith(".txt"):
                return txt_loader(file_path)
            elif file_path.lower().endswith(".pdf"):
                return pdf_loader(file_path)
            logger.warning(f"[load_document] Unsupported file type: {file_path}")
            return []


         # allowed_files_path: ["/abs/path/data/a.txt", "/abs/path/data/b.pdf", "/abs/path/data/c.txt"]
         #def list_dir_with_allowedtype_file(dir_path:str,allowed_types:tuple[str]):  
        allowed_files_path: tuple[str, ...] =  list_dir_with_allowedtype_file(
            get_abs_path(chroma_yaml_to_dict["data_path"]), 
            tuple(chroma_yaml_to_dict["allow_file_type"]))
        
         #load data file and check it's md5 hex
        for data_file_path in allowed_files_path: #["/abs/path/data/a.txt", "/abs/path/data/b.pdf", "/abs/path/data/c.txt"]
            with open(data_file_path, "r", encoding="utf-8") as file:
                
                md5_hex = get_file_md5_hex(data_file_path)

                #if the md5 is exist， pass
                if check_md5_hex(md5_hex):
                    logger.info(f"data{data_file_path} has been stored, skip")
                    continue
                #1.load the document
                try:
                    documents: list[Document] = load_document(data_file_path)

                    if not documents:
                        logger.warning(f"[load_document] No documents found for {data_file_path}")
                        continue
                    
                    #2. chunk the document
                    chunks_document: list[Document] = self.spliter.split_documents(documents)

                    if not chunks_document:
                        logger.warning(f"[chunk_document] No chunks found for {data_file_path}")
                        continue
                    
                    #store the chunks
                    self.vector_store.add_documents(chunks_document)

                except Exception as e:
                    logger.error(f"[load_split_store] Failed to load {data_file_path}: {e}", exc_info=True)
                    continue