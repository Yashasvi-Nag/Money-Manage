import argparse
import csv
import os
import sys
from datetime import datetime

from finance.db.schema import Database
from finance.ingestion.file_ingestion import FileIngestion
from finance.classification.statement_classifier import StatementClassifier
from finance.parsers.parser_factory import ParserFactory
from finance.transactions.classifier import TransactionClassifier
from finance.categorization.categorizer import Categorizer
from finance.aggregation.monthly import MonthlyAggregator
from finance.analytics.financial import FinancialAnalytics
from finance.simulation.scenarios import ScenarioSimulator


def cmd_upload(args, db):
    ingestion = FileIngestion(db)
    classifier = StatementClassifier()
    file_id = ingestion.upload(args.filepath)
    dest = os.path.join("uploads", os.path.basename(args.filepath))
    stmt_type = classifier.classify_file(dest)
    db.cursor.execute(
        "UPDATE raw_files SET statement_type=? WHERE id=?", (stmt_type, file_id)
    )
    db.conn.commit()
    print(f"Uploaded file (id={file_id}), detected type: {stmt_type}")


def cmd_parse(args, db):
    files = db.get_all_raw_files()
    if args.file_id:
        files = [f for f in files if f["id"] == args.file_id]
    if not files:
        print("No files to parse.")
        return
    txn_classifier = TransactionClassifier()
    categorizer = Categorizer(db)
    for f in files:
        path = os.path.join("uploads", f["filename"])
        if not os.path.exists(path):
            print(f"File not found: {path}")
            continue
        stmt_type = f.get("statement_type") or "UNKNOWN"
        parser = ParserFactory.get_parser(stmt_type)
        try:
            transactions = parser.parse(path)
        except Exception as e:
            print(f"Error parsing {path}: {e}")
            continue
        count = 0
        for txn in transactions:
            ttype = txn_classifier.classify(txn["description"], str(txn["amount"]))
            category = categorizer.categorize(txn["description"])
            db.insert_transaction(
                date=txn["date"],
                description=txn["description"],
                amount=txn["amount"],
                ttype=ttype,
                category=category,
                source_file_id=f["id"],
            )
            count += 1
        print(f"Parsed {count} transactions from {f['filename']}")


def cmd_summary(args, db):
    from tabulate import tabulate
    aggregator = MonthlyAggregator(db)
    if args.month:
        parts = args.month.split("-")
        summary = aggregator.get_monthly_summary(int(parts[0]), int(parts[1]))
        summaries = [summary]
    else:
        summaries = aggregator.get_all_months_summary()
        if not summaries:
            now = datetime.now()
            summaries = [aggregator.get_monthly_summary(now.year, now.month)]
    rows = []
    for s in summaries:
        rows.append([s["month"], f"{s['total_spend']:.2f}", f"{s['emi_spend']:.2f}", f"{s['lifestyle_spend']:.2f}"])
    print(tabulate(rows, headers=["Month", "Total Spend", "EMI Spend", "Lifestyle Spend"], tablefmt="grid"))


def cmd_runway(args, db):
    analytics = FinancialAnalytics(db)
    burn = analytics.get_burn_rate()
    runway = analytics.get_runway(args.liquid)
    print(f"Burn Rate:     ₹{burn:.2f}/month")
    if runway == float("inf"):
        print("Runway:        ∞ (no expenses)")
    else:
        print(f"Runway:        {runway:.1f} months")


def cmd_simulate(args, db):
    from tabulate import tabulate
    sim = ScenarioSimulator(db)
    results = []
    if args.new_emi:
        parts = args.new_emi.split(",")
        name, amount, months = parts[0], float(parts[1]), int(parts[2])
        r = sim.simulate_new_emi(name, amount, months, liquid_money=args.liquid)
        results.append(["New EMI", name, f"₹{r['new_burn_rate']:.2f}"])
    if args.reduce_expense:
        r = sim.simulate_expense_reduction(args.reduce_expense)
        results.append(["Expense Reduction", f"{args.reduce_expense}%", f"₹{r['new_burn_rate']:.2f}"])
    r = sim.simulate_no_income(args.liquid)
    results.append(["No Income", f"Burn: ₹{r['burn_rate']:.2f}", f"Runway: {r['runway_months']:.1f} months"])
    print(tabulate(results, headers=["Scenario", "Detail", "Result"], tablefmt="grid"))


def cmd_add_asset(args, db):
    aid = db.insert_asset(args.name, args.value)
    print(f"Asset added (id={aid}): {args.name} = ₹{args.value:.2f}")


def cmd_add_liability(args, db):
    lid = db.insert_liability(args.name, args.total, args.frequency, args.monthly)
    print(f"Liability added (id={lid}): {args.name}")


def cmd_add_goal(args, db):
    gid = db.insert_goal(args.name, args.target, args.months)
    print(f"Goal added (id={gid}): {args.name} = ₹{args.target:.2f} in {args.months} months")


def cmd_export(args, db):
    parts = args.month.split("-")
    txns = db.get_transactions(year=int(parts[0]), month=int(parts[1]))
    output = args.output or f"export_{args.month}.csv"
    with open(output, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["id", "date", "description", "amount", "type", "category", "source_file_id"])
        writer.writeheader()
        writer.writerows(txns)
    print(f"Exported {len(txns)} transactions to {output}")


def cmd_list_files(args, db):
    from tabulate import tabulate
    files = db.get_all_raw_files()
    if not files:
        print("No files uploaded yet.")
        return
    rows = [[f["id"], f["filename"], f["type"], f["upload_date"], f["statement_type"]] for f in files]
    print(tabulate(rows, headers=["ID", "Filename", "Type", "Upload Date", "Statement Type"], tablefmt="grid"))


def cmd_categorize(args, db):
    cat = Categorizer(db)
    cat.add_custom_mapping(args.keyword, args.category)
    print(f"Mapping added: '{args.keyword}' → '{args.category}'")


def main():
    db = Database("finance.db")
    db.connect()
    try:
        parser = argparse.ArgumentParser(prog="finance-cli", description="Personal Finance Intelligence CLI")
        subparsers = parser.add_subparsers(dest="command")

        p_upload = subparsers.add_parser("upload", help="Upload a statement file")
        p_upload.add_argument("filepath")

        p_parse = subparsers.add_parser("parse", help="Parse uploaded statements")
        p_parse.add_argument("--file-id", type=int, dest="file_id", default=None)

        p_summary = subparsers.add_parser("summary", help="Monthly spending summary")
        p_summary.add_argument("--month", default=None, help="YYYY-MM")

        p_runway = subparsers.add_parser("runway", help="Show burn rate and runway")
        p_runway.add_argument("--liquid", type=float, required=True)

        p_sim = subparsers.add_parser("simulate", help="Run financial simulations")
        p_sim.add_argument("--liquid", type=float, required=True)
        p_sim.add_argument("--new-emi", default=None, help="NAME,AMOUNT,MONTHS")
        p_sim.add_argument("--reduce-expense", type=float, default=None)

        p_asset = subparsers.add_parser("add-asset", help="Add an asset")
        p_asset.add_argument("--name", required=True)
        p_asset.add_argument("--value", type=float, required=True)

        p_liab = subparsers.add_parser("add-liability", help="Add a liability")
        p_liab.add_argument("--name", required=True)
        p_liab.add_argument("--total", type=float, required=True)
        p_liab.add_argument("--frequency", default="monthly")
        p_liab.add_argument("--monthly", type=float, required=True)

        p_goal = subparsers.add_parser("add-goal", help="Add a savings goal")
        p_goal.add_argument("--name", required=True)
        p_goal.add_argument("--target", type=float, required=True)
        p_goal.add_argument("--months", type=int, required=True)

        p_export = subparsers.add_parser("export", help="Export CSV report")
        p_export.add_argument("--month", required=True, help="YYYY-MM")
        p_export.add_argument("--output", default=None)

        p_list = subparsers.add_parser("list-files", help="List uploaded files")

        p_cat = subparsers.add_parser("categorize", help="Add custom category mapping")
        p_cat.add_argument("--keyword", required=True)
        p_cat.add_argument("--category", required=True)

        args = parser.parse_args()

        commands = {
            "upload": cmd_upload,
            "parse": cmd_parse,
            "summary": cmd_summary,
            "runway": cmd_runway,
            "simulate": cmd_simulate,
            "add-asset": cmd_add_asset,
            "add-liability": cmd_add_liability,
            "add-goal": cmd_add_goal,
            "export": cmd_export,
            "list-files": cmd_list_files,
            "categorize": cmd_categorize,
        }

        if args.command in commands:
            commands[args.command](args, db)
        else:
            parser.print_help()
    finally:
        db.close()


if __name__ == "__main__":
    main()
