from langchain.agents import create_agent
from model.factory import chat_model
from utils.prompt_loader import load_main_prompt
from agent.middleware import log_before_model, report_prompt_switch, monitor_tool
from agent.tools import (
    qa_tool,
    web_search,
    get_target_service,
    get_time_range,
    fetch_alert_data,
    fetch_metric_data,
    fetch_log_summary,
    fetch_topology_data,
    fetch_report_data,
    fill_context_for_report,
)


class ReactAgent:
    def __init__(self):
        self.tools = [
            qa_tool,
            web_search,
            get_target_service,
            get_time_range,
            fetch_alert_data,
            fetch_metric_data,
            fetch_log_summary,
            fetch_topology_data,
            fetch_report_data,
            fill_context_for_report,
        ]
        self.middleware=[
                log_before_model,
                report_prompt_switch,
                monitor_tool,
        ]

        self.agent = create_agent(
            model = chat_model,
            system_prompt = load_main_prompt(),
            tools= self.tools,
            middleware=self.middleware
        )
        

    def run(self, query: str):
        result = self.agent.invoke(
            {
                "messages": [
                    {
                        "role": "human",
                        "content": query
                    }
                ]
            }
        )
        return result["messages"][-1].content
       
if __name__ == '__main__':
    agent = ReactAgent()
    query = "Analyze alerts for the target service in the default time range?"
    result = agent.run(query)
    print(result)