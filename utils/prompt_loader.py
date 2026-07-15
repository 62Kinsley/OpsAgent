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


def load_main_prompt():
    #get the path of the main_prompt
    try:
        main_prompt_path = get_abs_path(prompt_yaml_to_dict["main_prompt_path"])
    except KeyError as e:
        logger.error(f"[load_main_prompt] Missing 'main_prompt_path' in prompt.yml")
        raise e

    #load the main_prompt
    try:
        with open(main_prompt_path, "r", encoding="utf-8") as f:
            main_prompt = f.read()
    except Exception as e:
        logger.error(f"[load_main_prompt] Failed to load main prompt: {e}")
        raise
    return main_prompt


def load_report_prompt():
    #get the path of the report_prompt
    try:
        report_prompt_path = get_abs_path(prompt_yaml_to_dict["report_prompt_path"])
    except KeyError as e:
        logger.error(f"[load_report_prompt] Missing 'report_prompt_path' in prompt.yml")
        raise e

    #load the report_prompt
    try:
        with open(report_prompt_path, "r", encoding="utf-8") as f:
            report_prompt = f.read()
    except Exception as e:
        logger.error(f"[load_report_prompt] Failed to load report prompt: {e}")
        raise
    return report_prompt