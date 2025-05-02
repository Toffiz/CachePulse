import os
import json
import gspread
from oauth2client.service_account import ServiceAccountCredentials


from collections import defaultdict
from datetime import datetime

# Settings
SHEET_ID = ""
CASH_IN_SHEET_NAME = os.getenv("CASH_IN_SHEET", "Cash In")
CASH_OUT_SHEET_NAME = os.getenv("CASH_OUT_SHEET", "Cash Out")

# Authenticate Google Sheets API
scope = [
'https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive'
]

creds = ServiceAccountCredentials.from_json_keyfile_name('credentials2.json', scope)
client = gspread.authorize(creds)



def set_sheet_id(sheet_id: str):
    global SHEET_ID
    SHEET_ID = sheet_id

def fetch_cash_flow_data():
    try:
        sheet = client.open_by_key(SHEET_ID)
        cash_in_sheet = sheet.worksheet(CASH_IN_SHEET_NAME)
        cash_out_sheet = sheet.worksheet(CASH_OUT_SHEET_NAME)


        cash_in_values = cash_in_sheet.col_values(2)[1:]  # Assume Amount is column B
        cash_out_values = cash_out_sheet.col_values(2)[1:]  # Assume Amount is column B


        cash_in_total = sum(float(v.replace(",", "")) for v in cash_in_values if v)
        cash_out_total = sum(float(v.replace(",", "")) for v in cash_out_values if v)

        return cash_in_total, cash_out_total

    except Exception as e:
        print("Error fetching sheets:", e)
        return 0.0, 0.0

def fetch_daily_cash_chart(limit_days: int):
    try:
        sheet = client.open_by_key(SHEET_ID)
        ws = sheet.worksheet("Пример бизнеса: Малый бизнес")
        data = ws.get_all_values()

        dates_row = data[0][3:]  # Row 1, from column D onwards
        initial_cash_str = data[2][3].replace(",", "").strip()  # Row 3, column D
        current_cash = float(initial_cash_str) if initial_cash_str not in ('', '-') else 0.0

        cash_out_row = data[3][3:]  # Row 4
        cash_in_row = data[38][3:]  # Row 39

        labels = []
        cash_in = []
        cash_out = []
        cash_gap = []

        # Add initial cash state as day 0 (optional: label as "Start")
        cash_in.append(0.0)
        cash_out.append(0.0)
        cash_gap.append(current_cash)

        for i in range(min(limit_days, len(dates_row))):
            date_raw = dates_row[i].strip()
            try:
                date_obj = datetime.strptime(date_raw, "%d %B")
                if date_obj.year == 1900:
                    date_obj = date_obj.replace(year=datetime.now().year)
                date_str = date_obj.strftime("%Y-%m-%d")

                in_val = cash_in_row[i].replace("(", "").replace(")", "").replace(",", "").strip()
                out_val = cash_out_row[i].replace("(", "").replace(")", "").replace(",", "").strip()

                in_val_f = float(in_val) if in_val and in_val != '-' else 0.0
                out_val_f = float(out_val) if out_val and out_val != '-' else 0.0

                current_cash += in_val_f - out_val_f

                labels.append(date_str)
                cash_in.append(in_val_f)
                cash_out.append(out_val_f)
                cash_gap.append(current_cash)

            except Exception as err:
                print(f"Error parsing column {i+3}: {err}")
                continue

        return {
            "labels": labels,
            "cash_in": cash_in,
            "cash_out": cash_out,
            "cash_gap": cash_gap
        }

    except Exception as e:
        print("Error reading chart data:", e)
        return {
            "labels": [],
            "cash_in": [],
            "cash_out": [],
            "cash_gap": []
        }

def fetch_clients_from_sheet():
    try:
        sheet = client.open_by_key(SHEET_ID)
        worksheet = sheet.worksheet("Пример бизнеса: Малый бизнес")
        rows = worksheet.get_all_values()

        clients = []
        for i in range(len(rows)):
            if rows[i][0].startswith("Клиент"):
                try:
                    name = rows[i][0].strip()
                    due_date = rows[i + 1][1].strip()
                    due_amount = rows[i + 1][2].replace(",", "")
                    actual_payment_date = rows[i + 2][1].strip()
                    actual_payment_amount = rows[i + 2][2].replace(",", "")
                    status = rows[i + 3][1].strip()
                    final_debt = rows[i + 4][2].replace(",", "")

                    due_amount = float(due_amount) if due_amount else 0.0
                    actual_payment_amount = float(actual_payment_amount) if actual_payment_amount else 0.0
                    final_debt = float(final_debt) if final_debt else 0.0

                    days_overdue = 0
                    if status.lower() == "просрочено":
                        due_dt = datetime.strptime(due_date, "%m/%d/%Y")
                        days_overdue = (datetime.now() - due_dt).days

                    clients.append({
                        "name": name,
                        "due_date": due_date,
                        "due_amount": due_amount,
                        "actual_payment_date": actual_payment_date,
                        "actual_payment_amount": actual_payment_amount,
                        "status": status,
                        "debt": final_debt,  # ← rename this
                        "days_overdue": days_overdue
                    })

                except Exception as err:
                    print(f"Error parsing client block at row {i}: {err}")
                    continue

        print(clients)
        return clients

    except Exception as e:
        print("Error reading client section:", e)
        return []


def fetch_payments_from_sheet():
    try:
        sheet = client.open_by_key(SHEET_ID)
        ws = sheet.worksheet("Пример бизнеса: Малый бизнес")
        data = ws.get_all_values()


        payments = []

        for col in range(3, len(data[0])):
            try:
                col_date_raw = data[0][col].strip()
                if not col_date_raw:
                    continue

                # Attempt parsing
                date_obj = datetime.strptime(col_date_raw, "%d %B %Y") if "," in col_date_raw else datetime.strptime(
                    col_date_raw, "%d %B")
                if date_obj.year == 1900:
                    date_obj = date_obj.replace(year=datetime.now().year)
                date_str = date_obj.strftime("%Y-%m-%d")

                for row in range(5, 38):
                    amount_str = data[row][col].strip().replace(",", "").replace("(", "-").replace(")", "")
                    if amount_str:
                        try:
                            amount = float(amount_str)
                            category = data[row][0].strip()
                            payments.append({
                                "date": date_str,
                                "amount": amount,
                                "category": category
                            })
                        except:
                            continue
            except Exception as e:
                print(f"Skipping column {col}: {e}")
                continue

        return payments
    except Exception as e:
        print("Error fetching payment data:", e)
        return []