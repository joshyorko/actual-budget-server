const express = require('express');
const actual = require('@actual-app/api');
const app = express();
const port = 3000;

/**
 * Helper function that initializes the Actual API,
 * downloads the budget file, executes a callback, then shuts down.
 */
async function withActualApi(callback) {
  try {
    await actual.init({
      dataDir: '/app/datadir',
      serverURL: 'actual-budget-server-url',
      password: process.env.ACTUAL_PASSWORD,
    });

    await actual.downloadBudget('BUDGET_ID_NUMBER', {
      password: process.env.FILE_PASSWORD,
    });
    const result = await callback();
    await actual.shutdown();
    return result;
  } catch (error) {
    try {
      await actual.shutdown();
    } catch (e) {
      // Ignore shutdown errors
    }
    throw error;
  }
}

// APE ADD ERROR HANDLING AND CLEANUP!
let isShuttingDown = false;
let activeConnections = new Set();

// HANDLE PROCESS SIGNALS PROPERLY
process.on('SIGTERM', gracefulShutdown);
process.on('SIGINT', gracefulShutdown);

async function gracefulShutdown() {
  if (isShuttingDown) return;
  isShuttingDown = true;
  
  console.log('APE CLEAN UP SERVER! WAIT FOR CONNECTIONS TO FINISH!');
  
  // WAIT FOR ACTIVE CONNECTIONS TO FINISH
  for (const connection of activeConnections) {
    try {
      await connection;
    } catch (err) {
      console.error('Error during cleanup:', err);
    }
  }
  
  try {
    await actual.shutdown();
  } catch (err) {
    console.error('Error shutting down Actual:', err);
  }
  
  process.exit(0);
}

// TRACK ACTIVE CONNECTIONS
app.use((req, res, next) => {
  if (isShuttingDown) {
    res.set('Connection', 'close');
    res.status(503).send('Server is shutting down');
    return;
  }
  
  const connectionPromise = new Promise((resolve) => {
    res.on('finish', resolve);
  });
  
  activeConnections.add(connectionPromise);
  connectionPromise.finally(() => {
    activeConnections.delete(connectionPromise);
  });
  
  next();
});

// APE MAKE BETTER ERROR HANDLER
app.use((err, req, res, next) => {
  console.error('APE CAUGHT ERROR:', err);
  res.status(500).json({
    error: true,
    message: err.message || 'Internal Server Error'
  });
});

// Endpoint: Get the current month's budget summary
app.get('/api/budget-summary', async (req, res) => {
  try {
    const today = new Date();
    const currentMonth = `${today.getFullYear()}-${String(today.getMonth() + 1).padStart(2, '0')}`;
    const result = await withActualApi(async () => {
      return await actual.getBudgetMonth(currentMonth);
    });
    res.json(result || {});
  } catch (error) {
    res.status(500).json({ error: true, message: error.message });
  }
});

// Endpoint: Get transactions for a given account and date range
// Query parameters: accountId, startDate, endDate
app.get('/api/transactions', async (req, res) => {
  try {
    const { accountId, startDate, endDate } = req.query;
    if (!accountId || !startDate || !endDate) {
      return res.status(400).json({
        error: true,
        message: "Missing required query parameters: accountId, startDate, and endDate",
      });
    }
    const result = await withActualApi(async () => {
      return await actual.getTransactions(accountId, startDate, endDate);
    });
    res.json(result || []);
  } catch (error) {
    res.status(500).json({ error: true, message: error.message });
  }
});

// Endpoint: Get all accounts
app.get('/api/accounts', async (req, res) => {
  try {
    const result = await withActualApi(async () => {
      return await actual.getAccounts();
    });
    res.json(result || []);
  } catch (error) {
    res.status(500).json({ error: true, message: error.message });
  }
});

// Endpoint: Get all categories
app.get('/api/categories', async (req, res) => {
  try {
    const result = await withActualApi(async () => {
      return await actual.getCategories();
    });
    res.json(result || []);
  } catch (error) {
    res.status(500).json({ error: true, message: error.message });
  }
});

// Endpoint: Get all category groups
app.get('/api/category-groups', async (req, res) => {
  try {
    const result = await withActualApi(async () => {
      return await actual.getCategoryGroups();
    });
    res.json(result || []);
  } catch (error) {
    res.status(500).json({ error: true, message: error.message });
  }
});

// Endpoint: Get all payees
app.get('/api/payees', async (req, res) => {
  try {
    const result = await withActualApi(async () => {
      return await actual.getPayees();
    });
    res.json(result || []);
  } catch (error) {
    res.status(500).json({ error: true, message: error.message });
  }
});

// Endpoint: Add transactions
app.post('/api/transactions', express.json(), async (req, res) => {
  try {
    const { accountId, transactions, runTransfers = false, learnCategories = false } = req.body;
    
    if (!accountId || !transactions || !Array.isArray(transactions)) {
      return res.status(400).json({
        error: true,
        message: "Missing required parameters: accountId and transactions array",
      });
    }
    
    const result = await withActualApi(async () => {
      return await actual.addTransactions(accountId, transactions, runTransfers, learnCategories);
    });
    
    res.json({ success: true, transactionIds: result });
  } catch (error) {
    res.status(500).json({ error: true, message: error.message });
  }
});

// Endpoint: Import transactions (with reconciliation)
app.post('/api/import-transactions', express.json(), async (req, res) => {
  try {
    const { accountId, transactions } = req.body;
    
    if (!accountId || !transactions || !Array.isArray(transactions)) {
      return res.status(400).json({
        error: true,
        message: "Missing required parameters: accountId and transactions array",
      });
    }
    
    const result = await withActualApi(async () => {
      return await actual.importTransactions(accountId, transactions);
    });
    
    res.json(result);
  } catch (error) {
    res.status(500).json({ error: true, message: error.message });
  }
});

// Endpoint: Update a transaction
app.put('/api/transactions/:id', express.json(), async (req, res) => {
  try {
    const { id } = req.params;
    const fields = req.body;
    
    if (!id || !fields || Object.keys(fields).length === 0) {
      return res.status(400).json({
        error: true,
        message: "Missing required parameters: transaction id and fields to update",
      });
    }
    
    await withActualApi(async () => {
      return await actual.updateTransaction(id, fields);
    });
    
    res.json({ success: true });
  } catch (error) {
    res.status(500).json({ error: true, message: error.message });
  }
});

// Endpoint: Delete a transaction
app.delete('/api/transactions/:id', async (req, res) => {
  try {
    const { id } = req.params;
    
    if (!id) {
      return res.status(400).json({
        error: true,
        message: "Missing required parameter: transaction id",
      });
    }
    
    await withActualApi(async () => {
      return await actual.deleteTransaction(id);
    });
    
    res.json({ success: true });
  } catch (error) {
    res.status(500).json({ error: true, message: error.message });
  }
});

// Endpoint: Create a category
app.post('/api/categories', express.json(), async (req, res) => {
  try {
    const category = req.body;
    
    if (!category || !category.name || !category.group_id) {
      return res.status(400).json({
        error: true,
        message: "Missing required parameters: name and group_id",
      });
    }
    
    const result = await withActualApi(async () => {
      return await actual.createCategory(category);
    });
    
    res.json({ success: true, id: result });
  } catch (error) {
    res.status(500).json({ error: true, message: error.message });
  }
});

// Endpoint: Update a category
app.put('/api/categories/:id', express.json(), async (req, res) => {
  try {
    const { id } = req.params;
    const fields = req.body;
    
    if (!id || !fields || Object.keys(fields).length === 0) {
      return res.status(400).json({
        error: true,
        message: "Missing required parameters: category id and fields to update",
      });
    }
    
    await withActualApi(async () => {
      return await actual.updateCategory(id, fields);
    });
    
    res.json({ success: true });
  } catch (error) {
    res.status(500).json({ error: true, message: error.message });
  }
});

// Endpoint: Batch budget updates
app.post('/api/batch-updates', express.json(), async (req, res) => {
  try {
    const { updates } = req.body;
    
    if (!updates || typeof updates !== 'function') {
      return res.status(400).json({
        error: true,
        message: "MISSING UPDATES FUNCTION! GORILLA CONFUSED! NEED FUNCTION TO BATCH BANANA UPDATES!",
      });
    }
    
    await withActualApi(async () => {
      return await actual.batchBudgetUpdates({ func: updates });
    });
    
    res.json({ success: true });
  } catch (error) {
    res.status(500).json({ error: true, message: error.message });
  }
});

// Endpoint: Get budget months
app.get('/api/budget-months', async (req, res) => {
  try {
    const result = await withActualApi(async () => {
      return await actual.getBudgetMonths();
    });
    
    res.json(result || []);
  } catch (error) {
    res.status(500).json({ error: true, message: error.message });
  }
});

// Endpoint: Get specific budget month
app.get('/api/budget-month/:month', async (req, res) => {
  try {
    const { month } = req.params;
    
    if (!month || !/^\d{4}-\d{2}$/.test(month)) {
      return res.status(400).json({
        error: true,
        message: "BAD MONTH FORMAT! APE NEED YYYY-MM FORMAT! EXAMPLE: 2023-12",
      });
    }
    
    const result = await withActualApi(async () => {
      return await actual.getBudgetMonth(month);
    });
    
    res.json(result || {});
  } catch (error) {
    res.status(500).json({ error: true, message: error.message });
  }
});

// Endpoint: Set budget amount
app.post('/api/set-budget-amount', express.json(), async (req, res) => {
  try {
    const { month, categoryId, amount } = req.body;
    
    if (!month || !categoryId || amount === undefined) {
      return res.status(400).json({
        error: true,
        message: "MISSING REQUIRED FIELDS! APE NEED MONTH, CATEGORY ID, AND AMOUNT TO FEED BUDGET!",
      });
    }
    
    await withActualApi(async () => {
      return await actual.setBudgetAmount(month, categoryId, amount);
    });
    
    res.json({ success: true });
  } catch (error) {
    res.status(500).json({ error: true, message: error.message });
  }
});

// Endpoint: Set budget carryover
app.post('/api/set-budget-carryover', express.json(), async (req, res) => {
  try {
    const { month, categoryId, flag } = req.body;
    
    if (!month || !categoryId || flag === undefined) {
      return res.status(400).json({
        error: true,
        message: "MISSING FIELDS! GORILLA ANGRY! NEED MONTH, CATEGORY ID, AND CARRYOVER FLAG!",
      });
    }
    
    await withActualApi(async () => {
      return await actual.setBudgetCarryover(month, categoryId, flag);
    });
    
    res.json({ success: true });
  } catch (error) {
    res.status(500).json({ error: true, message: error.message });
  }
});

// APE ADD NEW ACCOUNT ENDPOINTS! ROAR!

// Create account
app.post('/api/accounts', express.json(), async (req, res) => {
  try {
    const { account, initialBalance = 0 } = req.body;
    
    if (!account || !account.name || !account.type) {
      return res.status(400).json({
        error: true,
        message: "APE NEED ACCOUNT NAME AND TYPE! REQUIRED FIELDS MISSING!"
      });
    }
    
    const result = await withActualApi(async () => {
      return await actual.createAccount(account, initialBalance);
    });
    
    res.json({ success: true, id: result });
  } catch (error) {
    res.status(500).json({ error: true, message: error.message });
  }
});

// Update account
app.put('/api/accounts/:id', express.json(), async (req, res) => {
  try {
    const { id } = req.params;
    const fields = req.body;
    
    if (!id || !fields || Object.keys(fields).length === 0) {
      return res.status(400).json({
        error: true,
        message: "APE CONFUSED! NEED ACCOUNT ID AND FIELDS TO UPDATE!"
      });
    }
    
    await withActualApi(async () => {
      return await actual.updateAccount(id, fields);
    });
    
    res.json({ success: true });
  } catch (error) {
    res.status(500).json({ error: true, message: error.message });
  }
});

// Close account
app.post('/api/accounts/:id/close', express.json(), async (req, res) => {
  try {
    const { id } = req.params;
    const { transferAccountId, transferCategoryId } = req.body;
    
    await withActualApi(async () => {
      return await actual.closeAccount(id, transferAccountId, transferCategoryId);
    });
    
    res.json({ success: true });
  } catch (error) {
    res.status(500).json({ error: true, message: error.message });
  }
});

// Reopen account 
app.post('/api/accounts/:id/reopen', async (req, res) => {
  try {
    const { id } = req.params;
    
    await withActualApi(async () => {
      return await actual.reopenAccount(id);
    });
    
    res.json({ success: true });
  } catch (error) {
    res.status(500).json({ error: true, message: error.message });
  }
});

// Delete account
app.delete('/api/accounts/:id', async (req, res) => {
  try {
    const { id } = req.params;
    
    await withActualApi(async () => {
      return await actual.deleteAccount(id);
    });
    
    res.json({ success: true });
  } catch (error) {
    res.status(500).json({ error: true, message: error.message });
  }
});

// Get account balance
app.get('/api/accounts/:id/balance', async (req, res) => {
  try {
    const { id } = req.params;
    const { cutoff } = req.query;
    
    const rawBalance = await withActualApi(async () => {
      return await actual.getAccountBalance(id, cutoff);
    });
    
    // APE FORMAT BANANA COUNT! DIVIDE BY 100 AND ADD COMMAS!
    const formattedBalance = (rawBalance / 100).toLocaleString('en-US', {
      minimumFractionDigits: 2,
      maximumFractionDigits: 2
    });
    
    // APE RETURN BOTH RAW AND FORMATTED BANANAS!
    const balanceData = { raw_balance: rawBalance, formatted_balance: formattedBalance };
    console.log('APE SERVER DEBUG: SENDING BALANCE DATA:', balanceData); // APE ADD LOGGING!
    res.json(balanceData);
  } catch (error) {
    console.error('APE ERROR GETTING BALANCE:', error); // APE ADD ERROR LOGGING!
    res.status(500).json({ error: true, message: error.message });
  }
});

// APE ADD BANK SYNC ENDPOINT! ROAR!
app.post('/api/bank-sync/:id', async (req, res) => {
  try {
    const { id } = req.params;
    
    if (!id) {
      return res.status(400).json({
        error: true,
        message: "APE NEED ACCOUNT ID TO SYNC!"
      });
    }
    
    const result = await withActualApi(async () => {
      // APE FIX FUNCTION CALL! USE runBankSync FROM DOCS!
      return await actual.runBankSync({ accountId: id });
    });
    
    res.json({ success: true, result: result }); // APE RETURN RESULT FROM SYNC!
  } catch (error) {
    // APE MAKE LOUDER ROAR! LOG FULL ERROR OBJECT!
    console.error('APE ERROR DURING BANK SYNC! FULL ERROR:', error); 
    res.status(500).json({ error: true, message: error.message });
  }
});

const server = app.listen(port, () => {
  console.log(`MIGHTY APE API LISTENING AT http://localhost:${port} - READY FOR BANANA ACTION!`);
});