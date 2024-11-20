import csv


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
        print(f"Error processing RDS errors: {str(e)}")

    return rds_error_messages, rds_error_categories
