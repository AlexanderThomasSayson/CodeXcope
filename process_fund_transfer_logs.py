import os
import csv
import re
from datetime import date
from create_folder import create_folder


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
                "HTTP Status Code: ",
                "I/O",
                "Unexpected error:",
                "error_message:",
                "Response Body:",
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
        writer.writerows([[line.strip()] for line in find_sending_sms])

    # save the raw HTTP status 200 OK.
    with open(
        os.path.join(
            folder_for_raw_status_200_OK, f"{date_today}_raw_status_200_OK.csv"
        ),
        "w",
        newline="",
    ) as f:
        writer = csv.writer(f)
        writer.writerows([[line.strip()] for line in find_status_200_ok])

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
        writer.writerows([[line.strip()] for line in find_error_responses])

    # process the cleaned logs
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
