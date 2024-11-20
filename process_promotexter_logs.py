import os
import csv
from create_folder import create_folder
from datetime import date


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


# 639095532118
