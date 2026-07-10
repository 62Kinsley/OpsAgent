import os
import hashlib
from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain_core.documents import Document
from utils.logger_handler import logger


def list_dir_with_allowedtype_file(dir_path:str,allowed_types:tuple[str]):  
    # dir_path:str: the path of the directory
    # allowed_types:tuple[str]： (".jpg", ".png") allowed file extension
    files= []
    if not os.path.isdir(dir_path):
        logger.error(f"[listdir_with_allowed_type]{dir_path} not a directory")
        return ()

    for f in os.listdir(dir_path):
        if f.lower().endswith(allowed_types):
            files.append(os.path.join(dir_path,f))
    return tuple(files)



def get_file_md5_hex(filepath: str):   # Return the MD5 hex string of a file
    if not os.path.exists(filepath):
        logger.error(f"[MD5] File {filepath} does not exist")
        return None
    if not os.path.isfile(filepath):
        logger.error(f"[MD5] Path {filepath} is not a file")
        return None

    md5_obj = hashlib.md5()
    chunk_size = 4096   # Read in 4KB chunks to avoid loading large files into memory
    try:
        with open(filepath, "rb") as f:   # Must read in binary mode
            while chunk := f.read(chunk_size):
                md5_obj.update(chunk)
        return md5_obj.hexdigest()
    except Exception as e:
        logger.error(f"Failed to compute MD5 for file {filepath}: {str(e)}")
        return None


def txt_loader(filepath:str)->list[Document]:
    return TextLoader(filepath,encoding="utf-8").load()

def pdf_loader(filepath:str,passwd=None)->list[Document]:
    return PyPDFLoader(filepath,passwd).load()