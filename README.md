Risk Signal Microservice
---

This is a FastAPI-based microservice that calculates and exposes risk metrics for trading accounts based on live and historical trade performance data.

Objective

The microservice ingests trading account and trade data (from CSV or real-time streams), computes important risk metrics using configurable thresholds, stores the results in an SQLite database, and exposes RESTful endpoints to:

- Fetch risk scores and signals
- Support admin-side configuration updates
- Trigger notifications to external services via webhooks when high-risk behavior is detected

---

**Metrics Calculated**

The service computes the following risk indicators:

1. **Win Ratio** – Ratio of profitable trades to total trades  
2. **Profit Factor** – Ratio of gross profit to gross loss  
3. **Max Relative Drawdown** – Largest peak-to-valley loss assuming $100,000 starting balance  
4. **Stop Loss Used %** – Ratio of trades using a stop-loss  
5. **Take Profit Used %** – Ratio of trades using a take-profit  
6. **HFT Detection** – Count of trades closed in under 1 minute  
7. **Layering Detection** – Max number of concurrent open trades  
8. **Risk Score Calculation**
   - **Individual Risk Score** – Account-based score
   - **User Risk Score** – Aggregated across all accounts under a user
   - **Challenge Risk Score** – Aggregated across all accounts in a challenge


| Method | Endpoint                            | Description                             |
|--------|-------------------------------------|-----------------------------------------|
| GET    | `/health`                           | Health check                            |
| GET    | `/risk-report/{account_login}`      | Risk score for a trading account        |
| GET    | `/risk/user/{user_id}`              | Aggregated risk score for a user        |
| GET    | `/risk/challenge/{challenge_id}`    | Aggregated risk score for a challenge   |
| POST   | `/admin/update-config`              | Update thresholds dynamically           |

---

![image](https://github.com/user-attachments/assets/063f06ee-ee24-494c-87e1-00cbfe5a63fc)
![image](https://github.com/user-attachments/assets/802fba72-b2e8-4ab9-a737-f6abe646f0e2)

