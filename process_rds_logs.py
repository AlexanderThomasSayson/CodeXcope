import os
import csv
from create_folder import create_folder
from datetime import date


# function to process the rds logs.
def process_rds_logs(file_path):
    base_path = os.path.dirname(file_path)
    date_today = date.today().strftime("%Y-%m-%d")
    folder_for_rds_records = create_folder(base_path, "RDS Records")
    folder_for_rds_failed_transactions = create_folder(
        folder_for_rds_records, "RDS Failed Transactions"
    )

    with open(file_path, "r") as file:
        reader = csv.reader(file)
        successful_transactions = []
        failed_transactions = []

        failure_codes = ["TF", "SC", "SP", "-20", "RT"]

        # Let's add a header row print to debug
        for row in reader:
            # First check if it's a successful transaction (contains "TS")
            if any("TS" in cell for cell in row):
                successful_transactions.append(row)
            # If it's not successful, check if it contains any failure codes
            else:
                if any(code in cell for cell in row for code in failure_codes):
                    failed_transactions.append(row)

    # Save the successful transactions
    with open(
        os.path.join(
            folder_for_rds_records,
            f"{date_today}_rds_sucessful_transactions.csv",
        ),
        "w",
        newline="",
    ) as f:
        writer = csv.writer(f)
        writer.writerows(successful_transactions)

    # Save failed transactions
    if failed_transactions:
        with open(
            os.path.join(
                folder_for_rds_failed_transactions,
                f"{date_today}_rds_failed_transactions.csv",
            ),
            "w",
            newline="",
        ) as f:
            writer = csv.writer(f)
            writer.writerows(failed_transactions)
