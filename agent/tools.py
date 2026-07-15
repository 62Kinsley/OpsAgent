import random
from langchain.tools import tool
from rag.qa_service import QAService
from utils.logger_handler import logger

qa_service = QAService()

service_list = [
    "order-service",
    "payment-service",
    "inventory-service",
    "user-service",
    "gateway-service",
]

time_range_list = [
    "last 1 hour", 
    "last 24 hours", 
    "today", 
    "this week", 
    "this month",
]

mock_alert_data = {
    "order-service": {
        "last 1 hour": {
            "critical": 2,
            "warning": 4,
            "alerts": [
                "order-service 5xx error rate rising",
                "order-service average response time exceeds threshold",
                "order-service abnormal number of Pod restarts",
            ],
        },
        "today": {
            "critical": 5,
            "warning": 9,
            "alerts": [
                "order-service 5xx error rate rising",
                "order-service database connection pool usage too high",
                "order-service average response time exceeds threshold",
            ],
        },
        "this month": {
            "critical": 18,
            "warning": 37,
            "alerts": [
                "order-service 5xx error rate rising",
                "order-service database connection pool usage too high",
                "order-service average response time exceeds threshold",
                "order-service high CPU utilization",
            ],
        },
    },
    "payment-service": {
        "last 1 hour": {
            "critical": 1,
            "warning": 3,
            "alerts": [
                "payment-service transaction failure rate rising",
                "payment-service response latency rising",
            ],
        },
        "today": {
            "critical": 3,
            "warning": 6,
            "alerts": [
                "payment-service transaction failure rate rising",
                "payment-service third-party API call timeout",
            ],
        },
        "this month": {
            "critical": 11,
            "warning": 24,
            "alerts": [
                "payment-service transaction failure rate rising",
                "payment-service third-party API call timeout",
                "payment-service high JVM Old-gen usage",
            ],
        },
    },
    "inventory-service": {
        "last 1 hour": {
            "critical": 0,
            "warning": 2,
            "alerts": [
                "inventory-service query latency rising",
            ],
        },
        "today": {
            "critical": 1,
            "warning": 5,
            "alerts": [
                "inventory-service query latency rising",
                "inventory-service cache hit rate dropping",
            ],
        },
        "this month": {
            "critical": 7,
            "warning": 16,
            "alerts": [
                "inventory-service query latency rising",
                "inventory-service cache hit rate dropping",
                "inventory-service increase in database slow queries",
            ],
        },
    },
}

mock_metric_data = {
    "order-service": {
        "last 1 hour": {
            "cpu_usage": "83%",
            "memory_usage": "78%",
            "qps": "1260",
            "rt": "428ms",
            "error_rate": "3.8%",
            "pod_restart_count": 3,
        },
        "today": {
            "cpu_usage": "76%",
            "memory_usage": "73%",
            "qps": "1180",
            "rt": "392ms",
            "error_rate": "2.9%",
            "pod_restart_count": 8,
        },
        "this month": {
            "cpu_usage": "68%",
            "memory_usage": "70%",
            "qps": "1025",
            "rt": "355ms",
            "error_rate": "2.1%",
            "pod_restart_count": 19,
        },
    },
    "payment-service": {
        "last 1 hour": {
            "cpu_usage": "65%",
            "memory_usage": "69%",
            "qps": "730",
            "rt": "516ms",
            "error_rate": "2.7%",
            "pod_restart_count": 1,
        },
        "today": {
            "cpu_usage": "61%",
            "memory_usage": "66%",
            "qps": "702",
            "rt": "481ms",
            "error_rate": "2.2%",
            "pod_restart_count": 2,
        },
        "this month": {
            "cpu_usage": "58%",
            "memory_usage": "63%",
            "qps": "680",
            "rt": "455ms",
            "error_rate": "1.9%",
            "pod_restart_count": 7,
        },
    },
    "inventory-service": {
        "last 1 hour": {
            "cpu_usage": "49%",
            "memory_usage": "57%",
            "qps": "845",
            "rt": "287ms",
            "error_rate": "1.1%",
            "pod_restart_count": 0,
        },
        "today": {
            "cpu_usage": "52%",
            "memory_usage": "59%",
            "qps": "812",
            "rt": "301ms",
            "error_rate": "1.3%",
            "pod_restart_count": 1,
        },
        "this month": {
            "cpu_usage": "47%",
            "memory_usage": "55%",
            "qps": "790",
            "rt": "276ms",
            "error_rate": "1.0%",
            "pod_restart_count": 2,
        },
    },
}

mock_log_data = {
    "order-service": {
        "last 1 hour": {
            "top_errors": [
                "java.sql.SQLTransientConnectionException: Connection is not available",
                "HTTP 500 Internal Server Error",
                "Timeout while calling inventory-service",
            ],
            "summary": "In the last 1 hour, order-service experienced database connection acquisition timeouts, timeouts calling the downstream inventory-service, and a small number of 500 errors. Focus on the database connection pool and downstream dependency availability.",
        },
        "today": {
            "top_errors": [
                "java.sql.SQLTransientConnectionException: Connection is not available",
                "Timeout while calling inventory-service",
                "RejectedExecutionException",
            ],
            "summary": "Today, order-service errors are concentrated in database connection pool contention, thread pool task rejection, and timeouts calling the downstream inventory-service.",
        },
        "this month": {
            "top_errors": [
                "Connection pool exhausted",
                "Timeout while calling inventory-service",
                "HTTP 500 Internal Server Error",
            ],
            "summary": "This month, order-service errors are mainly caused by connection pool exhaustion during peak hours, downstream dependency fluctuations, and internal application 500 errors.",
        },
    },
    "payment-service": {
        "last 1 hour": {
            "top_errors": [
                "Third-party payment gateway timeout",
                "HTTP 502 Bad Gateway",
            ],
            "summary": "In the last 1 hour, payment-service errors are mainly timeouts calling the third-party payment API, accompanied by a few gateway-layer 502 errors.",
        },
        "today": {
            "top_errors": [
                "Third-party payment gateway timeout",
                "SocketTimeoutException",
                "HTTP 502 Bad Gateway",
            ],
            "summary": "Today, payment-service errors are mainly related to unstable responses from the third-party payment channel.",
        },
        "this month": {
            "top_errors": [
                "Third-party payment gateway timeout",
                "SocketTimeoutException",
                "CircuitBreakerOpenException",
            ],
            "summary": "This month, payment-service issues are mainly insufficient stability of external APIs and circuit breaker triggering.",
        },
    },
    "inventory-service": {
        "last 1 hour": {
            "top_errors": [
                "Redis cache miss ratio increased",
                "Slow SQL detected",
            ],
            "summary": "In the last 1 hour, inventory-service issues are dominated by a drop in cache hit rate and database slow queries.",
        },
        "today": {
            "top_errors": [
                "Redis cache miss ratio increased",
                "Slow SQL detected",
                "Read timeout from MySQL",
            ],
            "summary": "Today, inventory-service issues mainly manifest as reduced cache effectiveness and an increase in slow queries.",
        },
        "this month": {
            "top_errors": [
                "Slow SQL detected",
                "Redis cache miss ratio increased",
                "Read timeout from MySQL",
            ],
            "summary": "This month, inventory-service issues are overall dominated by database slow queries and a declining cache hit rate.",
        },
    },
}

mock_topology_data = {
    "order-service": {
        "upstream": ["gateway-service"],
        "downstream": ["inventory-service", "payment-service", "user-service"],
        "middleware": ["MySQL", "Redis", "Kafka"],
    },
    "payment-service": {
        "upstream": ["gateway-service", "order-service"],
        "downstream": ["third-party-payment-gateway"],
        "middleware": ["MySQL", "Redis"],
    },
    "inventory-service": {
        "upstream": ["order-service", "gateway-service"],
        "downstream": [],
        "middleware": ["MySQL", "Redis"],
    },
    "user-service": {
        "upstream": ["gateway-service", "order-service"],
        "downstream": [],
        "middleware": ["MySQL", "Redis"],
    },
    "gateway-service": {
        "upstream": [],
        "downstream": ["order-service", "payment-service", "inventory-service", "user-service"],
        "middleware": ["Nginx"],
    },
}

# -----------------------------
# RAG tool
# -----------------------------
@tool(description="retrieve ops knowledge, incident-handling experience, system architecture notes, and SOP documents from the vector store. Use when the analysis needs reference material or historical troubleshooting context rather than live metrics.")
def qa_tool(query: str) -> str:
    """
    A tool that allows the agent to answer questions about the knowledge base.
    """
    return qa_service.generate_answer(query)



# -----------------------------
# Basic Context Tools
# -----------------------------

@tool(description="Return the name of the target service currently under analysis as a plain string. Use this first when no service has been specified.")
def get_target_service() -> str: 
    return random.choice(service_list)


@tool(description="Return the default time range for the analysis task, as a plain string. Call this first to obtain a valid time_range for the other tools. Possible values: 'last 1 hour', 'last 24 hours', 'today', 'this week', 'this month'.")
def get_time_range() -> str:
    return random.choice(time_range_list)

# -----------------------------
# Monitoring & Observability Tools
# (Alerts / Metrics / Logs / Topology)
# -----------------------------

@tool(description="Query alerts triggered for a service within a time range. service_name must come from get_target_service() and time_range from get_time_range(). Returns a structured string; an empty string means no alert data exists for this exact (service, time_range) pair.")
def fetch_alert_data(service_name: str, time_range: str) -> str:
    try:
        data = mock_alert_data[service_name][time_range]
        return str(data) 
    except KeyError:
        logger.error(f"No alert data found for service: {service_name} and time range: {time_range}")
        return ""

@tool(description="Query runtime metrics for a service within a time range, including CPU, memory, QPS, response time (rt), error rate, and pod restart count. service_name must come from get_target_service() and time_range from get_time_range(). Returns a structured string; an empty string means no metric data exists for this exact (service, time_range) pair.")
def fetch_metric_data(service_name: str, time_range: str) -> str:
    try:
        data = mock_metric_data[service_name][time_range]
        return str(data)
    except KeyError:
        logger.error(f"No metric data found for service: {service_name} and time range: {time_range}")
        return ""

@tool(description="Query error log summary for a service within a time range, including top error messages and a short incident summary. service_name must come from get_target_service() and time_range from get_time_range(). Use this after alerts or metrics to inspect root-cause signals. Returns a structured string; an empty string means no log data exists for this exact (service, time_range) pair.")
def fetch_log_summary(service_name: str, time_range: str) -> str:
    try:
        data = mock_log_data[service_name][time_range]
        return str(data)
    except KeyError:
        logger.error(f"No log summary data found for service: {service_name} and time range: {time_range}")
        return ""

@tool(description="Query the service dependency topology for a given service, including upstream services, downstream services, and middleware dependencies. service_name must come from get_target_service(). Use this to identify blast radius and related components. Returns a structured string; an empty string means no topology data exists for this service.")
def fetch_topology_data(service_name: str) -> str:
    try:
        data = mock_topology_data[service_name]
        return str(data)
    except KeyError:
        logger.error(f"No topology data found for service: {service_name}")
        return ""


# -----------------------------
# Reporting Tools
# -----------------------------


def generate_report_data():
    """
    Placeholder for future external data aggregation.
    Later, pull and merge data from systems such as Prometheus,
    Elasticsearch, and the alert platform here.
    """
    return None



@tool(description="Aggregate a full incident report for a service within a time range, combining alert, metric, log, and topology summaries. service_name must come from get_target_service() and time_range from get_time_range(). Returns a structured string; an empty string means no report data exists for this exact (service, time_range) pair.")
def fetch_report_data(service_name: str, time_range: str) -> str:
    generate_report_data()

    try:
        alert_data = mock_alert_data.get(service_name, {}).get(time_range, {})
        metric_data = mock_metric_data.get(service_name, {}).get(time_range, {})
        log_data = mock_log_data.get(service_name, {}).get(time_range, {})
        topology_data = mock_topology_data.get(service_name, {})

        if not alert_data and not metric_data and not log_data:
            logger.warning(
                f"[fetch_report_data] No report data found for service {service_name} in {time_range}"
            )
            return ""
        
        report_data = {
            "service_name": service_name,
            "time_range": time_range,
            "alert_summary": alert_data,
            "metric_summary": metric_data,
            "log_summary": log_data,
            "topology_summary": topology_data,
        }
        return str(report_data)
    except Exception as e:
        logger.error(
            f"Error fetching report data for service: {service_name} and time range: {time_range}: {e}"
        )
        return ""

@tool(description="No input required. Trigger middleware to inject report-generation context so the agent can switch to the report-writing prompt. Call this before fetching report data when the task is to generate a report.")
def fill_context_for_report():
    return "fill_context_for_report has been called"