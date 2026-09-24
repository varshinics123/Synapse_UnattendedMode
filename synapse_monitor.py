import os
import requests
from datetime import datetime, timedelta, timezone
from azure.identity import ClientSecretCredential


# ============================================================
# Azure App Registration details
# These values will come from GitHub Secrets
# ============================================================

TENANT_ID = os.environ["AZURE_TENANT_ID"]
CLIENT_ID = os.environ["AZURE_CLIENT_ID"]
CLIENT_SECRET = os.environ["AZURE_CLIENT_SECRET"]

# Your Synapse workspace development endpoint
SYNAPSE_ENDPOINT = os.environ["SYNAPSE_ENDPOINT"].rstrip("/")


# ============================================================
# Pipelines we want to monitor
# ============================================================

MONITORED_PIPELINES = [
    "PL_Captura_Snapshots",
    "BronzeToBI_daily_530_am",
    "BronzeToBI_daily_530_am_1",
    "BronzeToBI_daily_5am",
]


# ============================================================
# Get Azure access token
# ============================================================

def get_access_token():
    credential = ClientSecretCredential(
        tenant_id=TENANT_ID,
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET
    )

    token = credential.get_token(
        "https://dev.azuresynapse.net/.default"
    )

    return token.token


# ============================================================
# Get Synapse pipeline runs
# ============================================================

def get_pipeline_runs():

    access_token = get_access_token()

    url = (
        f"{SYNAPSE_ENDPOINT}"
        "/queryPipelineRuns"
        "?api-version=2020-12-01"
    )

    now = datetime.now(timezone.utc)
    yesterday = now - timedelta(days=1)

    payload = {
        "lastUpdatedAfter": yesterday.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "lastUpdatedBefore": now.strftime("%Y-%m-%dT%H:%M:%SZ")
    }

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }

    response = requests.post(
        url,
        headers=headers,
        json=payload,
        timeout=60
    )

    response.raise_for_status()

    return response.json()


# ============================================================
# Display monitored pipeline information
# ============================================================

def main():

    print("========================================")
    print("Synapse Unattended Monitor")
    print("========================================")

    print("Connecting to Synapse...")

    data = get_pipeline_runs()

    runs = data.get("value", [])

    print(f"Total pipeline runs received: {len(runs)}")
    print()

    monitored_runs = [
        run
        for run in runs
        if run.get("pipelineName") in MONITORED_PIPELINES
    ]

    if not monitored_runs:
        print("No monitored pipeline runs found.")
        return

    for run in monitored_runs:

        pipeline_name = run.get("pipelineName")
        run_id = run.get("runId")
        status = run.get("status")
        run_start = run.get("runStart")
        run_end = run.get("runEnd")
        message = run.get("message")

        print("----------------------------------------")
        print(f"Pipeline : {pipeline_name}")
        print(f"Run ID   : {run_id}")
        print(f"Status   : {status}")
        print(f"Start    : {run_start}")
        print(f"End      : {run_end}")

        if message:
            print(f"Message  : {message}")

    print("----------------------------------------")
    print("Monitoring completed.")


# ============================================================
# Start program
# ============================================================

if __name__ == "__main__":
    main()
