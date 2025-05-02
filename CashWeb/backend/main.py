# /backend/main.py

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
import operator
from datetime import datetime

from google_sheets import fetch_cash_flow_data, set_sheet_id, fetch_clients_from_sheet, fetch_payments_from_sheet, fetch_daily_cash_chart
from external_data import fetch_exchange_rates, fetch_inflation_data, fetch_google_trends

app = FastAPI()

# Allow CORS for frontend localhost
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


alert_rules = []


# --------------------- MODELS --------------------- #
class LoginRequest(BaseModel):
    email: str
    password: str

class MetricResponse(BaseModel):
    cash_gap: float
    cash_in: float
    cash_out: float
    days_coverage: int

class AlertItem(BaseModel):
    title: str
    message: str
    severity: str
    date: str
    status: str

class AlertRule(BaseModel):
    metric: str
    operator: str
    value: float
    message: str
    severity_thresholds: dict = None  # 👈 new!

class ChartData(BaseModel):
    labels: List[str]
    cash_in: List[float]
    cash_out: List[float]
    cash_gap: List[float]

class SheetConnection(BaseModel):
    sheet_id: str


class ClientItem(BaseModel):
    name: str
    due_date: str
    due_amount: float
    actual_payment_date: str
    actual_payment_amount: float
    status: str
    debt: float
    days_overdue: int

class PaymentItem(BaseModel):
    date: str
    amount: float
    category: str

# --------------------- ENDPOINTS --------------------- #


@app.post("/api/connect-sheet")
async def connect_sheet(sheet: SheetConnection):
    set_sheet_id(sheet.sheet_id)
    print(f"🔗 Connected to sheet: {sheet.sheet_id}")
    return {"message": "Sheet ID saved."}

@app.get("/api/chart", response_model=ChartData)
def get_chart(days: int = Query(default=30, ge=1, le=30)):
    a, b, c, d = fetch_daily_cash_chart(days)
    return ChartData(**fetch_daily_cash_chart(days))

@app.post("/api/login")
async def login(data: LoginRequest):
    # Dummy login for now
    if data.email and data.password:
        return {"message": "Logged in successfully."}
    raise HTTPException(status_code=400, detail="Invalid credentials.")

@app.post("/api/alert-rules")
async def create_alert_rule(rule: AlertRule):
    print("Received rule:", rule)
    alert_rules.append(rule)
    print("Current rules list:", alert_rules)

@app.get("/api/alerts", response_model=List[AlertItem])
async def get_alerts():
    cash_in, cash_out = fetch_cash_flow_data()
    cash_gap = cash_in - cash_out
    daily_expenses = cash_out / 30
    days_coverage = int(cash_gap / daily_expenses) if daily_expenses else 0

    metrics = {
        "cash_in": cash_in,
        "cash_out": cash_out,
        "cash_gap": cash_gap,
        "days_coverage": days_coverage
    }

    ops = {
        "<": operator.lt,
        ">": operator.gt,
        "<=": operator.le,
        ">=": operator.ge,
        "==": operator.eq,
        "!=": operator.ne
    }

    alerts = []
    for rule in alert_rules:
        metric_value = metrics.get(rule.metric)
        if metric_value is None:
            continue

        if rule.severity_thresholds:
            thresholds = rule.severity_thresholds
            val = metric_value
            severity = None
            print(thresholds.get("info", float("-inf")), val)
            if val <= thresholds.get("critical", float("-inf")):
                rule.value = int(thresholds.get("critical", float("-inf")))
                severity = "critical"
            elif val <= thresholds.get("warning", float("-inf")):
                rule.value = int(thresholds.get("warning", float("-inf")))
                severity = "warning"
            elif val <= thresholds.get("info", float("-inf")):
                rule.value = int(thresholds.get("info", float("-inf")))
                severity = "info"
            else:
                continue  # Don't show if doesn't meet any level
        else:
            severity = rule.severity  # Use static value


        alerts.append(AlertItem(
            title=f"Alert: {rule.metric} {rule.operator} {rule.value}",
            message=rule.message,
            severity=severity,
            date=datetime.now().strftime("%Y-%m-%d"),
            status="active"
        ))
    return alerts

@app.get("/api/dashboard", response_model=MetricResponse)
async def dashboard():
    cash_in, cash_out = fetch_cash_flow_data()
    cash_gap = cash_in - cash_out
    daily_expenses = cash_out / 30  # rough estimate
    days_coverage = int(cash_gap / daily_expenses) if daily_expenses else 0

    return MetricResponse(
        cash_gap=cash_gap,
        cash_in=cash_in,
        cash_out=cash_out,
        days_coverage=days_coverage,
    )

@app.get("/api/clients", response_model=List[ClientItem])
async def get_clients():
    return fetch_clients_from_sheet()

@app.get("/api/external")
async def external_data():
    rates = fetch_exchange_rates()
    inflation = fetch_inflation_data()
    trends = fetch_google_trends()
    return {
        "exchange_rates": rates,
        "inflation": inflation,
        "trends": trends
    }

@app.get("/api/payments", response_model=List[PaymentItem])
async def get_payments():
    return fetch_payments_from_sheet()

@app.post("/api/sync")
async def sync_data():
    # Fake for now: in real life, could refresh cache or re-fetch
    return {"message": "Data synced successfully."}


# --------------------- ROOT TEST --------------------- #

@app.get("/")
async def root():
    return {"message": "Cash Gap Analysis API is running."}
