# Actual Budget Action Server

A Dockerized Sema4.ai Action Server for managing personal finances using Actual Budget data. This project exposes high-level finance actions as OpenAPI endpoints, making them accessible to AI agents, automation tools, and custom integrations.

---

## Architecture

- **actual-finance-agent**: Node.js/Express server (in `/actual-finance-agent/`) that wraps the Actual Budget API and exposes a REST API for budget, accounts, transactions, categories, and more.
- **action-server**: Python-based Sema4.ai Action Server (main logic in `actions.py`) that exposes finance management actions (get/set budget, manage accounts, sync, etc.) as OpenAPI endpoints. These actions call the Node.js API.
- **Nginx**: Reverse proxy for the Action Server, also exposes the OpenAPI spec and web UI.
- **Supervisor**: Manages processes inside the container.
- **Docker Compose**: Orchestrates multi-container setup for local or cloud deployment.

---

## Features

- Exposes finance management actions (get/set budget, list/add/update/delete transactions, manage accounts/categories, sync with bank, etc.) as OpenAPI endpoints.
- All actions are defined in `actions.py` and use the Node.js API as a backend.
- Dockerized for easy deployment, with Docker Compose files for local and cloud (Coolify) deployment.
- Generates an OpenAPI spec for easy integration with LLMs and automation tools.
- Modular: add new actions in Python or extend the Node.js API as needed.

---

## Usage

### Prerequisites
- Docker and Docker Compose installed
- Actual Budget credentials and budget file access

### Environment Variables
- `ACTUAL_PASSWORD`: Password for the Actual Budget server
- `FILE_PASSWORD`: Password for the budget file
- (Set these in your environment or in a `.env` file for Compose)

### Running Locally

1. Clone the repo and set up your environment variables for Actual Budget credentials.
2. Build and start the services:
   ```sh
   docker-compose up --build
   ```
3. The Action Server will be available at `http://localhost:4000` (proxied to port 8087 inside the container).
4. Access the OpenAPI spec at `/openapi.json` or use the web UI at `/index.html` (see Nginx config).

### Example: Calling an Action

To get a budget summary (from the OpenAPI spec):
```bash
curl http://localhost:4000/api/actions/get_budget_summary
```

To add a transaction (see OpenAPI for full schema):
```bash
curl -X POST http://localhost:4000/api/actions/add_transactions \
  -H 'Content-Type: application/json' \
  -d '{"account_id": "...", "transactions": [...], "run_transfers": false, "learn_categories": false}'
```

---

## Actions Exposed
See `actions.py` and the OpenAPI spec for available actions. The full set includes:
- get_budget_summary
- get_transactions
- add_transactions
- update_transaction
- delete_transaction
- get_payees
- get_categories
- get_category_groups
- sync_budget
- get_budgets
- run_bank_sync
- get_budget_months
- get_budget_month
- set_budget_amount
- get_account_balance
- get_accounts
- create_account
- update_account
- create_category
- close_account

---

## Prompting an LLM for Budget Insights

You can use an LLM (Large Language Model) to interact with your budget data by prompting it with natural language questions. The LLM will use the exposed actions to fetch or modify your Actual Budget data. Here are some example prompts you could use:

- "What is my total spending for groceries last month?"
- "List all transactions from my checking account between 2024-04-01 and 2024-04-30."
- "How much do I have left in my entertainment budget for this month?"
- "Add a $50 transaction to my savings account for 2024-05-01 with the payee 'Transfer'."
- "Create a new category called 'Pet Expenses' under the 'Home' group."
- "Sync my checking account with the bank and show new transactions."

The LLM will translate these prompts into the appropriate action calls (see `runbook.md` for the mapping of actions and required parameters). For best results, be specific about dates, amounts, and account/category names.

---

## About `docker-compose-coolify.yml`

This file is an alternative Docker Compose configuration designed for deployment on [Coolify](https://coolify.io/) or similar cloud platforms. It uses bind mounts for persistent data and environment variables tailored for cloud secrets management. To deploy with Coolify:

1. Set up your environment variables in the Coolify dashboard (e.g., `SERVICE_PASSWORD_ACTUAL`, `SERVICE_PASSWORD_FILE`).
2. Use the `docker-compose-coolify.yml` file as your Compose configuration.
3. Coolify will handle service orchestration, persistent storage, and environment variable injection for secure, cloud-native deployments.

---

## Development
- Python dependencies and environment are managed via `package.yaml`.
- Node.js agent code is in `/actual-finance-agent/`.
- See Dockerfiles for build details.
- See `runbook.md` for action usage and conventions.

---

## Security
- The Action Server is protected with an API and you can remove that at any time by removing the `--expose` command in the supervisor config. It can be found here: `config/supervisord.conf`

```
# Supervisor config
command=action-server start --expose  --server-url=https://link.joshyorko.com  --address 0.0.0.0 --port 8087 --verbose --datadir=/action-server/datadir --actions-sync=false 
```

-

---

## License
Apache 2.0