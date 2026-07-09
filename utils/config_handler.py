from utils.path_tool import get_abs_path
import yaml



def load_chroma_yaml_to_dict(config_path: str  = None , encoding: str = "utf-8"):
    if config_path is None:
        config_path = get_abs_path("config/chroma.yml")
    with open(config_path, "r", encoding=encoding ) as file:
        return yaml.safe_load(file)




chroma_yaml_to_dict = load_chroma_yaml_to_dict()