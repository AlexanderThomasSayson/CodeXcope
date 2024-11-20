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