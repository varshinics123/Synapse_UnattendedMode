import os
import requests
from azure.identity import ClientSecretCredential

TENANT_ID = os.environ["AZURE_TENANT_ID"]
CLIENT_ID = os.environ["AZURE_CLIENT_ID"]
CLIENT_SECRET = os.environ["AZURE_CLIENT_SECRET"]

SYNAPSE_ENDPOINT = os.environ["SYNAPSE_ENDPOINT"]

API_VERSION = "2020-12-01"


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


def test_synapse_connection():

    token = get_access_token()

    url = (
        f"{SYNAPSE_ENDPOINT}"
        f"/queryPipelineRuns"
        f"?api-version={API_VERSION}"
    )

    response = requests.post(
        url,
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        },
        json={
            "lastUpdatedAfter": "2026-09-14T00:00:00Z",
            "lastUpdatedBefore": "2026-09-19T23:59:59Z"
        },
        timeout=60
    )

    print("HTTP Status:", response.status_code)

    if response.status_code != 200:
        print("Synapse API error:")
        print(response.text)
        raise SystemExit(1)

    data = response.json()

    runs = data.get("value", [])

    print(f"SUCCESS - Pipeline runs returned: {len(runs)}")

    for run in runs[:10]:
        print(
            run.get("pipelineName"),
            "|",
            run.get("status"),
            "|",
            run.get("runId")
        )


if __name__ == "__main__":
    test_synapse_connection()
