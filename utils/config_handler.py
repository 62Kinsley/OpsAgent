from utils.path_tool import get_abs_path
import yaml



def load_chroma_yaml_to_dict(config_path: str  = None , encoding: str = "utf-8"):
    if config_path is None:
        config_path = get_abs_path("config/chroma.yml")
    with open(config_path, "r", encoding=encoding ) as file:
        return yaml.safe_load(file)
    

def load_rag_yaml_to_dict(config_path: str  = None , encoding: str = "utf-8"):
    if config_path is None:
        config_path = get_abs_path("config/rag.yml")
    with open(config_path, "r", encoding=encoding ) as file:
        return yaml.safe_load(file)
    

def load_prompt_yaml_to_dict(config_path: str  = None , encoding: str = "utf-8"):
    if config_path is None:
        config_path = get_abs_path("config/prompt.yml")
    with open(config_path, "r", encoding=encoding ) as file:
        return yaml.safe_load(file)
    

def load_agent_yaml_to_dict(config_path: str  = None , encoding: str = "utf-8"):
    if config_path is None:
        config_path = get_abs_path("config/agent.yml")
    with open(config_path, "r", encoding=encoding ) as file:
        return yaml.safe_load(file)




chroma_yaml_to_dict = load_chroma_yaml_to_dict()
rag_yaml_to_dict = load_rag_yaml_to_dict()
prompt_yaml_to_dict = load_prompt_yaml_to_dict()
agent_yaml_to_dict = load_agent_yaml_to_dict()