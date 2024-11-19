import random
import os
from datetime import date, datetime
from tkinter import filedialog, messagebox
from extract_ec2_errors import extract_ec2_errors
from extract_rds_errors import extract_rds_errors
from analyze_with_ai import analyze_with_ai


# function to create the summary
def create_summary():
    date_today = date.today().strftime("%Y-%m-%d")
    current_time = datetime.now().strftime("%H:%M:%S")
    summary = []

    # ask the user to select the base folder containing all the log files.
    base_path = filedialog.askdirectory(
        title="Select the folder containing all log files."
    )
    if not base_path:
        messagebox.showerror("Error: ", "No folder selected, Operation is cancelled.")
        return

    summary.append(f"**Summary Report as of {date_today} at {current_time}**")

    #  random messages
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

    message = (
        f"{random.choice(greetings)} "
        f"{random.choice(intros)} "
        f"{random.choice(systems)}. "
        f"{random.choice(transitions)}\n"
    )

    summary.append(message)

    # initialize counters
    successful_count = 0
    promotexter_failed_count = 0
    failed_transactions = 0
    error_categories = {
        "NO RECORDS ON FILE": 0,
        "EXCEEDS ACCOUNT AMOUNT LIMIT": 0,
        "SYSTEM FAILURE; CATCH ALL TRANSACTION PROCESSING ERROR CODE": 0,
    }
    duplicate_transactions = set()

    # process ec2 logs.
    ec2_path = os.path.join(base_path, "Ec2 Logs (Raw)")
    if os.path.exists(ec2_path):
        for filename in os.listdir(ec2_path):
            if filename.endswith(".csv"):
                file_path = os.path.join(ec2_path, filename)
                with open(file_path, "r") as f:
                    line_count = sum(1 for _ in f)
                # summary.append(
                #     f"Ec2 Logs (Raw) - {filename}: {line_count} transaction(s)"
                # )
    # process failed transactions in ec2.
    failed_transactions_path = os.path.join(base_path, "Ec2 Failed Transactions")
    if os.path.exists(failed_transactions_path):
        for filename in os.listdir(failed_transactions_path):
            if filename.endswith(".csv"):
                failed_transactions_path = os.path.join(
                    failed_transactions_path, filename
                )

                # use the error extraction function
                error_codes = extract_ec2_errors(file_path)
                promotexter_failed_count = len(error_codes)

                summary.append(
                    f"\nFailed to send SMS - {filename}: {promotexter_failed_count} failed to send SMS transaction(s)"
                )
                if error_codes:
                    summary.append("\n Detailed Errors:")
                    for error in error_codes:
                        summary.append(f" - {error}")
                else:
                    summary.append(
                        "Congratulations, no specific errors found in the log file."
                    )

    # process the RDS logs.
    rds_path = os.path.join(base_path, "RDS Records")
    if os.path.exists(rds_path):
        for filename in os.listdir(rds_path):
            if filename.endswith(".csv"):
                file_path = os.path.join(rds_path, filename)
                with open(file_path, "r") as f:
                    successful_count = sum(1 for _ in f)
                summary.append(
                    f"UnionBank Successful Transactions - {filename}: {successful_count} successful transaction(s)"
                )

    # process the promotexter logs.
    promotexter_path = os.path.join(base_path, "Promotexter Records")
    if os.path.exists(promotexter_path):
        for filename in os.listdir(promotexter_path):
            if filename.endswith(".csv"):
                file_path = os.path.join(promotexter_path, filename)
                with open(file_path, "r") as f:
                    line_count = sum(1 for _ in f)
                summary.append(
                    f"Sent SMS from Promotexter - {filename}: {line_count} transaction(s) sent succesfully."
                )

    # process rds failed transactions with dynamic error categorization
    failed_rds_transactions_path = os.path.join(rds_path, "RDC Failed Transactions")
    if os.path.exists(failed_rds_transactions_path):
        for filename in os.listdir(failed_rds_transactions_path):
            if filename.endswith(".csv"):
                file_path = os.path.join(failed_rds_transactions_path, filename)
                error_codes, error_cats = extract_rds_errors(file_path)
                failed_transactions = len(error_codes)

                # update the error categories
                for category, count in error_cats.items():
                    error_categories[category] = count

                summary.append(
                    f"RDC Failed Transaction(s) - {filename}: {failed_transactions} transaction(s)"
                )
                summary.append("Found Errors:")
                for error in error_codes:
                    summary.append(f" - {error}")

    # add summary statistics.
    summary.append(f"\n-------------------------Overview-------------------------")
    total_records_from_audit_trail = successful_count + failed_transactions
    summary.append(f"\nTotal Records from Audtrail: {total_records_from_audit_trail}")
    summary.append(f"UBP Successful Transaction(s): {successful_count}")
    summary.append(f"Sent SMS from Promotexter:{line_count}")
    summary.append(f"\nUBP Failed Transactions: {failed_transactions} transaction(s)")
    # error messages counts.
    summary.append(f"NO RECORDS ON FILE - {error_categories['NO RECORDS ON FILE']}")
    summary.append(
        f"EXCEEDS ACCOUNT AMOUNT LIMIT - {error_categories['EXCEEDS ACCOUNT AMOUNT LIMIT']}"
    )
    summary.append(
        f"SYSTEM FAILURE; CATCH ALL TRANSACTION PROCESSING ERROR CODE - {error_categories['SYSTEM FAILURE; CATCH ALL TRANSACTION PROCESSING ERROR CODE']}"
    )

    # add duplicate transactions (if any were found during processing)
    if duplicate_transactions:
        summary.append("\nDuplcate Transactions:")
        for txn_id, name in duplicate_transactions:
            summary.append(
                f"DUPLICATE TRANSACTION  - source_txn_id: {txn_id}, Name: {name}"
            )
        # add the analysis of AI.
    ai_insights = analyze_with_ai(base_path)

    # add AI insights to the summary
    summary.append("\n --------------------AI Insights---------------------------\n")

    # add error analysis
    summary.append("\n Error Pattern Analysis:")
    for (
        pattern,
        count,
    ) in ai_insights[
        "error_analysis"
    ]["common_patterns"]:
        summary.append(f"- {pattern}: {count} occurrences")

    # add transaction analysis
    summary.append("\nTransaction Pattern Analysis:")
    summary.append(
        f" - Success Rate: {ai_insights['transaction_analysis']['success_rate']:.1f}%"
    )
    if ai_insights["transaction_analysis"]["peak_hours"]:
        peak_hours_str = ", ".join(
            [
                f"{h['hour']}:00"
                for h in ai_insights["transaction_analysis"]["peak_hours"]
            ]
        )
        summary.append(f"- Peak Transaction Hours: {peak_hours_str}")

    # add promotexter analysis.
    summary.append("\nPromotexter Delivery Analysis:")
    summary.append(
        f" - Delvery Success Rate: {ai_insights['sms_analysis']['delivery_rate']:.1f}%"
    )

    # add AI recommendations
    summary.append("\n AI Recommendations:")
    for rec in ai_insights["overall_recommendations"]:
        summary.append(f" - {rec}")

    # ask user to select where to save the documentation
    documentation_folder = filedialog.askdirectory(
        title="Please select where to save the documentation"
    )

    # check if the user select a folder for documentation
    if not documentation_folder:
        messagebox.showerror(
            "Error", "No folder selected for documentation. Operation cancelled"
        )
        return

    # write summary to file.
    summary_file_path = os.path.join(
        documentation_folder, f"Data_Evaluation_for_{date_today}.txt"
    )
    with open(summary_file_path, "w") as f:
        f.write("\n".join(summary))

    messagebox.showinfo("Success!", f"Overview Report generated: {summary_file_path}")
