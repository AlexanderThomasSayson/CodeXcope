import tkinter as tk
from tkinter import filedialog, messagebox
import csv
import os
from datetime import date, datetime
import re
from PIL import Image, ImageTk


def create_folder(base_path, folder_name):
    folder_path = os.path.join(base_path, folder_name)
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
    return folder_path


def process_fund_transfer_logs(file_path):
    base_path = os.path.dirname(file_path)
    today = date.today().strftime("%Y-%m-%d")

    uncleaned_folder = create_folder(base_path, "SpringBoot Logs (Unfiltered)")
    ok_folder = create_folder(base_path, "200 OK (Unfiltered)")
    unsuccessful_folder = create_folder(
        base_path, "Failed Transactions (SpringBoot Logs)"
    )
    cleaned_folder = create_folder(base_path, "200 OK (Filtered)")

    with open(file_path, "r") as file:
        content = file.readlines()

    sending_sms = [line for line in content if "sending SMS" in line]
    status_ok = [line for line in content if "SMS sender response code: 200 OK" in line]
    errors = [
        line
        for line in content
        if any(
            keyword in line
            for keyword in [
                "HTTP Status Code: ",
                "I/O",
                "Unexpected error:",
                "error_message",
                "NC",
                "error_message: 500 Internal Server Error:",
            ]
        )
    ]

    # Save Uncleaned Logs
    with open(
        os.path.join(uncleaned_folder, f"{today}_uncleaned.csv"), "w", newline=""
    ) as f:
        writer = csv.writer(f)
        writer.writerows([[line.strip()] for line in sending_sms])

    # Save 200 OK
    with open(os.path.join(ok_folder, f"{today}_200_OK.csv"), "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerows([[line.strip()] for line in status_ok])

    # Save Unsuccessful Transactions
    with open(
        os.path.join(unsuccessful_folder, f"{today}_unsuccessful_transactions.csv"),
        "w",
        newline="",
    ) as f:
        writer = csv.writer(f)
        writer.writerows([[line.strip()] for line in errors])

    # Process Cleaned Logs
    source_ids = [
        re.search(r"source_txn_id: (\S+)", line).group(1)
        for line in sending_sms
        if "source_txn_id:" in line
    ]

    with open(
        os.path.join(cleaned_folder, f"{today}_source_transaction_id.csv"),
        "w",
        newline="",
    ) as f:
        writer = csv.writer(f)
        writer.writerows([[id] for id in source_ids])

    # Process 200 OK Cleaned
    ok_source_ids = [
        re.search(r"source_txn_id: (\S+)", line).group(1)
        for line in status_ok
        if "source_txn_id" in line
    ]

    with open(
        os.path.join(cleaned_folder, f"{today}_200_OK_cleaned.csv"), "w", newline=""
    ) as f:
        writer = csv.writer(f)
        writer.writerows([[id] for id in ok_source_ids])


def process_database_logs(file_path):
    base_path = os.path.dirname(file_path)
    today = date.today().strftime("%Y-%m-%d")
    database_folder = create_folder(base_path, "Database Logs")
    failed_transactions_folder = create_folder(
        database_folder, "Failed Transactions (Database)"
    )

    with open(file_path, "r") as file:
        reader = csv.reader(file)
        ts_logs = []
        tf_logs = []
        for row in reader:
            if any("TS" in cell for cell in row):
                ts_logs.append(row)
            if any(
                "TF" in cell
                or "NC" in cell
                or "SP" in cell
                or "SC" in cell
                or "-20" in cell
                for cell in row
            ):
                tf_logs.append(row)

    # Save TS logs
    with open(
        os.path.join(database_folder, f"{today}_database.csv"), "w", newline=""
    ) as f:
        writer = csv.writer(f)
        writer.writerows(ts_logs)

    # Save TF logs (Failed Transactions)
    if tf_logs:
        with open(
            os.path.join(
                failed_transactions_folder, f"{today}_failed_transactions.csv"
            ),
            "w",
            newline="",
        ) as f:
            writer = csv.writer(f)
            writer.writerows(tf_logs)


def process_promotexter_logs(file_path):
    base_path = os.path.dirname(file_path)
    today = date.today().strftime("%Y-%m-%d")
    promotexter_folder = create_folder(base_path, "Promotexter Logs")

    target_message = "Tiwala Partner, we are happy to inform you that your GCash claim has now been credited."
    extracted_logs = []

    with open(file_path, "r") as file:
        for line in file:
            if target_message in line:
                # Extract the part of the line up to and including the target message
                extracted_part = line.split(target_message)[0] + target_message
                extracted_logs.append(extracted_part.strip())

    with open(
        os.path.join(promotexter_folder, f"{today}_promotexter.csv"), "w", newline=""
    ) as f:
        writer = csv.writer(f)
        for log in extracted_logs:
            writer.writerow([log])

    print(f"Processed {len(extracted_logs)} Promotexter logs.")


def extract_springboot_errors(file_path):
    errors = []
    with open(file_path, "r") as file:
        for line in file:
            if (
                "HTTP Status Code: " in line
                or "Unexpected error:" in line
                or "I/O" in line
            ):
                # Extract the full error message
                error_msg = line.strip()
                # If it's an HTTP Status error, try to extract the specific code and message
                if "HTTP Status Code: " in error_msg:
                    match = re.search(
                        r"HTTP Status Code: (\d+).*?message:\s*(.*?)(?:\s*,|\s*$)",
                        error_msg,
                    )
                    if match:
                        status_code, message = match.groups()
                        error_msg = f"HTTP Status Code: {status_code} - {message}"
                errors.append(error_msg)
    return errors


def extract_database_errors(file_path):
    errors = []
    error_categories = {
        "NO RECORDS ON FILE": 0,
        "EXCEEDS ACCOUNT AMOUNT LIMIT": 0,
        "SYSTEM FAILURE; CATCH ALL TRANSACTION PROCESSING ERROR CODE": 0,
    }

    try:
        with open(file_path, "r", newline="") as file:
            reader = csv.reader(file)
            all_rows = list(reader)  # Read all rows including header

            if not all_rows:
                return errors, error_categories

            headers = all_rows[0]

            # Find the message column index
            message_col_index = None
            for i, header in enumerate(headers):
                if "message" in header.lower():
                    message_col_index = i
                    break

            if message_col_index is None:
                print("Warning: No message column found in CSV headers")
                return errors, error_categories

            # Process each row including header
            for row in all_rows:  # Process all rows
                if len(row) > message_col_index:
                    message = row[message_col_index]

                    # Categorize errors based on message content
                    if "NO RECORD ON FILE" in message.upper():
                        error_categories["NO RECORDS ON FILE"] += 1
                    elif "EXCEEDS ACCOUNT AMOUNT LIMIT" in message.upper():
                        error_categories["EXCEEDS ACCOUNT AMOUNT LIMIT"] += 1
                    elif (
                        "SYSTEM FAILURE; CATCH ALL TRANSACTION PROCESSING ERROR CODE"
                        in message.upper()
                    ):
                        error_categories[
                            "SYSTEM FAILURE; CATCH ALL TRANSACTION PROCESSING ERROR CODE"
                        ] += 1

                    errors.append(", ".join(row))

    except Exception as e:
        print(f"Error processing database errors: {str(e)}")

    return errors, error_categories


def create_summary():
    today = date.today().strftime("%Y-%m-%d")
    now = datetime.now().strftime("%H:%M:%S")
    summary = []

    # Ask user to select the base folder containing all log folders
    base_path = filedialog.askdirectory(
        title="Select the folder containing all log folders"
    )
    if not base_path:
        messagebox.showerror("Error", "No folder selected. Operation cancelled.")
        return

    # Ask user to select where to save the documentation
    documentation_folder = filedialog.askdirectory(
        title="Select where to save the documentation"
    )
    if not documentation_folder:
        messagebox.showerror(
            "Error", "No folder selected for documentation. Operation cancelled."
        )
        return

    summary.append(f"**Summary Report as of {today} at {now}**")
    summary.append(
        "Good day! We have reviewed the logs from the server, database, and Promotexter. The current findings are as follows:\n"
    )

    # Initialize counters
    successful_count = 0
    sms_failed_count = 0
    failed_transactions = 0
    error_categories = {
        "NO RECORDS ON FILE": 0,
        "EXCEEDS ACCOUNT AMOUNT LIMIT": 0,
        "SYSTEM FAILURE; CATCH ALL TRANSACTION PROCESSING ERROR CODE": 0,
    }
    duplicate_transactions = set()

    # Process SpringBoot logs
    springboot_path = os.path.join(base_path, "SpringBoot Logs (Unfiltered)")
    if os.path.exists(springboot_path):
        for filename in os.listdir(springboot_path):
            if filename.endswith(".csv"):
                file_path = os.path.join(springboot_path, filename)
                with open(file_path, "r") as f:
                    line_count = sum(1 for _ in f)
                # summary.append(f"SpringBoot Logs (Unfiltered) - {filename}: {line_count} transaction(s)")

    # Process Failed Transactions (UBP)
    failed_path = os.path.join(base_path, "Failed Transactions (SpringBoot Logs)")
    if os.path.exists(failed_path):
        for filename in os.listdir(failed_path):
            if filename.endswith(".csv"):
                file_path = os.path.join(failed_path, filename)
                # Use the enhanced error extraction function
                errors = extract_springboot_errors(file_path)
                sms_failed_count = len(errors)

                summary.append(
                    f"\nFailed to send SMS - {filename}: {sms_failed_count} failed to send SMS transaction(s)"
                )
                if errors:
                    summary.append("Detailed Errors:")
                    for error in errors:
                        summary.append(f"  - {error}")
                else:
                    summary.append("No specific errors found in the log file.")

    # Process Database logs
    database_path = os.path.join(base_path, "Database Logs")
    if os.path.exists(database_path):
        for filename in os.listdir(database_path):
            if filename.endswith(".csv"):
                file_path = os.path.join(database_path, filename)
                with open(file_path, "r") as f:
                    successful_count = sum(1 for _ in f)
                summary.append(
                    f"UBP Successful Transaction(s) - {filename}: {successful_count} successful transaction(s)."
                )

    # Process Promotexter logs
    promotexter_path = os.path.join(base_path, "Promotexter Logs")
    if os.path.exists(promotexter_path):
        for filename in os.listdir(promotexter_path):
            if filename.endswith(".csv"):
                file_path = os.path.join(promotexter_path, filename)
                with open(file_path, "r") as f:
                    line_count = sum(1 for _ in f)
                summary.append(
                    f"Promotexter Sent SMS - {filename}: {line_count} transaction(s) sent successfully."
                )

    # Process Database Failed Transactions with dynamic error categorization
    failed_db_path = os.path.join(database_path, "Failed Transactions (Database)")
    if os.path.exists(failed_db_path):
        for filename in os.listdir(failed_db_path):
            if filename.endswith(".csv"):
                file_path = os.path.join(failed_db_path, filename)
                errors, error_cats = extract_database_errors(file_path)
                failed_transactions = len(errors)

                # Update error categories
                for category, count in error_cats.items():
                    error_categories[category] = count

                summary.append(
                    f"UBP Failed Transaction(s) - {filename}: {failed_transactions} transaction(s)"
                )
                summary.append("Errors:")
                for error in errors:
                    summary.append(f"  - {error}")

    # Add summary statistics
    summary.append(f"\n-----------------Brief Summary-------------------\n")
    total_records = successful_count + failed_transactions
    summary.append(f"\nTotal Records from Auditrail: {total_records}")
    summary.append(f"UBP Successful Transaction(s): {successful_count}")
    summary.append(f"Promotexter Sent SMS: {line_count}")
    summary.append(f"\nUBP Failed Transactions: {failed_transactions} transactions")
    summary.append(f"NO RECORDS ON FILE - {error_categories['NO RECORDS ON FILE']}")
    summary.append(
        f"EXCEEDS ACCOUNT AMOUNT LIMIT - {error_categories['EXCEEDS ACCOUNT AMOUNT LIMIT']}"
    )
    summary.append(
        f"SYSTEM FAILURE; CATCH ALL TRANSACTION PROCESSING ERROR CODE - {error_categories['SYSTEM FAILURE; CATCH ALL TRANSACTION PROCESSING ERROR CODE']}"
    )

    # Add duplicate transactions (if any were found during processing)
    if duplicate_transactions:
        summary.append("\nDuplicate Transactions:")
        for txn_id, name in duplicate_transactions:
            summary.append(
                f"DUPLICATE TRANSACTIONS - source_txn_id: {txn_id}, Name: {name}"
            )

    # Write summary to file
    summary_file_path = os.path.join(documentation_folder, f"{today}_summary.txt")
    with open(summary_file_path, "w") as f:
        f.write("\n".join(summary))

    messagebox.showinfo("Success", f"Summary Report created: {summary_file_path}")


def upload_file(button):
    file_path = filedialog.askopenfilename()
    if file_path:
        if button == "Fund Transfer Logs":
            process_fund_transfer_logs(file_path)
        elif button == "Database Logs":
            process_database_logs(file_path)
        elif button == "Promotexter Logs":
            process_promotexter_logs(file_path)
        messagebox.showinfo("Success", f"{button} processed successfully!")


def create_gradient(canvas, color1, color2, width, height):
    for i in range(height):
        r = int(color1[0] + (color2[0] - color1[0]) * i / height)
        g = int(color1[1] + (color2[1] - color1[1]) * i / height)
        b = int(color1[2] + (color2[2] - color1[2]) * i / height)
        color = f"#{r:02x}{g:02x}{b:02x}"
        canvas.create_line(0, i, width, i, fill=color)


def create_gui():
    root = tk.Tk()
    root.title("Logify by Bountiply")

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
    logo = Image.open(r"bountiply.png")
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
