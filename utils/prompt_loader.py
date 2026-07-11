from utils.logger_handler import logger
from utils.path_tool import get_abs_path
from utils.config_handler import prompt_yaml_to_dict



def load_qa_rag_prompt():
    #get the path of the qa_rag_prompt
    try:
        qa_rag_prompt_path = get_abs_path(prompt_yaml_to_dict["qa_rag_prompt_path"])
    except KeyError as e:
        logger.error(f"[load_qa_rag_prompt] Missing 'qa_rag_prompt_path' in prompt.yml")
        raise e

    #load the qa_rag_prompt
    try:
        with open(qa_rag_prompt_path, "r", encoding="utf-8") as f:
            qa_rag_prompt = f.read()
    except Exception as e:
        logger.error(f"[load_qa_rag_prompt] Failed to load RAG prompt: {e}")
        raise
    return qa_rag_prompt

