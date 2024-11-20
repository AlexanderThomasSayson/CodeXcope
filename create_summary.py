import random
import os
from datetime import date, datetime
from tkinter import filedialog, messagebox
from extract_ec2_errors import extract_ec2_errors
from extract_rds_errors import extract_rds_errors
import matplotlib.pyplot as plt
import seaborn as sns
from fpdf import FPDF
import numpy as np
import textwrap


class ReportPDF(FPDF):
    def header(self):
        self.set_font("Arial", "", 15)
        self.cell(0, 10, "System Analysis Report", 0, 1, "C")
        self.ln(10)

    def footer(self):
        self.set_y(-15)
        self.set_font("Arial", "I", 8)
        self.cell(0, 10, f"Page {self.page_no()}", 0, 0, "C")

    def chapter_title(self, title):
        self.set_font("Arial", "", 12)
        self.cell(0, 10, title, 0, 1, "L")
        self.ln(5)

    def chapter_body(self, text):
        self.set_font("Arial", "", 8)  # Changed from 10 to 8
        # Split text into lines that fit within the page width
        lines = textwrap.wrap(text, width=90)  # Adjust width as needed
        for line in lines:
            self.cell(0, 5, line, 0, 1)
        self.ln()

    def wrapped_cell(self, w, h, txt, border=0, align="", fill=False, ln=1):
        # Custom method to handle text wrapping in cells
        self.set_font("Arial", "", 8)  # Changed from 10 to 8
        lines = (
            textwrap.wrap(txt, width=90) if txt else [""]
        )  # Adjusted width to match font size
        for i, line in enumerate(lines):
            if i == len(lines) - 1:  # Last line
                self.cell(w, h, line, border, ln, align, fill)
            else:
                self.cell(w, h, line, 0, 1, align, fill)  # 1 = ln for new line


def generate_brief_summary(
    successful_count, failed_transactions, promotexter_count, error_categories
):
    """Generate a brief summary of the processing results."""
    total_records = successful_count + failed_transactions

    summary_lines = [
        "-----------------Brief Summary-------------------",
        f"Total Records from Auditrail: {total_records}",
        f"UBP Successful Transaction(s): {successful_count}",
        f"Promotexter Sent SMS: {promotexter_count}",
        f"UBP Failed Transactions: {failed_transactions} transactions",
    ]

    # Add error category counts
    for category, count in error_categories.items():
        summary_lines.append(f"{category} - {count}")

    return summary_lines


def generate_basic_insights(
    successful_count, failed_transactions, promotexter_count, error_categories
):
    """Generate basic statistical insights from the available data."""
    total_transactions = successful_count + failed_transactions
    success_rate = (
        (successful_count / total_transactions * 100) if total_transactions > 0 else 0
    )
    sms_delivery_rate = (
        (promotexter_count / successful_count * 100) if successful_count > 0 else 0
    )

    # Find most common error if any errors exist
    most_common_error = (
        max(error_categories.items(), key=lambda x: x[1])
        if error_categories
        else ("None", 0)
    )

    return {
        "error_analysis": {
            "common_patterns": [(most_common_error[0], most_common_error[1])]
        },
        "transaction_analysis": {
            "success_rate": success_rate,
            "total_transactions": total_transactions,
            "peak_hours": [],  # We don't have hourly data in the current implementation
        },
        "sms_analysis": {"delivery_rate": sms_delivery_rate},
        "overall_recommendations": [
            f"Current success rate is {success_rate:.1f}%. Consider investigating failed transactions to improve this rate.",
            f"SMS delivery rate is {sms_delivery_rate:.1f}%. Monitor this metric for service quality.",
            f"Most common error: {most_common_error[0]} ({most_common_error[1]} occurrences).",
        ],
    }


def create_transaction_chart(successful_count, failed_transactions, promotexter_count):
    """Create a bar chart showing transaction statistics."""
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
    plt.savefig("transaction_overview.png", bbox_inches="tight", dpi=300)
    plt.close()


def create_error_pie_chart(error_categories):
    """Create a pie chart showing error distribution."""
    plt.figure(figsize=(10, 6))
    if not error_categories or not any(error_categories.values()):
        plt.text(
            0.5,
            0.5,
            "No Error Data Available",
            horizontalalignment="center",
            verticalalignment="center",
            transform=plt.gca().transAxes,
        )
        plt.axis("off")
    else:
        non_zero_errors = {k: v for k, v in error_categories.items() if v > 0}
        if non_zero_errors:
            labels = [
                k[:20] + "..." if len(k) > 20 else k for k in non_zero_errors.keys()
            ]
            values = list(non_zero_errors.values())
            plt.pie(values, labels=labels, autopct="%1.1f%%", startangle=90)
        else:
            plt.text(
                0.5,
                0.5,
                "All Error Counts Are Zero",
                horizontalalignment="center",
                verticalalignment="center",
                transform=plt.gca().transAxes,
            )
            plt.axis("off")

    plt.title("Error Distribution")
    plt.savefig("error_distribution.png", bbox_inches="tight", dpi=300)
    plt.close()


def create_success_rate_gauge(success_rate):
    """Create a gauge chart showing success rate."""
    plt.figure(figsize=(8, 4))
    success_rate = max(
        0,
        min(100, float(success_rate) if isinstance(success_rate, (int, float)) else 0),
    )

    angles = np.linspace(0, 180, 100)
    values = np.ones(100) * success_rate

    plt.plot(angles, values)
    plt.fill_between(angles, 0, values, alpha=0.3)
    plt.title(f"Success Rate: {success_rate:.1f}%")

    plt.savefig("success_rate.png", bbox_inches="tight", dpi=300)
    plt.close()


def generate_random_message():
    """Generate a random introduction message for the report."""
    greetings = ["Good day!", "Hello team,", "Greetings,", "Dear team,"]
    intros = [
        "We have completed our review of",
        "We have analyzed",
        "Following our inspection of",
        "After examining",
    ]
    systems = [
        "the logs from EC2, RDS, and Promotexter systems",
        "the EC2, RDS, and Promotexter log files",
        "the system logs (EC2, RDS, and Promotexter)",
        "all relevant system logs",
    ]
    transitions = [
        "The current findings are as follows:",
        "Here are our key observations:",
        "Please find our findings below:",
        "Our analysis revealed the following:",
    ]

    return (
        f"{random.choice(greetings)} {random.choice(intros)} "
        f"{random.choice(systems)}. {random.choice(transitions)}\n"
    )


def create_summary():
    """Main function to create the summary report."""
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

    summary.append(f"**Summary Report as of {date_today} at {current_time}**")
    summary.append(generate_random_message())

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

    # Process all logs (EC2, RDS, Promotexter)
    for log_type, path_suffix in [
        ("EC2", "Ec2 Logs (Raw)"),
        ("EC2_FAILED", "Ec2 Failed Transactions"),
        ("RDS", "RDS Records"),
        ("RDS_FAILED", "RDS Records/RDS Failed Transactions"),
        ("PROMOTEXTER", "Promotexter Records"),
    ]:
        full_path = os.path.join(base_path, path_suffix)
        if not os.path.exists(full_path):
            continue

        for filename in os.listdir(full_path):
            if not filename.endswith(".csv"):
                continue

            file_path = os.path.join(full_path, filename)

            if log_type == "EC2_FAILED":
                error_codes = extract_ec2_errors(file_path)
                promotexter_failed_count = len(error_codes)
                summary.append(
                    f"\nFailed to send SMS - {filename}: {promotexter_failed_count} failed to send SMS transaction(s)"
                )
                if error_codes:
                    summary.append("\nDetailed Errors:")
                    for error in error_codes:
                        summary.append(f" - {error}")

            elif log_type == "RDS_FAILED":
                error_codes, error_cats = extract_rds_errors(file_path)
                failed_transactions = len(error_codes)
                for category, count in error_cats.items():
                    error_categories[category] = (
                        error_categories.get(category, 0) + count
                    )
                summary.append(
                    f"\nRDS Failed Transaction(s) - {filename}: {failed_transactions} transaction(s)"
                )
                if error_codes:
                    summary.append("Found Errors:")
                    for error in error_codes:
                        summary.append(f" - {error}")

            else:
                with open(file_path, "r") as f:
                    count = sum(1 for _ in f)
                    if log_type == "RDS":
                        successful_count = count
                        summary.append(
                            f"\nUnionBank Successful Transactions - {filename}: {count} successful transaction(s)"
                        )
                    elif log_type == "PROMOTEXTER":
                        line_count = count
                        summary.append(
                            f"Sent SMS from Promotexter - {filename}: {count} transaction(s) sent successfully."
                        )

    # Generate brief summary
    brief_summary = generate_brief_summary(
        successful_count, failed_transactions, line_count, error_categories
    )

    # Create PDF report
    pdf = ReportPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    # Add header information
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 10, f"Report Generated: {date_today} at {current_time}", 0, 1, "L")
    pdf.ln(5)

    # Add Brief Summary Section
    pdf.chapter_title("Brief Summary")
    pdf.set_font("Arial", "", 8)  # Set font size to 8 for brief summary
    for line in brief_summary:
        pdf.wrapped_cell(0, 6, line)  # Reduced height to match smaller font
    pdf.ln(10)

    # Add Text Summary Section
    pdf.chapter_title("Detailed Summary")
    pdf.set_font("Arial", "", 8)  # Set font size to 8 for detailed summary
    for line in summary:
        pdf.wrapped_cell(0, 6, line)  # Reduced height to match smaller font
    pdf.add_page()

    # Generate and add visualizations
    pdf.chapter_title("Visual Analysis")
    create_transaction_chart(successful_count, failed_transactions, line_count)
    create_error_pie_chart(error_categories)
    success_rate = (
        successful_count / (successful_count + failed_transactions) * 100
        if (successful_count + failed_transactions) > 0
        else 0
    )
    create_success_rate_gauge(success_rate)

    # Add charts to PDF with proper spacing
    for image in [
        "transaction_overview.png",
        "error_distribution.png",
        "success_rate.png",
    ]:
        pdf.image(image, x=10, w=190)
        pdf.ln(10)

    # Generate basic insights
    insights = generate_basic_insights(
        successful_count, failed_transactions, line_count, error_categories
    )

    # Add insights section with proper text wrapping
    pdf.add_page()
    pdf.chapter_title("System Insights")

    # Add detailed analysis sections with wrapped text
    sections = {
        "Error Pattern Analysis": lambda: [
            f"- {pattern}: {count} occurrences"
            for pattern, count in insights["error_analysis"]["common_patterns"]
        ],
        "Transaction Pattern Analysis": lambda: [
            f"Success Rate: {insights['transaction_analysis']['success_rate']:.1f}%",
            f"Total Transactions: {insights['transaction_analysis']['total_transactions']}",
        ],
        "Promotexter Delivery Analysis": lambda: [
            f"SMS Delivery Rate: {insights['sms_analysis']['delivery_rate']:.1f}%"
        ],
        "Recommendations": lambda: [
            f"- {rec}" for rec in insights["overall_recommendations"]
        ],
    }

    for section, content_func in sections.items():
        pdf.set_font("Arial", "", 11)
        pdf.cell(0, 10, section + ":", 0, 1)
        pdf.set_font("Arial", "", 10)

        for line in content_func():
            pdf.wrapped_cell(0, 8, line)
        pdf.ln(5)

    # Save the reports
    documentation_folder = filedialog.askdirectory(
        title="Select where to save the reports"
    )
    if not documentation_folder:
        messagebox.showerror(
            "Error", "No folder selected for documentation. Operation cancelled"
        )
        return

    # Save text summary
    summary_path = os.path.join(
        documentation_folder, f"Data_Evaluation_for_{date_today}.txt"
    )
    with open(summary_path, "w") as f:
        f.write("\n".join(summary))

    # Save PDF report
    pdf_path = os.path.join(
        documentation_folder, f"Data_Evaluation_for_{date_today}.pdf"
    )
    pdf.output(pdf_path)

    # Clean up temporary files
    for temp_file in [
        "transaction_overview.png",
        "error_distribution.png",
        "success_rate.png",
    ]:
        if os.path.exists(temp_file):
            os.remove(temp_file)

    messagebox.showinfo(
        "Success!", f"Reports generated:\n1. {summary_path}\n2. {pdf_path}"
    )


if __name__ == "__main__":
    create_summary()
