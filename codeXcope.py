import random
import tkinter as tk
from tkinter import filedialog, messagebox
import csv
import os
from datetime import date, datetime
import re
from PIL import Image, ImageTk
from log_analyzer import LogAnalyzer


# function to create folder for each file.
# this takes two parameters: base path and the folder name.
def create_folder(based_path, folder_name):
    folder_path = os.path.join(based_path, folder_name)
    # check if folder exists, if not create a directory folder.
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
        return folder_path


# function to process the txt file, which is the fund transfer logs.
def process_fund_transfer_logs(file_path):
    base_path = os.path.dirname(file_path)
    date_today = date.today().strftime("%Y-%m-%d")

    # create folder for each file using the create_folder function.
    folder_for_raw_ec2_logs = create_folder(base_path, "Ec2 Logs (Raw)")
    folder_for_raw_status_200_OK = create_folder(base_path, "HTTP Status 200 OK (Raw)")
    folder_for_unsuccessful_transactions = create_folder(
        base_path, "Ec2 Failed Transactions"
    )

    folder_for_src_txn_id_200_OK = create_folder(
        base_path, "HTTP Status 200 OK (Source Transaction IDs)"
    )

    with open(file_path, "r") as file:
        content = file.readlines()

    find_sending_sms = [line for line in content if "sending SMS to" in line]
    find_status_200_ok = [
        line for line in content if "SMS sender response code: 200 OK" in line
    ]
    find_error_responses = [
        line
        for line in content
        if any(
            keyword in line
            for keyword in [
                "HTTP Status Code:",
                "I/O",
                "Unexpected error:",
                "error_messages:",
            ]
        )
    ]

    # save the raw ec2 logs.
    with open(
        os.path.join(folder_for_raw_ec2_logs, f"{date_today}_raw_ec2_logs.csv"),
        "w",
        newline="",
    ) as f:
        writer = csv.writer(f)
        writer.writerow([[line.strip()] for line in find_sending_sms])

    # save the raw HTTP status 200 OK.
    with open(
        os.path.join(
            folder_for_raw_status_200_OK, f"{date_today}_raw_status_200_OK.csv"
        ),
        "w",
        newline="",
    ) as f:
        writer = csv.writer(f)
        writer.writerow([[line.strip()] for line in find_status_200_ok])

    # save the unsuccessful statuses.
    with open(
        os.path.join(
            folder_for_unsuccessful_transactions,
            f"{date_today}_ec2_failed_transactions.csv",
        ),
        "w",
        newline="",
    ) as f:
        writer = csv.writer(f)
        writer.writerow([[line.strip()] for line in find_error_responses])

    # process to extract source transaction id for HTTP status 200 OK.
    src_txn_ids = [
        re.search(r"source_txn_id: (\S+)", line).group(1)
        for line in find_sending_sms
        if "source_txn_id" in line
    ]

    with open(
        os.path.join(
            folder_for_src_txn_id_200_OK, f"{date_today}_src_txn_ids_200_ok.csv"
        ),
        "w",
        newline="",
    ) as f:
        writer = csv.writer(f)
        writer.writerows([[id] for id in src_txn_ids])


# function to process the rds logs.
def process_rds_logs(file_path):
    base_path = os.path.dirname(file_path)
    date_today = date.today().strftime("%Y-%m-%d")
    folder_for_rds_records = create_folder(base_path, "RDS Records")
    folder_for_rds_failed_transactions = create_folder(
        folder_for_rds_records, " rds Failed Transactions"
    )

    with open(file_path, "r") as file:
        reader = csv.reader(file)
        sucessfull_transactions = []  # TS code.
        failed_transactions = []  # TF, SC ,SP, -20, RT codes.

        # iterate through the status codes.
        for row in reader:
            # sucessfull transactions.
            if any("TS" in cell for cell in row):
                sucessfull_transactions.append(row)
            # failed transactions.
            if any("TF" in cell for cell in row):
                failed_transactions.append(row)
            if any("SC" in cell for cell in row):
                failed_transactions.append(row)
            if any("SP" in cell for cell in row):
                failed_transactions.append(row)
            if any("-20" in cell for cell in row):
                failed_transactions.append(row)
            if any("RT" in cell for cell in row):
                failed_transactions.append(row)

    # save the succesfull transactions
    with open(
        os.path.join(
            folder_for_rds_records,
            f"{date_today}rds_sucessfull_transactions.csv",
        ),
        "w",
        newline="",
    ) as f:
        writer = csv.writer(f)
        writer.writerows(sucessfull_transactions)

    # save failed transactions
    if failed_transactions:
        with open(
            os.path.join(
                folder_for_rds_failed_transactions,
                f"{date_today}rds_failed_transactions.csv",
            ),
            "w",
            newline="",
        ) as f:
            writer = csv.writer(f)
            writer.writerows(failed_transactions)


# function to process the promotexter logs.
# This is the sms that is sent from both bountiply and syngenta, we only need to get the message that is from bountiply.
def process_promotexter_data(file_path):
    base_path = os.path.dirname(file_path)
    date_today = date.today().strftime("%Y-%m-%d")
    folder_for_promotexter = create_folder(base_path, "Promotexter Records")

    bountiply_target_message = "Tiwala Partner, we are happy to inform you that your GCash claim has now been credited."
    extracted_records = []

    # open the file in read mode and iterate over each line in the file.
    with open(file_path, "r") as file:
        for line in file:
            #  check if the line contains the target message.
            if bountiply_target_message in line:
                #  extract the line and remove the word before and after the target message.
                extracted_part_of_the_line = (
                    line.split(bountiply_target_message)[0] + bountiply_target_message
                )
                extracted_records.append(extracted_part_of_the_line.strip())

    with open(
        os.path.join(
            folder_for_promotexter, f"{date_today}_records_from_promotexter.csv"
        ),
        "w",
        newline="",
    ) as f:
        writer = csv.writer(f)
        for log in extracted_records:
            writer.writerow([log])


# function to extract the errors from the ec2.
def extract_ec2_errors(file_path):
    http_error_codes = []
    with open(file_path, "r") as file:
        for line in file:
            if (
                "HTTP Status Code: " in line
                or "I/O" in line
                or "error_messages:" in line
            ):
                # extract the full error messages.
                http_error_messages = line.strip()
                # check if the message is an HTTP Status error, and try to extrtact the specific code and message.
                if "HTTP Status Code: " in http_error_messages:
                    match = re.search(
                        r"HTTP Status Code: (\d+).*?messages:\s*(.*?)(?:\s*,|\s*$)",
                        http_error_messages,
                    )
                    if match:
                        status_code, status_message = match.groups()
                        http_error_messages = (
                            f"HTTP Status Code: {status_code} - {status_message}"
                        )
                http_error_codes.append(http_error_messages)
    return http_error_codes


# function to extract the errors from the rds records, this is done to do some cross checking from the ec2 records.
def extract_rds_errors(file_path):
    rds_error_messages = []
    rds_error_categories = {
        "NO RECORDS ON FILE": 0,
        "EXCEEDS ACCOUNT AMOUNT LIMIT": 0,
        "SYSTEM FAILURE; CATCH ALL TRANSACTION PROCESSING ERROR CODE": 0,
    }

    try:
        with open(file_path, "r", newline="") as file:
            reader = csv.reader(file)
            read_all_rows = list(reader)  # read all rows including the headers.

            if not read_all_rows:
                return rds_error_messages, rds_error_categories

            headers = read_all_rows[0]

            # find the message column index.
            message_col_index = None
            for i, header in enumerate(headers):
                if "message" in header.lower():
                    message_col_index = i
                    break

            if message_col_index is None:
                print("Warning: No message column found in CSV headers")
                return rds_error_messages, rds_error_categories

            # process each row including the header
            for row in read_all_rows:
                if len(row) > message_col_index:
                    message = row[message_col_index]

                    # Categorize errors based on message content
                    if "NO RECORD ON FILE" in message.upper():
                        rds_error_categories["NO RECORDS ON FILE"] += 1
                    elif "EXCEEDS ACCOUNT AMOUNT LIMIT" in message.upper():
                        rds_error_categories["EXCEEDS ACCOUNT AMOUNT LIMIT"] += 1
                    elif (
                        "SYSTEM FAILURE; CATCH ALL TRANSACTION PROCESSING ERROR CODE"
                        in message.upper()
                    ):
                        rds_error_categories[
                            "SYSTEM FAILURE; CATCH ALL TRANSACTION PROCESSING ERROR CODE"
                        ] += 1

                    rds_error_messages.append(", ".join(row))

    except Exception as e:
        print(f"Error processing rds errors: {str(e)}")

    return rds_error_messages, rds_error_categories


# process the analyzation with artificial intelligence.
def analyze_with_ai(base_path: str) -> dict:
    """Analyzation with AI insigths."""
    ai_analyzer = LogAnalyzer()

    # collect logs from different sources.
    ec2_logs = []
    rds_logs = []
    promotexter_logs = []

    # read ec2 logs.
    ec2_path = os.path.join(base_path, "Ec2 raw records")
    if os.path.exists(ec2_path):
        for filename in os.listdir(ec2_logs):
            if filename.endswith(".csv"):
                with open(os.path.join(ec2_logs, filename), "r") as f:
                    ec2_logs.extend(f.readlines())

    # read the rds logs.
    rds_path = os.path.join(base_path, "RDS Records")
    if os.path.exists(rds_path):
        for filename in os.listdir(rds_path):
            if filename.endswith(".csv"):
                with open(os.path.join(rds_path, filename), "r") as f:
                    rds_logs.extend(f.readlines())

    # read the promotexter logs.
    promotexter_path = os.path.join(base_path, "Promotexter records")
    if os.path.exists(promotexter_path):
        for filename in os.listdir(promotexter_path):
            if filename.endswith(".csv"):
                with open(os.path.join(promotexter_path, filename), "r") as f:
                    promotexter_logs.extend(f.readlines())

    # get the AI insights
    return ai_analyzer.get_ai_insights(ec2_logs, rds_logs, promotexter_logs)


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
                summary.append(
                    f"Ec2 Logs (Raw) - {filename}: {line_count} transaction(s)"
                )
    # process failed transactions in ec2.
    failed_transactions_path = os.path.join(base_path, "Ec2 failed transactions (Raw)")
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

    # process the rds logs.
    rds_path = os.path.join(base_path, "RDS Logs")
    if os.path.exists(rds_path):
        for filename in os.listdir(rds_path):
            if filename.endswith(".csv"):
                file_path = os.path.join(rds_path, filename)
                with open(file_path, "r") as f:
                    successful_count = sum(1 for _ in f)
                summary.append(
                    f"RDS Successful Transactions - {filename}: {successful_count} successful transaction(s)"
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


#  function for the upload buttons.
def upload_file(button):
    file_path = filedialog.askopenfilename()
    if file_path:
        if button == "Fund Transfer Logs":
            process_fund_transfer_logs(file_path)
        elif button == "RDC Logs":
            process_rds_logs(file_path)
        elif button == "Promotexter Logs":
            process_promotexter_data(file_path)
        messagebox.showinfo("Success!", f"{button} execution successful")


def create_gradient(canvas, color1, color2, width, height):
    for i in range(height):
        r = int(color1[0] + (color2[0] - color1[0]) * i / height)
        g = int(color1[1] + (color2[1] - color1[1]) * i / height)
        b = int(color1[2] + (color2[2] - color1[2]) * i / height)
        color = f"#{r:02x}{g:02x}{b:02x}"
        canvas.create_line(0, i, width, i, fill=color)


def create_gui():
    root = tk.Tk()
    root.title("CodeXCope")

    # Set window size and position
    window_width = 600
    window_height = 500
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    x = (screen_width // 2) - (window_width // 2)
    y = (screen_height // 2) - (window_height // 2)
    root.geometry(f"{window_width}x{window_height}+{x}+{y}")

    # Create canvas for gradient background
    canvas = tk.Canvas(root, width=window_width, height=window_height)
    canvas.pack(fill="both", expand=True)

    # Create gradient background
    create_gradient(canvas, (0, 128, 255), (0, 255, 128), window_width, window_height)

    # Add logo (replace 'path_to_logo.png' with your actual logo path)
    logo = Image.open(r"codeXcope.png")
    logo = logo.resize((200, 100), Image.LANCZOS)
    logo = ImageTk.PhotoImage(logo)
    logo_label = tk.Label(canvas, image=logo, bg=canvas["bg"])
    logo_label.image = logo
    logo_label.place(relx=0.5, rely=0.2, anchor=tk.CENTER)

    buttons = ["Fund Transfer Logs", "Database Logs", "Promotexter Logs"]
    for i, button in enumerate(buttons):
        btn = tk.Button(
            canvas, text=f"Upload {button}", command=lambda b=button: upload_file(b)
        )
        btn.place(relx=0.5, rely=0.5 + i * 0.1, anchor=tk.CENTER)

    summary_btn = tk.Button(canvas, text="Create Summary", command=create_summary)
    summary_btn.place(relx=0.5, rely=0.8, anchor=tk.CENTER)

    root.mainloop()


if __name__ == "__main__":
    create_gui()
