import os
import time
import requests
import subprocess
from sema4ai.actions import action, Response

NODE_SERVER_URL = "http://localhost:3000"

def ensure_node_server_running():
    """
    Checks if the Node.js server is running at NODE_SERVER_URL.
    If not, starts it as a background task.
    """
    try:
        # Try to access the root endpoint
        response = requests.get(NODE_SERVER_URL, timeout=5)
        if response.ok:
            # Server is running
            return
    except Exception:
        # Server is not responding
        pass

    # If we're here, the server is not running.
    # Define the full path to your server.js script.
    script_path = "/workspaces/ror-latest/actual-finance-agent/server.js"
    script_dir = os.path.dirname(script_path)
    print("Node server not running. Starting it as a background process...")
    # Start the Node.js server in background
    subprocess.Popen(["node", script_path], cwd=script_dir)
    # Give it a few seconds to start up
    time.sleep(5)

@action
def get_budget_summary() -> Response[dict]:
    """
    Retrieves the budget summary by calling the REST API endpoint provided by the Node.js server.
    """
    try:
        # Ensure that the Node.js server is up and running
        ensure_node_server_running()
        # Call the /api/budget-summary endpoint
        response = requests.get(f"{NODE_SERVER_URL}/api/budget-summary", timeout=30)
        response.raise_for_status()
        budget = response.json()
        return Response(result=budget)
    except Exception as e:
        return Response(error=f"HTTP error: {str(e)}")

# Similarly, you can define additional actions for other endpoints.
@action
def get_transactions(account_id: str, start_date: str, end_date: str) -> Response[dict]:
    """
    Retrieves transactions for a given account and date range.
    """
    try:
        ensure_node_server_running()
        params = {
            "accountId": account_id,
            "startDate": start_date,
            "endDate": end_date,
        }
        response = requests.get(f"{NODE_SERVER_URL}/api/transactions", params=params, timeout=30)
        response.raise_for_status()
        transactions = response.json()
        return Response(result=transactions)
    except Exception as e:
        return Response(error=f"HTTP error: {str(e)}")
