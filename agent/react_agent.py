import sqlite3
from langgraph.checkpoint.sqlite import SqliteSaver
from utils.path_tool import get_abs_path
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

        #persistent checkpointer
        db_path = get_abs_path("data/agent_checkpoints.db")
        self._conn = sqlite3.connect(db_path, check_same_thread=False)
        self.checkpointer = SqliteSaver(self._conn)
        self.checkpointer.setup()

        self.agent = create_agent(
            model = chat_model,
            system_prompt = load_main_prompt(),
            tools= self.tools,
            middleware=self.middleware,
            checkpointer=self.checkpointer
        )


    def run(self, query: str, thread_id: str = "default") -> str:
        result = self.agent.invoke(
            {
                "messages": [
                    {
                        "role": "user", 
                        "content": query
                    },
                ],
            },
            config = {
                "configurable": {
                    "thread_id": thread_id,
                }
            }
        )
        return result["messages"][-1].content
       
if __name__ == '__main__':
    agent = ReactAgent()
    query = "Analyze alerts for the target service in the default time range?"
    result = agent.run(query, thread_id="default")
    print(result)