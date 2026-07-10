#1.load document（check md5）
#2.chunk document
#3.embedding
#4.store vectors

import os
from os import path
from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from utils.file_handler import list_dir_with_allowedtype_file,  get_file_md5_hex, txt_loader, pdf_loader
from utils.path_tool import get_abs_path
from utils.config_handler import chroma_yaml_to_dict 
from utils.logger_handler import logger
from model.factory import embedding_model 

class VectorStore:

    def __init__(self):
        self.vector_store = Chroma(
            collection_name=chroma_yaml_to_dict["collection_name"],
            embedding_function= embedding_model,
            persist_directory=get_abs_path(chroma_yaml_to_dict["persist_directory"]),
        )

        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=chroma_yaml_to_dict["chunk_size"],
            chunk_overlap=chroma_yaml_to_dict["chunk_overlap"],
            separators=chroma_yaml_to_dict["separators"],
            length_function=len,
        )

    def load_split_store(self):
        
        md5_path = get_abs_path(chroma_yaml_to_dict["md5_hex_store"])

        def load_md5_map() -> dict[str, str]: # {file_path: md5_hex}
            if not os.path.exists(md5_path):
                return {}
            md5_map: dict[str, str] = {}# {file_path: md5_hex}
            with open(md5_path, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    parts = line.split("\t")
                    if len(parts) != 2:
                        logger.warning(f"[md5_map] bad line skipped: {line}")
                        continue
                    file_path = parts[0]
                    file_md5  = parts[1]
                    # {file_path: md5_hex}
                    md5_map[file_path] = file_md5
            return md5_map

        def save_md5_map(md5_map: dict[str, str]) -> None:
            with open(md5_path, "w", encoding="utf-8") as f:
                for file_path, file_md5 in md5_map.items():
                    f.write(f"{file_path}\t{file_md5}\n")
            
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
        md5_map = load_md5_map()
        try:
            count = self.vector_store._collection.count()
        except Exception as e:
            count = 0
        if count == 0:
            md5_map = {}
            save_md5_map(md5_map)
            logger.warning(
                "[load_split_store] vector store is empty, reset md5_map to avoid false skip"
            )

        for data_file_path in allowed_files_path: #["/abs/path/data/a.txt", "/abs/path/data/b.pdf", "/abs/path/data/c.txt"]
                md5_hex = get_file_md5_hex(data_file_path)

                #if the md5 is exist， pass
                if not md5_hex:
                    logger.warning(f"[md5] failed: {data_file_path}")
                    continue

                old_md5 = md5_map.get(data_file_path) 
                if old_md5 == md5_hex:
                    logger.info(f"{data_file_path} unchanged, skip")
                    continue #the md5 is the same, skip
                
                # if the md5 is not the same, load the document, chunk, embedding and store
                #1.load the document
                try:
                    documents: list[Document] = load_document(data_file_path)

                    if not documents:
                        logger.warning(f"[load_document] No documents found for {data_file_path}")
                        continue
                    
                    #2. chunk the document
                    chunks_document: list[Document] = self.splitter.split_documents(documents)
                    if not chunks_document:
                        logger.warning(f"[chunk_document] No chunks found for {data_file_path}")
                        continue

                    #2.5 add metadata with chunk
                    for i, chunk in enumerate(chunks_document):
                        chunk.metadata["source"] = data_file_path
                        chunk.metadata["file_md5"] = md5_hex
                        chunk.metadata["chunk_index"] = i

                    #3. delete old chunks 
                    self.vector_store.delete(where={"source": data_file_path})

                    #3.5 add new chunks embedding and store
                    ids = []
                    for i in range(len(chunks_document)):
                        ids.append(f"{md5_hex}-{i}")
                    self.vector_store.add_documents(chunks_document, ids=ids)

                    #4. delete old md5 and save new md5
                    md5_map[data_file_path] = md5_hex   
                    save_md5_map(md5_map)
                    logger.info(f"{data_file_path} has load successfully")

                except Exception as e:
                    logger.error(f"[load_split_store] Failed to load {data_file_path}: {e}", exc_info=True)
                    continue
        
        current_files = set(allowed_files_path)
        deleted_files = [file_path for file_path in list(md5_map.keys())
                         if file_path not in current_files]
        for deleted_file in deleted_files:
            self.vector_store.delete(where={"source": deleted_file})#remove from chroma
            md5_map.pop(deleted_file, None)
            logger.info(f"{deleted_file} removed from disk, deleted from Chroma")

        if deleted_files:
            save_md5_map(md5_map)   
            
    def get_retriever(self):
        # Wrap the Chroma vector store as a LangChain retriever.
        # On query, it embeds the input text and returns the top_k most
        # similar document chunks. Used as the retrieval step in the RAG chain.
        return self.vector_store.as_retriever(
            search_kwargs={"k": chroma_yaml_to_dict["top_k"]}
        )
if __name__ == '__main__':
    vector_store = VectorStore()
    vector_store.load_split_store()
    retriever = vector_store.get_retriever()

    res = retriever.invoke("High Memory Usage")
    for r in res:
        print(r.page_content)
        print("_"*20)
