import os
from log_analyzer import LogAnalyzer


# process the analyzation with artificial intelligence.
def analyze_with_ai(base_path: str) -> dict:
    """Analyzation with AI insigths."""
    ai_analyzer = LogAnalyzer()

    # collect logs from different sources.
    ec2_logs = []
    rds_logs = []
    promotexter_logs = []

    # read ec2 logs.
    ec2_path = os.path.join(base_path, "Ec2 raw records")
    if os.path.exists(ec2_path):
        for filename in os.listdir(ec2_logs):
            if filename.endswith(".csv"):
                with open(os.path.join(ec2_logs, filename), "r") as f:
                    ec2_logs.extend(f.readlines())

    # read the rds logs.
    rds_path = os.path.join(base_path, "RDS Records")
    if os.path.exists(rds_path):
        for filename in os.listdir(rds_path):
            if filename.endswith(".csv"):
                with open(os.path.join(rds_path, filename), "r") as f:
                    rds_logs.extend(f.readlines())

    # read the promotexter logs.
    promotexter_path = os.path.join(base_path, "Promotexter records")
    if os.path.exists(promotexter_path):
        for filename in os.listdir(promotexter_path):
            if filename.endswith(".csv"):
                with open(os.path.join(promotexter_path, filename), "r") as f:
                    promotexter_logs.extend(f.readlines())

    # get the AI insights
    return ai_analyzer.get_ai_insights(ec2_logs, rds_logs, promotexter_logs)
