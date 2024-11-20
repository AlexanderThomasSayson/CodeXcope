import re


# function to extract the errors from the ec2.
def extract_ec2_errors(file_path):
    http_error_codes = []
    with open(file_path, "r") as file:
        for line in file:
            if (
                "HTTP Status Code: " in line
                or "I/O" in line
                or "error_message:" in line
                or "Unexpected error:" in line
                or "Response Body:" in line
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
