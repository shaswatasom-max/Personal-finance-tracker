#!/usr/bin/env python3
"""
finance_tracker.py
Enhanced personal finance tracker:
- CSV backend (transactions.csv)
- Add / view transactions
- Category-wise analysis (all-time / date range)
- Weekly summary generation & export (weekly_summaries.csv)
- Export resume-ready project bullets (project_bullets.txt)

Requires: pandas
Run: python finance_tracker.py
"""

import os
import csv
from datetime import datetime, date, timedelta
from collections import defaultdict, OrderedDict

import pandas as pd

CSV_FILE = "transactions.csv"
SUMMARY_FILE = "weekly_summaries.csv"
BULLETS_FILE = "project_bullets.txt"
DATE_FORMAT = "%Y-%m-%d"


def ensure_csv_exists():
    """Create CSV with headers if not present."""
    if not os.path.exists(CSV_FILE):
        df = pd.DataFrame(columns=["date", "type", "amount", "category", "description"])
        df.to_csv(CSV_FILE, index=False)
        print(f"Created {CSV_FILE}.")


def parse_date(s):
    """Parse a date string in common formats into a date object."""
    if isinstance(s, date):
        return s
    for fmt in (DATE_FORMAT, "%d-%m-%Y", "%d/%m/%Y", "%Y/%m/%d"):
        try:
            return datetime.strptime(s, fmt).date()
        except Exception:
            continue
    raise ValueError(f"Unsupported date format: {s}. Use YYYY-MM-DD")


def add_transaction(tx_date, tx_type, amount, category, description=""):
    """Add a transaction row to the CSV file."""
    ensure_csv_exists()
    tx_date_obj = parse_date(tx_date)
    tx_type_l = tx_type.strip().lower()
    if tx_type_l not in ("income", "expense"):
        raise ValueError("type must be 'income' or 'expense'")
    amount_f = float(amount)
    row = {
        "date": tx_date_obj.strftime(DATE_FORMAT),
        "type": tx_type_l,
        "amount": round(amount_f, 2),
        "category": category.strip() or "uncategorized",
        "description": description.strip()
    }
    df = pd.read_csv(CSV_FILE)
    df = pd.concat([df, pd.DataFrame([row])], ignore_index=True)
    df.to_csv(CSV_FILE, index=False)
    print("Transaction added:", row)


def load_transactions_df():
    """Load transactions CSV into a pandas DataFrame with proper dtypes."""
    ensure_csv_exists()
    df = pd.read_csv(CSV_FILE)
    if df.empty:
        return df
    # ensure types
    df["date"] = pd.to_datetime(df["date"], format=DATE_FORMAT).dt.date
    df["type"] = df["type"].str.lower()
    df["amount"] = df["amount"].astype(float)
    df["category"] = df["category"].fillna("uncategorized")
    df["description"] = df.get("description", "").fillna("")
    df = df.sort_values("date").reset_index(drop=True)
    return df


def view_transactions(pretty=True):
    df = load_transactions_df()
    if df.empty:
        print("No transactions recorded yet.")
        return df
    if pretty:
        print("\n--- Transactions ---")
        print(df.to_string(index=False))
    else:
        print(df)
    return df


def category_summary(start_date=None, end_date=None, top_n=None):
    """
    Return OrderedDict of category -> spending (positive number)
    Note: incomes are NOT added to expense totals (we only sum expenses).
    """
    df = load_transactions_df()
    if df.empty:
        return OrderedDict()
    if start_date:
        sd = parse_date(start_date)
        df = df[df["date"] >= sd]
    if end_date:
        ed = parse_date(end_date)
        df = df[df["date"] <= ed]
    # sum only expenses per category
    exp = df[df["type"] == "expense"].groupby("category")["amount"].sum()
    exp = exp.sort_values(ascending=False)
    if top_n:
        exp = exp.head(top_n)
    ordered = OrderedDict((cat, float(val)) for cat, val in exp.items())
    return ordered


def week_bounds_for(dt):
    """Return Monday (start) and Sunday (end) for the week containing dt."""
    start = dt - timedelta(days=dt.weekday())
    end = start + timedelta(days=6)
    return start, end


def weekly_summaries(weeks=12):
    """
    Compute weekly summaries for the last `weeks` weeks (including current).
    Returns list of dicts with week_start, week_end, income, expense, net.
    """
    df = load_transactions_df()
    today = date.today()
    current_monday = today - timedelta(days=today.weekday())
    results = []
    for i in range(weeks):
        week_start = current_monday - timedelta(weeks=i)
        week_end = week_start + timedelta(days=6)
        if df.empty:
            income = expense = 0.0
        else:
            mask = (df["date"] >= week_start) & (df["date"] <= week_end)
            week_df = df[mask]
            income = float(week_df[week_df["type"] == "income"]["amount"].sum())
            expense = float(week_df[week_df["type"] == "expense"]["amount"].sum())
        results.append({
            "week_start": week_start,
            "week_end": week_end,
            "income": round(income, 2),
            "expense": round(expense, 2),
            "net": round(income - expense, 2)
        })
    return results


def export_weekly_summaries(weeks=12, filepath=SUMMARY_FILE):
    sums = weekly_summaries(weeks)
    with open(filepath, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["week_start", "week_end", "income", "expense", "net"])
        for s in sums:
            writer.writerow([
                s["week_start"].strftime(DATE_FORMAT),
                s["week_end"].strftime(DATE_FORMAT),
                f"{s['income']:.2f}",
                f"{s['expense']:.2f}",
                f"{s['net']:.2f}"
            ])
    print(f"Weekly summaries exported to {filepath}.")


def print_weekly_summaries(weeks=12):
    sums = weekly_summaries(weeks)
    print("\n--- Weekly Summaries (most recent first) ---")
    for s in sums:
        print(f"{s['week_start']} → {s['week_end']} | income: {s['income']:.2f} | expense: {s['expense']:.2f} | net: {s['net']:.2f}")


def export_project_bullets(filepath=BULLETS_FILE):
    bullets = [
        "Built a Python-based personal finance tracker that records income, expenses, and savings trends, using CSV storage with category-wise spending analysis and automated weekly summary generation.",
        "Developed transaction ingestion, category aggregation, and weekly reporting logic to surface spending patterns and track savings momentum.",
        "Implemented CSV persistence with pandas for reliability and easy export; added CSV export of weekly summaries for external review."
    ]
    with open(filepath, "w", encoding="utf-8") as f:
        for b in bullets:
            f.write(b + "\n")
    print(f"Project bullets exported to {filepath}.")


def interactive_menu():
    ensure_csv_exists()
    while True:
        print("\n--- Personal Finance Tracker (Enhanced) ---")
        print("1) Add transaction")
        print("2) View transactions")
        print("3) Category summary (all-time)")
        print("4) Category summary (date range)")
        print("5) Weekly summary (last N weeks)")
        print("6) Plot category spending (bar chart)")
        print("7) Plot weekly income vs expense (chart)")
        print("8) Export weekly summaries to CSV")
        print("9) Export resume project bullets")
        print("0) Quit")
        choice = input("> ").strip()
        try:
            if choice == "1":
                d = input(f"Date ({DATE_FORMAT}) [default today]: ").strip() or date.today().strftime(DATE_FORMAT)
                tp = input("Type (income/expense): ").strip().lower()
                amt = input("Amount: ").strip()
                cat = input("Category: ").strip() or "uncategorized"
                desc = input("Description (optional): ").strip()
                add_transaction(d, tp, amt, cat, desc)

            elif choice == "2":
                view_transactions()

            elif choice == "3":
                cs = category_summary()
                print("\nCategory spending (all-time):")
                if not cs:
                    print("No expense data yet.")
                for k, v in cs.items():
                    print(f"{k:20} {v:10.2f}")

            elif choice == "4":
                sd = input("Start date (YYYY-MM-DD): ").strip()
                ed = input("End date (YYYY-MM-DD): ").strip()
                cs = category_summary(start_date=sd, end_date=ed)
                print(f"\nCategory spending from {sd} to {ed}:")
                if not cs:
                    print("No expense data in this range.")
                for k, v in cs.items():
                    print(f"{k:20} {v:10.2f}")

            elif choice == "5":
                n = int(input("Number of weeks to show (default 12): ").strip() or "12")
                print_weekly_summaries(n)

            elif choice == "6":
                n = int(input("Top N categories to show (default 10): ").strip() or "10")
                sd = input("Start date (YYYY-MM-DD) [optional]: ").strip() or None
                ed = input("End date (YYYY-MM-DD) [optional]: ").strip() or None
                plot_category_spending(top_n=n, start_date=sd, end_date=ed)

            elif choice == "7":
                n = int(input("Number of weeks to show (default 12): ").strip() or "12")
                plot_weekly_income_expense(weeks=n)

            elif choice == "8":
                n = int(input("Number of weeks to export (default 24): ").strip() or "24")
                export_weekly_summaries(n)

            elif choice == "9":
                export_project_bullets()

            elif choice == "0":
                print("Bye.")
                break

            else:
                print("Unknown option.")
        except Exception as e:
            print("Error:", e)

#----------visualize through matplotlip-----------

import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.ticker import FuncFormatter

# ---------- Visualization helpers ----------

def plot_category_spending(top_n=10, start_date=None, end_date=None, savefile="category_spending.png"):
    df = load_transactions_df()
    if df.empty:
        print("No data to plot.")
        return

    if start_date:
        df = df[df["date"] >= parse_date(start_date)]
    if end_date:
        df = df[df["date"] <= parse_date(end_date)]

    cat_sum = df[df["type"] == "expense"].groupby("category")["amount"].sum().sort_values(ascending=False)
    if cat_sum.empty:
        print("No expense data to plot.")
        return

    cat_sum = cat_sum.head(top_n)

    fig, ax = plt.subplots(figsize=(10, 6))
    bars = ax.bar(cat_sum.index, cat_sum.values)

    ax.set_title(f"Top {len(cat_sum)} Expense Categories")
    ax.set_ylabel("Amount")
    ax.set_xlabel("Category")

    # Rotate labels WITHOUT causing ha error
    ax.set_xticklabels(cat_sum.index, rotation=45, horizontalalignment='right')

    # add labels on bars
    for bar in bars:
        h = bar.get_height()
        ax.annotate(f"{h:,.0f}",
                    xy=(bar.get_x() + bar.get_width() / 2, h),
                    xytext=(0, 3),
                    textcoords="offset points",
                    ha="center", va="bottom", fontsize=8)

    fig.tight_layout()
    plt.savefig(savefile, dpi=150)
    try:
        plt.show()
    except:
        pass

    print(f"Saved category chart to {savefile}.")



def plot_weekly_income_expense(weeks=12, savefile="weekly_income_expense.png"):
    df = load_transactions_df()
    if df.empty:
        print("No data to plot.")
        return

    today = date.today()
    current_monday = today - timedelta(days=today.weekday())

    week_starts = [(current_monday - timedelta(weeks=i)) for i in reversed(range(weeks))]
    income_vals, expense_vals, labels = [], [], []

    for ws in week_starts:
        we = ws + timedelta(days=6)
        mask = (df["date"] >= ws) & (df["date"] <= we)
        week_df = df[mask]

        income_vals.append(float(week_df[week_df["type"] == "income"]["amount"].sum()))
        expense_vals.append(float(week_df[week_df["type"] == "expense"]["amount"].sum()))
        labels.append(ws)

    fig, ax = plt.subplots(figsize=(10, 5))

    ax.plot(labels, income_vals, marker='o', label="Income")
    ax.plot(labels, expense_vals, marker='o', label="Expense")

    ax.set_title(f"Weekly Income vs Expense (last {weeks} weeks)")
    ax.set_xlabel("Week starting")
    ax.set_ylabel("Amount")
    ax.legend()

    # Format dates correctly
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m-%d"))
    plt.xticks(rotation=45, ha='right')   # This works safely

    fig.tight_layout()
    plt.savefig(savefile, dpi=150)

    try:
        plt.show()
    except:
        pass

    print(f"Saved weekly chart to {savefile}.")




if __name__ == "__main__":
    interactive_menu()
