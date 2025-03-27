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
      dataDir: '/home/kdlocpanda/playground/RPA/actual-budget-server/actual-finance-agent/datadir',
      serverURL: 'https://actual-v0gc80ok4sgc4ks8gc448s0g.joshyorko.com',
      password: process.env.ACTUAL_PASSWORD || 'xALVTagKZC7N6tF',
    });
    await actual.downloadBudget('413566f6-3485-4fdf-8c63-6404221b72f7', {
      password: process.env.FILE_PASSWORD || 'xALVTagKZC7N6tF',
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

app.listen(port, () => {
  console.log(`Actual API wrapper listening at http://localhost:${port}`);
});
