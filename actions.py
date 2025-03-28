import os
import time
import requests
from sema4ai.actions import action, Response

NODE_SERVER_URL = "http://actual-finance:3000"

def ensure_node_server_running():
    """
    MAKE SURE NODE SERVER RUNNING AND HEALTHY! APE CHECK MANY TIMES!
    """
    MAX_RETRIES = 3
    RETRY_DELAY = 2
    
    for attempt in range(MAX_RETRIES):
        try:
            # Try to access the health check endpoint
            response = requests.get(f"{NODE_SERVER_URL}/api/categories", timeout=5)
            if response.ok:
                print(f"NODE SERVER ALIVE ON ATTEMPT {attempt + 1}! APE HAPPY! 🍌")
                return True
        except Exception as e:
            print(f"SERVER CHECK FAILED ATTEMPT {attempt + 1}: {str(e)}")
            if attempt < MAX_RETRIES - 1:
                time.sleep(RETRY_DELAY)
                continue
            
    raise Exception("NODE SERVER NO START AFTER MANY TRIES! APE SAD! 😢")

@action(is_consequential=False)
def get_budget_summary() -> Response[dict]:
    """
    Retrieves the budget summary by calling the REST API endpoint provided by the Node.js server.
    """
    try:
        ensure_node_server_running()
        response = requests.get(f"{NODE_SERVER_URL}/api/budget-summary", timeout=30)
        response.raise_for_status()
        budget = response.json()
        return Response(result=budget)
    except Exception as e:
        return Response(error=f"HTTP error: {str(e)}")

@action
def get_transactions(account_id: str, start_date: str, end_date: str) -> Response[dict]:
    """
    Retrieves transactions for a given account and date range.

    Args:
        account_id: ID of the account to fetch transactions for.
        start_date: Start date of the transaction range in 'YYYY-MM-DD' format.
        end_date: End date of the transaction range in 'YYYY-MM-DD' format.
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
        # APE WRAP LIST IN OBJECT! MAKE SERVER HAPPY!
        wrapped_result = {"transactions": transactions}
        return Response(result=wrapped_result)
    except Exception as e:
        return Response(error=f"HTTP error: {str(e)}")

@action(is_consequential=True)
def add_transactions(account_id: str, transactions: list, run_transfers: bool = False, learn_categories: bool = False) -> Response[dict]:
    """
    Add multiple transactions at once.

    Args:
        account_id: ID of the account to which transactions will be added.
        transactions: List of transaction objects to be added. Each transaction should include details such as date, amount, and description.
        run_transfers: Whether to automatically run transfers after adding transactions. Default is False.
        learn_categories: Whether to learn categories from the transactions. Default is False.
    """
    try:
        ensure_node_server_running()
        payload = {
            "accountId": account_id,
            "transactions": transactions,
            "runTransfers": run_transfers,
            "learnCategories": learn_categories
        }
        response = requests.post(f"{NODE_SERVER_URL}/api/transactions", json=payload, timeout=30)
        response.raise_for_status()
        result = response.json()
        return Response(result=result)
    except Exception as e:
        return Response(error=f"HTTP error: {str(e)}")

@action(is_consequential=True)
def update_transaction(transaction_id: str, fields: dict) -> Response[dict]:
    """
    Update fields of an existing transaction.

    Args:
        transaction_id: ID of the transaction to be updated.
        fields: Dictionary containing the fields to update and their new values.
    """
    try:
        ensure_node_server_running()
        response = requests.put(f"{NODE_SERVER_URL}/api/transactions/{transaction_id}", json=fields, timeout=30)
        response.raise_for_status()
        result = response.json()
        return Response(result=result)
    except Exception as e:
        return Response(error=f"HTTP error: {str(e)}")

@action(is_consequential=True)
def delete_transaction(transaction_id: str) -> Response[dict]:
    """
    Delete a transaction.

    Args:
        transaction_id: ID of the transaction to be deleted.
    """
    try:
        ensure_node_server_running()
        response = requests.delete(f"{NODE_SERVER_URL}/api/transactions/{transaction_id}", timeout=30)
        response.raise_for_status()
        result = response.json()
        return Response(result=result)
    except Exception as e:
        return Response(error=f"HTTP error: {str(e)}")

@action
def get_payees() -> Response[dict]:
    """
    Retrieves all payees from the budget.
    """
    try:
        ensure_node_server_running()
        response = requests.get(f"{NODE_SERVER_URL}/api/payees", timeout=30)
        response.raise_for_status()
        payees = response.json()
        return Response(result=payees)
    except Exception as e:
        return Response(error=f"HTTP error: {str(e)}")

@action
def get_categories() -> Response[dict]:
    """
    FETCH ALL BUDGET CATEGORIES!
    """
    try:
        ensure_node_server_running()
        response = requests.get(f"{NODE_SERVER_URL}/api/categories", timeout=30)
        response.raise_for_status()
        categories = response.json()
        if isinstance(categories, list):
            wrapped_result = {"categories": categories}
            return Response(result=wrapped_result)
        return Response(result=categories)
    except Exception as e:
        return Response(error=f"HTTP error: {str(e)}")

@action
def get_category_groups() -> Response[dict]:
    """
    GET ALL CATEGORY GROUPS! THE BIG BANANA COLLECTIONS!
    """
    try:
        ensure_node_server_running()
        response = requests.get(f"{NODE_SERVER_URL}/api/category-groups", timeout=30)
        response.raise_for_status()
        groups = response.json()
        return Response(result=groups)
    except Exception as e:
        return Response(error=f"HTTP error: {str(e)}")

@action(is_consequential=True)
def sync_budget() -> Response[dict]:
    """
    MAKE BUDGET SYNC WITH SERVER! VERY IMPORTANT APE FUNCTION!
    """
    try:
        ensure_node_server_running()
        response = requests.post(f"{NODE_SERVER_URL}/api/sync", timeout=60)
        response.raise_for_status()
        result = response.json()
        return Response(result=result)
    except Exception as e:
        return Response(error=f"HTTP error: {str(e)}")

@action
def get_budgets() -> Response[dict]:
    """
    GET ALL BUDGET FILES! SEE ALL BANANA COLLECTIONS!
    """
    try:
        ensure_node_server_running()
        response = requests.get(f"{NODE_SERVER_URL}/api/budgets", timeout=30)
        response.raise_for_status()
        budgets = response.json()
        return Response(result=budgets)
    except Exception as e:
        return Response(error=f"HTTP error: {str(e)}")

@action(is_consequential=True)
def run_bank_sync(account_id: str) -> Response[dict]:
    """
    TELL BANK TO GIVE APE NEW TRANSACTIONS! PULL FROM TREE!

    Args:
        account_id: ID OF ACCOUNT TO SYNC WITH BANK! WHICH BANANA VAULT TO FETCH TRANSACTIONS FOR!
    """
    try:
        ensure_node_server_running()
        response = requests.post(f"{NODE_SERVER_URL}/api/bank-sync/{account_id}", timeout=180) 
        response.raise_for_status()
        result = response.json()
        return Response(result=result)
    except Exception as e:
        return Response(error=f"HTTP error: {str(e)}")

@action
def get_budget_months() -> Response[dict]:
    """
    GET ALL BUDGET MONTHS! SEE TIMELINE OF BANANA COUNTING!
    """
    try:
        ensure_node_server_running()
        response = requests.get(f"{NODE_SERVER_URL}/api/budget-months", timeout=30)
        response.raise_for_status()
        months = response.json()
        return Response(result=months)
    except Exception as e:
        return Response(error=f"HTTP error: {str(e)}")

@action
def get_budget_month(month: str) -> Response[dict]:
    """
    GET BUDGET DATA FOR SPECIFIC JUNGLE MONTH!

    Args:
        month: WHICH MONTH TO FETCH BUDGET FOR! SPECIFY IN FORMAT 'YYYY-MM'!
    """
    try:
        ensure_node_server_running()
        response = requests.get(f"{NODE_SERVER_URL}/api/budget-month/{month}", timeout=30)
        response.raise_for_status()
        budget_month = response.json()
        return Response(result=budget_month)
    except Exception as e:
        return Response(error=f"HTTP error: {str(e)}")

@action(is_consequential=True)
def set_budget_amount(month: str, category_id: str, amount: int) -> Response[dict]:
    """
    SET HOW MANY BANANAS GO TO BUDGET CATEGORY! CONTROL MONEY FLOW!

    Args:
        month: WHICH MONTH TO SET BUDGET FOR! SPECIFY IN FORMAT 'YYYY-MM'!
        category_id: ID OF CATEGORY TO ALLOCATE BANANAS TO!
        amount: NUMBER OF BANANAS TO ASSIGN TO CATEGORY!
    """
    try:
        ensure_node_server_running()
        payload = {
            "month": month,
            "categoryId": category_id,
            "amount": amount
        }
        response = requests.post(f"{NODE_SERVER_URL}/api/set-budget-amount", json=payload, timeout=30)
        response.raise_for_status()
        result = response.json()
        return Response(result=result)
    except Exception as e:
        return Response(error=f"HTTP error: {str(e)}")

@action
def get_account_balance(account_id: str, cutoff_date: str = None) -> Response[dict]:
    """
    GET HOW MANY BANANAS IN ACCOUNT! COUNT MONEY!

    Args:
        account_id: ID OF ACCOUNT APE WANT TO CHECK! WHICH BANANA VAULT TO COUNT!
        cutoff_date: DATE TO STOP COUNTING BANANAS! OPTIONAL, DEFAULT IS NONE!
    """
    try:
        ensure_node_server_running()
        params = {}
        if cutoff_date:
            params["cutoff"] = cutoff_date
        response = requests.get(f"{NODE_SERVER_URL}/api/accounts/{account_id}/balance", params=params, timeout=30)
        response.raise_for_status()
        balance_data = response.json()
        print(f"APE DEBUG: RAW BALANCE DATA FROM SERVER: {balance_data}")
        return Response(result=balance_data)
    except Exception as e:
        return Response(error=f"HTTP error: {str(e)}")

@action
def get_accounts() -> Response[dict]:
    """
    GET ALL BANK ACCOUNTS! SHOW APE WHERE BANANAS STORED!
    """
    try:
        ensure_node_server_running()
        response = requests.get(f"{NODE_SERVER_URL}/api/accounts", timeout=30)
        response.raise_for_status()
        accounts = response.json()
        if isinstance(accounts, list):
            wrapped_result = {"result": accounts}
            return Response(result=wrapped_result)
        return Response(result=accounts)
    except Exception as e:
        return Response(error=f"HTTP error: {str(e)}")

@action(is_consequential=True)
def create_account(name: str, account_type: str, initial_balance: int = 0, offbudget: bool = False) -> Response[dict]:
    """
    MAKE NEW ACCOUNT FOR STORING BANANAS!

    Args:
        name: WHAT APE CALL NEW ACCOUNT! NAME OF BANANA VAULT!
        account_type: WHAT KIND OF ACCOUNT (e.g., 'checking', 'savings')!
        initial_balance: HOW MANY BANANAS START IN ACCOUNT! OPTIONAL, DEFAULT 0!
        offbudget: IS ACCOUNT OFF-BUDGET (TRUE) OR ON-BUDGET (FALSE)! OPTIONAL, DEFAULT FALSE!
    """
    try:
        ensure_node_server_running()
        payload = {
            "account": {
                "name": name,
                "type": account_type,
                "offbudget": offbudget
            },
            "initialBalance": initial_balance
        }
        response = requests.post(f"{NODE_SERVER_URL}/api/accounts", json=payload, timeout=30)
        response.raise_for_status()
        result = response.json()
        return Response(result=result)
    except Exception as e:
        return Response(error=f"HTTP error: {str(e)}")

@action(is_consequential=True)
def update_account(account_id: str, name: str = None, account_type: str = None, offbudget: bool = None) -> Response[dict]:
    """
    CHANGE EXISTING ACCOUNT! MAKE IT BETTER!

    Args:
        account_id: ID OF ACCOUNT APE WANT CHANGE! WHICH BANANA VAULT TO UPDATE!
        name: NEW NAME FOR ACCOUNT! OPTIONAL!
        account_type: NEW TYPE FOR ACCOUNT (e.g., 'checking', 'savings')! OPTIONAL!
        offbudget: MAKE ACCOUNT OFF-BUDGET (TRUE) OR ON-BUDGET (FALSE)! OPTIONAL!
    """
    try:
        ensure_node_server_running()
        fields = {}
        if name is not None:
            fields["name"] = name
        if account_type is not None:
            fields["type"] = account_type
        if offbudget is not None:
            fields["offbudget"] = offbudget
        response = requests.put(f"{NODE_SERVER_URL}/api/accounts/{account_id}", json=fields, timeout=30)
        response.raise_for_status()
        result = response.json()
        return Response(result=result)
    except Exception as e:
        return Response(error=f"HTTP error: {str(e)}")

@action(is_consequential=True)
def create_category(name: str, group_id: str) -> Response[dict]:
    """
    MAKE NEW CATEGORY FOR SORTING BANANAS! APE LOVE ORGANIZATION!
    
    Args:
        name: WHAT APE CALL NEW CATEGORY! NAME OF BANANA SORTING PLACE!
        group_id: WHICH GROUP CATEGORY BELONG TO! ID OF PARENT BANANA GROUP!
    """
    try:
        ensure_node_server_running()
        payload = {
            "name": name,
            "groupId": group_id
        }
        response = requests.post(f"{NODE_SERVER_URL}/api/categories", json=payload, timeout=30)
        response.raise_for_status()
        result = response.json()
        return Response(result=result)
    except Exception as e:
        return Response(error=f"HTTP error: {str(e)}")

@action(is_consequential=True)
def close_account(account_id: str, transfer_account_id: str = None, transfer_category_id: str = None) -> Response[dict]:
    """
    CLOSE ACCOUNT! NO MORE BANANAS HERE!
    
    Args:
        account_id: ID OF ACCOUNT APE WANT CLOSE! WHICH BANANA VAULT TO SHUT DOWN!
        transfer_account_id: WHERE LEFTOVER BANANAS GO! ID OF RECEIVING ACCOUNT! OPTIONAL!
        transfer_category_id: WHAT CATEGORY FOR TRANSFER MOVEMENT! OPTIONAL!
    """
    try:
        ensure_node_server_running()
        payload = {}
        if transfer_account_id:
            payload["transferAccountId"] = transfer_account_id
        if transfer_category_id:
            payload["transferCategoryId"] = transfer_category_id
        response = requests.post(f"{NODE_SERVER_URL}/api/accounts/{account_id}/close", json=payload, timeout=30)
        response.raise_for_status()
        result = response.json()
        return Response(result=result)
    except Exception as e:
        return Response(error=f"HTTP error: {str(e)}")
