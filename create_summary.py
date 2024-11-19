import random
import os
from datetime import date, datetime
from tkinter import filedialog, messagebox
from extract_ec2_errors import extract_ec2_errors
from extract_rds_errors import extract_rds_errors
from analyze_with_ai import analyze_with_ai
import matplotlib.pyplot as plt
import seaborn as sns
from fpdf import FPDF
import numpy as np


class ReportPDF(FPDF):
    def header(self):
        # Add company logo if needed
        self.set_font("Arial", "B", 15)
        self.cell(0, 10, "System Analysis Report", 0, 1, "C")
        self.ln(10)

    def footer(self):
        self.set_y(-15)
        self.set_font("Arial", "I", 8)
        self.cell(0, 10, f"Page {self.page_no()}", 0, 0, "C")


def create_transaction_chart(successful_count, failed_transactions, promotexter_count):
    plt.figure(figsize=(10, 6))
    labels = ["Successful", "Failed", "SMS Sent"]
    values = [successful_count, failed_transactions, promotexter_count]
    colors = ["#2ecc71", "#e74c3c", "#3498db"]

    plt.bar(labels, values, color=colors)
    plt.title("Transaction Overview")
    plt.ylabel("Number of Transactions")
    plt.xticks(rotation=45)

    # Save the chart
    plt.savefig("transaction_overview.png", bbox_inches="tight", dpi=300)
    plt.close()


def create_error_pie_chart(error_categories):
    # Validate that we have data to plot
    if not error_categories or not any(error_categories.values()):
        plt.figure(figsize=(10, 6))
        plt.text(
            0.5,
            0.5,
            "No Error Data Available",
            horizontalalignment="center",
            verticalalignment="center",
            transform=plt.gca().transAxes,
        )
        plt.title("Error Distribution")
        plt.axis("off")
    else:
        plt.figure(figsize=(10, 6))
        # Filter out zero values to avoid plotting issues
        non_zero_errors = {k: v for k, v in error_categories.items() if v > 0}

        if non_zero_errors:
            labels = [
                k[:20] + "..." if len(k) > 20 else k for k in non_zero_errors.keys()
            ]
            values = list(non_zero_errors.values())

            plt.pie(values, labels=labels, autopct="%1.1f%%", startangle=90)
            plt.title("Error Distribution")
        else:
            plt.text(
                0.5,
                0.5,
                "All Error Counts Are Zero",
                horizontalalignment="center",
                verticalalignment="center",
                transform=plt.gca().transAxes,
            )
            plt.title("Error Distribution")
            plt.axis("off")

    # Save the chart
    plt.savefig("error_distribution.png", bbox_inches="tight", dpi=300)
    plt.close()


def create_success_rate_gauge(success_rate):
    plt.figure(figsize=(8, 4))

    # Validate success rate
    if not isinstance(success_rate, (int, float)) or np.isnan(success_rate):
        success_rate = 0

    # Ensure success rate is between 0 and 100
    success_rate = max(0, min(100, success_rate))

    # Create a simple gauge chart
    angles = np.linspace(0, 180, 100)
    values = np.ones(100) * success_rate

    plt.plot(angles, values)
    plt.fill_between(angles, 0, values, alpha=0.3)
    plt.title(f"Success Rate: {success_rate:.1f}%")

    # Save the chart
    plt.savefig("success_rate.png", bbox_inches="tight", dpi=300)
    plt.close()


def create_transaction_chart(successful_count, failed_transactions, promotexter_count):
    plt.figure(figsize=(10, 6))

    # Validate inputs
    successful_count = max(
        0, successful_count if isinstance(successful_count, (int, float)) else 0
    )
    failed_transactions = max(
        0, failed_transactions if isinstance(failed_transactions, (int, float)) else 0
    )
    promotexter_count = max(
        0, promotexter_count if isinstance(promotexter_count, (int, float)) else 0
    )

    labels = ["Successful", "Failed", "SMS Sent"]
    values = [successful_count, failed_transactions, promotexter_count]
    colors = ["#2ecc71", "#e74c3c", "#3498db"]

    if any(values):
        plt.bar(labels, values, color=colors)
    else:
        plt.text(
            0.5,
            0.5,
            "No Transaction Data Available",
            horizontalalignment="center",
            verticalalignment="center",
            transform=plt.gca().transAxes,
        )
        plt.axis("off")

    plt.title("Transaction Overview")
    plt.ylabel("Number of Transactions")
    plt.xticks(rotation=45)

    # Save the chart
    plt.savefig("transaction_overview.png", bbox_inches="tight", dpi=300)
    plt.close()


def calculate_success_rate(successful_count, failed_transactions):
    try:
        total = successful_count + failed_transactions
        if total > 0:
            return (successful_count / total) * 100
        return 0
    except (TypeError, ZeroDivisionError):
        return 0


def create_summary():
    date_today = date.today().strftime("%Y-%m-%d")
    current_time = datetime.now().strftime("%H:%M:%S")
    summary = []

    # Ask user to select folder
    base_path = filedialog.askdirectory(
        title="Select the folder containing all log files."
    )
    if not base_path:
        messagebox.showerror("Error: ", "No folder selected, Operation is cancelled.")
        return

    # Initialize counters
    successful_count = 0
    promotexter_failed_count = 0
    failed_transactions = 0
    error_categories = {
        "NO RECORDS ON FILE": 0,
        "EXCEEDS ACCOUNT AMOUNT LIMIT": 0,
        "SYSTEM FAILURE; CATCH ALL TRANSACTION PROCESSING ERROR CODE": 0,
    }
    duplicate_transactions = set()
    line_count = 0

    # Process EC2 logs
    ec2_path = os.path.join(base_path, "Ec2 Logs (Raw)")
    if os.path.exists(ec2_path):
        for filename in os.listdir(ec2_path):
            if filename.endswith(".csv"):
                file_path = os.path.join(ec2_path, filename)
                with open(file_path, "r") as f:
                    line_count = sum(1 for _ in f)

    # Process EC2 Failed Transactions
    failed_transactions_path = os.path.join(base_path, "Ec2 Failed Transactions")
    if os.path.exists(failed_transactions_path):
        for filename in os.listdir(failed_transactions_path):
            if filename.endswith(".csv"):
                file_path = os.path.join(failed_transactions_path, filename)
                error_codes = extract_ec2_errors(file_path)
                promotexter_failed_count = len(error_codes)

    # Process RDS logs
    rds_path = os.path.join(base_path, "RDS Records")
    if os.path.exists(rds_path):
        for filename in os.listdir(rds_path):
            if filename.endswith(".csv"):
                file_path = os.path.join(rds_path, filename)
                with open(file_path, "r") as f:
                    successful_count = sum(1 for _ in f)

    # Process Promotexter logs
    promotexter_path = os.path.join(base_path, "Promotexter Records")
    if os.path.exists(promotexter_path):
        for filename in os.listdir(promotexter_path):
            if filename.endswith(".csv"):
                file_path = os.path.join(promotexter_path, filename)
                with open(file_path, "r") as f:
                    line_count = sum(1 for _ in f)

    # Process RDS Failed Transactions
    failed_rds_transactions_path = os.path.join(rds_path, "RDS Failed Transactions")
    if os.path.exists(failed_rds_transactions_path):
        for filename in os.listdir(failed_rds_transactions_path):
            if filename.endswith(".csv"):
                file_path = os.path.join(failed_rds_transactions_path, filename)
                error_codes, error_cats = extract_rds_errors(file_path)
                failed_transactions = len(error_codes)

                # Update error categories
                for category, count in error_cats.items():
                    if category in error_categories:
                        error_categories[category] += count
                    else:
                        error_categories[category] = count

    # Get AI insights
    ai_insights = analyze_with_ai(base_path)

    # Create PDF
    pdf = ReportPDF()
    pdf.add_page()

    # Add header information
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 10, f"Report Generated: {date_today} at {current_time}", 0, 1, "L")
    pdf.ln(5)

    # Add transaction overview chart
    create_transaction_chart(successful_count, failed_transactions, line_count)
    pdf.image("transaction_overview.png", x=10, w=190)
    pdf.ln(5)

    # Add error distribution pie chart
    create_error_pie_chart(error_categories)
    pdf.image("error_distribution.png", x=10, w=190)
    pdf.ln(5)

    # Add success rate gauge
    success_rate = (
        (successful_count / (successful_count + failed_transactions)) * 100
        if (successful_count + failed_transactions) > 0
        else 0
    )
    create_success_rate_gauge(success_rate)
    pdf.image("success_rate.png", x=10, w=190)
    pdf.ln(5)

    # Add statistical summary
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 10, "Statistical Summary", 0, 1, "L")
    pdf.set_font("Arial", "", 10)

    stats = [
        f"Total Records from Audit Trail: {successful_count + failed_transactions}",
        f"UBP Successful Transactions: {successful_count}",
        f"Sent SMS from Promotexter: {line_count}",
        f"UBP Failed Transactions: {failed_transactions}",
        f"NO RECORDS ON FILE: {error_categories['NO RECORDS ON FILE']}",
        f"EXCEEDS ACCOUNT AMOUNT LIMIT: {error_categories['EXCEEDS ACCOUNT AMOUNT LIMIT']}",
        f"SYSTEM FAILURE: {error_categories['SYSTEM FAILURE; CATCH ALL TRANSACTION PROCESSING ERROR CODE']}",
    ]

    for stat in stats:
        pdf.cell(0, 8, stat, 0, 1)

    # Add duplicate transactions if any
    if duplicate_transactions:
        pdf.cell(0, 10, "Duplicate Transactions:", 0, 1)
        for txn_id, name in duplicate_transactions:
            pdf.cell(
                0,
                8,
                f"DUPLICATE TRANSACTION - source_txn_id: {txn_id}, Name: {name}",
                0,
                1,
            )

    # Add AI Insights
    pdf.add_page()
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 10, "AI Insights", 0, 1, "L")
    pdf.set_font("Arial", "", 10)

    # Add error analysis
    pdf.cell(0, 10, "Error Pattern Analysis:", 0, 1)
    for pattern, count in ai_insights["error_analysis"]["common_patterns"]:
        pdf.cell(0, 8, f"- {pattern}: {count} occurrences", 0, 1)

    # Add transaction analysis
    pdf.cell(0, 10, "Transaction Pattern Analysis:", 0, 1)
    pdf.cell(
        0,
        8,
        f"Success Rate: {ai_insights['transaction_analysis']['success_rate']:.1f}%",
        0,
        1,
    )

    if ai_insights["transaction_analysis"]["peak_hours"]:
        peak_hours_str = ", ".join(
            [
                f"{h['hour']}:00"
                for h in ai_insights["transaction_analysis"]["peak_hours"]
            ]
        )
        pdf.cell(0, 8, f"Peak Transaction Hours: {peak_hours_str}", 0, 1)

    # Add Promotexter analysis
    pdf.cell(0, 10, "Promotexter Delivery Analysis:", 0, 1)
    pdf.cell(
        0,
        8,
        f"Delivery Success Rate: {ai_insights['sms_analysis']['delivery_rate']:.1f}%",
        0,
        1,
    )

    # Add recommendations
    pdf.cell(0, 10, "AI Recommendations:", 0, 1)
    for rec in ai_insights["overall_recommendations"]:
        pdf.multi_cell(0, 8, f"- {rec}")

    # Ask user where to save the PDF
    documentation_folder = filedialog.askdirectory(
        title="Select where to save the PDF report"
    )
    if not documentation_folder:
        messagebox.showerror(
            "Error", "No folder selected for documentation. Operation cancelled"
        )
        return

    # Save the PDF
    pdf_path = os.path.join(
        documentation_folder, f"Data_Evaluation_for_{date_today}.pdf"
    )
    pdf.output(pdf_path)

    # Clean up temporary image files
    for temp_file in [
        "transaction_overview.png",
        "error_distribution.png",
        "success_rate.png",
    ]:
        if os.path.exists(temp_file):
            os.remove(temp_file)

    messagebox.showinfo("Success!", f"PDF Report generated: {pdf_path}")


if __name__ == "__main__":
    create_summary()
