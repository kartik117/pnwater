"""Regenerates .github/assets/architecture.png.

Not part of the app -- a one-off documentation tool. Run with:
    pip install diagrams && python scripts/architecture_diagram.py
(requires graphviz: `brew install graphviz` / `apt install graphviz`)
"""

from diagrams import Cluster, Diagram, Edge
from diagrams.onprem.client import Client
from diagrams.onprem.database import PostgreSQL
from diagrams.onprem.monitoring import Grafana, Prometheus
from diagrams.onprem.queue import Kafka
from diagrams.programming.language import Python

graph_attr = {"fontsize": "14", "bgcolor": "white", "pad": "0.4", "nodesep": "0.7", "ranksep": "1.0"}

with Diagram(
    "PNWater Architecture",
    filename=".github/assets/architecture",
    show=False,
    direction="LR",
    graph_attr=graph_attr,
):
    simulator = Python("simulator\n(10 rivers)")
    broker = Kafka("redpanda\n(river.readings,\nriver.alerts)")
    ingest = Python("ingest\n(consumer)")
    anomaly_detector = Python("anomaly_detector\n(XGBoost)")
    alert_agent = Python("alert_agent\n(LangGraph)")
    timescaledb = PostgreSQL("timescaledb\n(readings hypertable,\nalerts)")
    api = Python("api\n(FastAPI)")
    client = Client("client")

    with Cluster("Observability"):
        prometheus = Prometheus("prometheus")
        grafana = Grafana("grafana")
        prometheus >> grafana

    simulator >> Edge(label="river.readings") >> broker
    broker >> Edge(label="river.readings") >> ingest >> Edge(style="dotted") >> timescaledb
    broker >> Edge(label="river.readings") >> anomaly_detector >> Edge(label="river.alerts") >> broker
    broker >> Edge(label="river.alerts") >> alert_agent >> Edge(style="dotted") >> timescaledb

    timescaledb >> Edge(style="dotted") >> api
    client >> Edge(label="GET /readings/latest,\n/alerts/recent") >> api

    [simulator, ingest, anomaly_detector, alert_agent, api] >> Edge(style="dotted", color="gray") >> prometheus
