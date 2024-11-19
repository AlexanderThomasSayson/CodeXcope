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
