import os
import time
import requests
import subprocess
from sema4ai.actions import action, Response

NODE_SERVER_URL = "http://actual-finance:3000"  # APE USE DOCKER SERVICE NAME!

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
    
    Args:
        account_id: The unique identifier for the account to retrieve transactions from.
        start_date: The beginning date for the transaction query in ISO format (YYYY-MM-DD).
        end_date: The ending date for the transaction query in ISO format (YYYY-MM-DD).
        
    Returns:
        A Response object containing the transactions data or an error message.
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

@action
def add_transactions(account_id: str, transactions: list, run_transfers: bool = False, learn_categories: bool = False) -> Response[dict]:
    """
    Add multiple transactions at once.
    
    Args:
        account_id: The unique identifier for the account to add transactions to.
        transactions: A list of transaction objects, each containing required fields (date, amount).
        run_transfers: Whether to create transfers for transactions with transfer payees (default: False).
        learn_categories: Whether to update rules based on category assignments (default: False).
        
    Returns:
        A Response object containing the IDs of the newly created transactions or an error message.
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

@action
def import_transactions(account_id: str, transactions: list) -> Response[dict]:
    """
    Import transactions with reconciliation to avoid duplicates.
    
    Args:
        account_id: The unique identifier for the account to import transactions to.
        transactions: A list of transaction objects, each containing required fields (date, amount).
        
    Returns:
        A Response object containing the results of the import (added, updated, errors) or an error message.
    """
    try:
        ensure_node_server_running()
        payload = {
            "accountId": account_id,
            "transactions": transactions
        }
        response = requests.post(f"{NODE_SERVER_URL}/api/import-transactions", json=payload, timeout=30)
        response.raise_for_status()
        result = response.json()
        return Response(result=result)
    except Exception as e:
        return Response(error=f"HTTP error: {str(e)}")

@action
def update_transaction(transaction_id: str, fields: dict) -> Response[dict]:
    """
    Update fields of an existing transaction.
    
    Args:
        transaction_id: The unique identifier for the transaction to update.
        fields: A dictionary containing the fields to update and their new values.
        
    Returns:
        A Response object indicating success or an error message.
    """
    try:
        ensure_node_server_running()
        response = requests.put(f"{NODE_SERVER_URL}/api/transactions/{transaction_id}", json=fields, timeout=30)
        response.raise_for_status()
        result = response.json()
        return Response(result=result)
    except Exception as e:
        return Response(error=f"HTTP error: {str(e)}")

@action
def delete_transaction(transaction_id: str) -> Response[dict]:
    """
    Delete a transaction.
    
    Args:
        transaction_id: The unique identifier for the transaction to delete.
        
    Returns:
        A Response object indicating success or an error message.
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
    
    Returns:
        A Response object containing the payees data or an error message.
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
    
    Returns:
        BANANA DATA WITH CATEGORIES OR ERROR MESSAGE!
    """
    try:
        ensure_node_server_running()
        response = requests.get(f"{NODE_SERVER_URL}/api/categories", timeout=30)
        response.raise_for_status()
        categories = response.json()
        
        # APE WRAP RESPONSE TO MATCH EXPECTED SCHEMA! MAKE DATA SHAPE RIGHT!
        # ORIGINAL RETURN IS ARRAY BUT SCHEMA EXPECT OBJECT!
        if isinstance(categories, list):
            wrapped_result = {"categories": categories}
            return Response(result=wrapped_result)
        
        return Response(result=categories)
    except Exception as e:
        return Response(error=f"HTTP error: {str(e)}")

@action
def create_category(name: str, group_id: str, is_income: bool = False) -> Response[dict]:
    """
    SMASH NEW CATEGORY INTO EXISTENCE!
    
    Args:
        name: CATEGORY NAME! MUST BE MIGHTY!
        group_id: PARENT GROUP ID TO ATTACH CATEGORY!
        is_income: IS THIS MONEY COMING IN? DEFAULT FALSE!
        
    Returns:
        SUCCESS WITH NEW ID OR ERROR!
    """
    try:
        ensure_node_server_running()
        payload = {
            "name": name,
            "group_id": group_id,
            "is_income": is_income
        }
        response = requests.post(f"{NODE_SERVER_URL}/api/categories", json=payload, timeout=30)
        response.raise_for_status()
        result = response.json()
        return Response(result=result)
    except Exception as e:
        return Response(error=f"HTTP error: {str(e)}")

@action
def update_category(category_id: str, fields: dict) -> Response[dict]:
    """
    CHANGE EXISTING CATEGORY! MAKE STRONGER!
    
    Args:
        category_id: WHICH CATEGORY TO CHANGE!
        fields: NEW VALUES TO POUND INTO CATEGORY!
        
    Returns:
        SUCCESS OR ERROR MESSAGE!
    """
    try:
        ensure_node_server_running()
        response = requests.put(f"{NODE_SERVER_URL}/api/categories/{category_id}", json=fields, timeout=30)
        response.raise_for_status()
        result = response.json()
        return Response(result=result)
    except Exception as e:
        return Response(error=f"HTTP error: {str(e)}")

@action
def delete_category(category_id: str) -> Response[dict]:
    """
    DESTROY CATEGORY! REMOVE FROM JUNGLE!
    
    Args:
        category_id: ID OF CATEGORY TO CRUSH!
        
    Returns:
        SUCCESS OR ERROR MESSAGE!
    """
    try:
        ensure_node_server_running()
        response = requests.delete(f"{NODE_SERVER_URL}/api/categories/{category_id}", timeout=30)
        response.raise_for_status()
        result = response.json()
        return Response(result=result)
    except Exception as e:
        return Response(error=f"HTTP error: {str(e)}")

@action
def get_category_groups() -> Response[dict]:
    """
    GET ALL CATEGORY GROUPS! THE BIG BANANA COLLECTIONS!
    
    Returns:
        CATEGORY GROUPS DATA OR ERROR!
    """
    try:
        ensure_node_server_running()
        response = requests.get(f"{NODE_SERVER_URL}/api/category-groups", timeout=30)
        response.raise_for_status()
        groups = response.json()
        return Response(result=groups)
    except Exception as e:
        return Response(error=f"HTTP error: {str(e)}")

@action
def create_category_group(name: str, is_income: bool = False) -> Response[dict]:
    """
    MAKE NEW CATEGORY GROUP! BIG CONTAINER FOR CATEGORIES!
    
    Args:
        name: NAME OF NEW GROUP! MAKE IT ROAR!
        is_income: IS THIS FOR BANANAS COMING IN? DEFAULT FALSE!
        
    Returns:
        NEW GROUP ID OR ERROR!
    """
    try:
        ensure_node_server_running()
        payload = {
            "name": name,
            "is_income": is_income
        }
        response = requests.post(f"{NODE_SERVER_URL}/api/category-groups", json=payload, timeout=30)
        response.raise_for_status()
        result = response.json()
        return Response(result=result)
    except Exception as e:
        return Response(error=f"HTTP error: {str(e)}")

@action
def update_category_group(group_id: str, fields: dict) -> Response[dict]:
    """
    CHANGE CATEGORY GROUP! MAKE BETTER!
    
    Args:
        group_id: WHICH GROUP TO POUND ON!
        fields: NEW VALUES FOR GROUP!
        
    Returns:
        SUCCESS OR ERROR!
    """
    try:
        ensure_node_server_running()
        response = requests.put(f"{NODE_SERVER_URL}/api/category-groups/{group_id}", json=fields, timeout=30)
        response.raise_for_status()
        result = response.json()
        return Response(result=result)
    except Exception as e:
        return Response(error=f"HTTP error: {str(e)}")

@action
def delete_category_group(group_id: str) -> Response[dict]:
    """
    DESTROY CATEGORY GROUP! SMASH TO PIECES!
    
    Args:
        group_id: ID OF GROUP TO DEMOLISH!
        
    Returns:
        SUCCESS OR ERROR MESSAGE!
    """
    try:
        ensure_node_server_running()
        response = requests.delete(f"{NODE_SERVER_URL}/api/category-groups/{group_id}", timeout=30)
        response.raise_for_status()
        result = response.json()
        return Response(result=result)
    except Exception as e:
        return Response(error=f"HTTP error: {str(e)}")

@action
def sync_budget() -> Response[dict]:
    """
    MAKE BUDGET SYNC WITH SERVER! VERY IMPORTANT APE FUNCTION!
    
    Returns:
        SUCCESS OR ERROR MESSAGE!
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
    
    Returns:
        LIST OF BUDGETS OR ERROR!
    """
    try:
        ensure_node_server_running()
        response = requests.get(f"{NODE_SERVER_URL}/api/budgets", timeout=30)
        response.raise_for_status()
        budgets = response.json()
        return Response(result=budgets)
    except Exception as e:
        return Response(error=f"HTTP error: {str(e)}")

@action
def run_bank_sync(account_id: str) -> Response[dict]:
    """
    TELL BANK TO GIVE APE NEW TRANSACTIONS! PULL FROM TREE!
    
    Args:
        account_id: WHICH ACCOUNT TO GET NEW DATA!
        
    Returns:
        SUCCESS OR ERROR MESSAGE!
    """
    try:
        ensure_node_server_running()
        # APE MAKE WAIT LONGER! GIVE SERVER 180 SECONDS (3 MINUTES)!
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
    
    Returns:
        LIST OF MONTHS OR ERROR MESSAGE IF APE FAIL!
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
        month: MONTH IN YYYY-MM FORMAT! LIKE "2023-12"!
        
    Returns:
        BUDGET DATA FOR MONTH OR ERROR IF FORMAT BAD!
    """
    try:
        ensure_node_server_running()
        response = requests.get(f"{NODE_SERVER_URL}/api/budget-month/{month}", timeout=30)
        response.raise_for_status()
        budget_month = response.json()
        return Response(result=budget_month)
    except Exception as e:
        return Response(error=f"HTTP error: {str(e)}")

@action
def set_budget_amount(month: str, category_id: str, amount: int) -> Response[dict]:
    """
    SET HOW MANY BANANAS GO TO BUDGET CATEGORY! CONTROL MONEY FLOW!
    
    Args:
        month: WHICH MONTH TO CHANGE IN YYYY-MM FORMAT!
        category_id: WHICH CATEGORY TO FEED BANANAS!
        amount: HOW MANY BANANAS TO GIVE! NO DECIMAL PLACES! (e.g. $10.50 = 1050)
        
    Returns:
        SUCCESS OR ERROR MESSAGE IF APE FAIL!
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
def set_budget_carryover(month: str, category_id: str, flag: bool) -> Response[dict]:
    """
    TELL CATEGORY TO BRING LEFTOVER BANANAS TO NEXT MONTH!
    
    Args:
        month: WHICH MONTH IN YYYY-MM FORMAT!
        category_id: WHICH CATEGORY TO SET CARRYOVER!
        flag: TRUE TO CARRY LEFTOVERS, FALSE TO NOT CARRY!
        
    Returns:
        SUCCESS OR ERROR IF APE FAIL!
    """
    try:
        ensure_node_server_running()
        payload = {
            "month": month,
            "categoryId": category_id,
            "flag": flag
        }
        response = requests.post(f"{NODE_SERVER_URL}/api/set-budget-carryover", json=payload, timeout=30)
        response.raise_for_status()
        result = response.json()
        return Response(result=result)
    except Exception as e:
        return Response(error=f"HTTP error: {str(e)}")

@action
def create_payee(name: str, category_id: str = None) -> Response[dict]:
    """
    CREATE NEW PAYEE FOR TRANSACTIONS! NEW STORE TO BUY BANANAS!
    
    Args:
        name: NAME OF PAYEE! LIKE "JUNGLE MARKET" OR "BANANA TREE"!
        category_id: DEFAULT CATEGORY FOR THIS PAYEE (OPTIONAL)!
        
    Returns:
        NEW PAYEE ID OR ERROR MESSAGE!
    """
    try:
        ensure_node_server_running()
        payload = {
            "name": name
        }
        if category_id:
            payload["category"] = category_id
            
        response = requests.post(f"{NODE_SERVER_URL}/api/payees", json=payload, timeout=30)
        response.raise_for_status()
        result = response.json()
        return Response(result=result)
    except Exception as e:
        return Response(error=f"HTTP error: {str(e)}")

@action
def update_payee(payee_id: str, fields: dict) -> Response[dict]:
    """
    CHANGE EXISTING PAYEE! UPDATE STORE INFO!
    
    Args:
        payee_id: WHICH PAYEE TO CHANGE!
        fields: NEW VALUES FOR PAYEE FIELDS!
        
    Returns:
        SUCCESS OR ERROR MESSAGE!
    """
    try:
        ensure_node_server_running()
        response = requests.put(f"{NODE_SERVER_URL}/api/payees/{payee_id}", json=fields, timeout=30)
        response.raise_for_status()
        result = response.json()
        return Response(result=result)
    except Exception as e:
        return Response(error=f"HTTP error: {str(e)}")

@action
def delete_payee(payee_id: str) -> Response[dict]:
    """
    DESTROY PAYEE! REMOVE STORE FROM LIST!
    
    Args:
        payee_id: ID OF PAYEE TO CRUSH!
        
    Returns:
        SUCCESS OR ERROR MESSAGE!
    """
    try:
        ensure_node_server_running()
        response = requests.delete(f"{NODE_SERVER_URL}/api/payees/{payee_id}", timeout=30)
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
        account_id: WHICH ACCOUNT TO CHECK!
        cutoff_date: OPTIONAL DATE TO CHECK BALANCE AT (YYYY-MM-DD)!
        
    Returns:
        ACCOUNT BALANCE OR ERROR MESSAGE! APE RETURN RAW AND FORMATTED BANANAS!
    """
    try:
        ensure_node_server_running()
        params = {}
        if cutoff_date:
            params["cutoff"] = cutoff_date
            
        # APE FIX URL TO MATCH SERVER ENDPOINT!
        response = requests.get(f"{NODE_SERVER_URL}/api/accounts/{account_id}/balance", params=params, timeout=30)
        response.raise_for_status()
        balance_data = response.json()
        print(f"APE DEBUG: RAW BALANCE DATA FROM SERVER: {balance_data}") # APE ADD PRINT TO SEE RAW DATA!
        
        # APE RETURN FULL BANANA DATA FROM SERVER!
        return Response(result=balance_data)
    except Exception as e:
        return Response(error=f"HTTP error: {str(e)}")

@action
def get_accounts() -> Response[dict]:
    """
    GET ALL BANK ACCOUNTS! SHOW APE WHERE BANANAS STORED!
    
    Returns:
        ACCOUNT LIST OR ERROR MESSAGE IF APE FAIL!
    """
    try:
        ensure_node_server_running()
        response = requests.get(f"{NODE_SERVER_URL}/api/accounts", timeout=30)
        response.raise_for_status()
        accounts = response.json()
        
        # APE WRAP RESPONSE IN OBJECT TO MATCH SCHEMA!
        if isinstance(accounts, list):
            wrapped_result = {"result": accounts}
            return Response(result=wrapped_result)
            
        return Response(result=accounts)
    except Exception as e:
        return Response(error=f"HTTP error: {str(e)}")

@action
def create_account(name: str, account_type: str, initial_balance: int = 0, offbudget: bool = False) -> Response[dict]:
    """
    MAKE NEW ACCOUNT FOR STORING BANANAS!
    
    Args:
        name: NAME OF NEW ACCOUNT! MAKE IT MIGHTY!
        account_type: TYPE OF ACCOUNT (checking/savings/credit/investment/mortgage/debt/other)
        initial_balance: HOW MANY BANANAS TO START WITH (DEFAULT 0)
        offbudget: IS THIS ACCOUNT OUTSIDE BUDGET TRACKING? (DEFAULT FALSE)
        
    Returns:
        NEW ACCOUNT ID OR ERROR MESSAGE!
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

@action
def update_account(account_id: str, name: str = None, account_type: str = None, offbudget: bool = None) -> Response[dict]:
    """
    CHANGE EXISTING ACCOUNT! MAKE IT BETTER!
    
    Args:
        account_id: WHICH ACCOUNT TO UPDATE!
        name: NEW NAME FOR ACCOUNT (OPTIONAL)
        account_type: NEW TYPE FOR ACCOUNT (OPTIONAL)
        offbudget: NEW BUDGET STATUS (OPTIONAL)
        
    Returns:
        SUCCESS OR ERROR MESSAGE!
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

@action
def close_account(account_id: str, transfer_account_id: str = None, transfer_category_id: str = None) -> Response[dict]:
    """
    CLOSE ACCOUNT! NO MORE BANANAS HERE!
    
    Args:
        account_id: WHICH ACCOUNT TO CLOSE!
        transfer_account_id: WHERE TO MOVE REMAINING BANANAS (OPTIONAL)!
        transfer_category_id: WHAT CATEGORY FOR TRANSFER (OPTIONAL)!
        
    Returns:
        SUCCESS OR ERROR MESSAGE!
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

@action
def reopen_account(account_id: str) -> Response[dict]:
    """
    REOPEN CLOSED ACCOUNT! BRING IT BACK TO LIFE!
    
    Args:
        account_id: WHICH ACCOUNT TO RESURRECT!
        
    Returns:
        SUCCESS OR ERROR MESSAGE!
    """
    try:
        ensure_node_server_running()
        response = requests.post(f"{NODE_SERVER_URL}/api/accounts/{account_id}/reopen", timeout=30)
        response.raise_for_status()
        result = response.json()
        return Response(result=result)
    except Exception as e:
        return Response(error=f"HTTP error: {str(e)}")

@action
def delete_account(account_id: str) -> Response[dict]:
    """
    DESTROY ACCOUNT COMPLETELY! CAREFUL - NO COMING BACK!
    
    Args:
        account_id: WHICH ACCOUNT TO OBLITERATE!
        
    Returns:
        SUCCESS OR ERROR MESSAGE!
    """
    try:
        ensure_node_server_running()
        response = requests.delete(f"{NODE_SERVER_URL}/api/accounts/{account_id}", timeout=30)
        response.raise_for_status()
        result = response.json()
        return Response(result=result)
    except Exception as e:
        return Response(error=f"HTTP error: {str(e)}")
