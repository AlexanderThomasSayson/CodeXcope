def generate_basic_insights(
    successful_count, failed_transactions, promotexter_count, error_categories
):
    """Generate basic statistical insights from the available data."""
    total_transactions = successful_count + failed_transactions
    success_rate = (
        (successful_count / total_transactions * 100) if total_transactions > 0 else 0
    )
    sms_delivery_rate = (
        (promotexter_count / successful_count * 100) if successful_count > 0 else 0
    )

    # Find most common error if any errors exist
    most_common_error = (
        max(error_categories.items(), key=lambda x: x[1])
        if error_categories
        else ("None", 0)
    )

    return {
        "error_analysis": {
            "common_patterns": [(most_common_error[0], most_common_error[1])]
        },
        "transaction_analysis": {
            "success_rate": success_rate,
            "total_transactions": total_transactions,
            "peak_hours": [],  # We don't have hourly data in the current implementation
        },
        "sms_analysis": {"delivery_rate": sms_delivery_rate},
        "overall_recommendations": [
            f"Current success rate is {success_rate:.1f}%. Consider investigating failed transactions to improve this rate.",
            f"SMS delivery rate is {sms_delivery_rate:.1f}%. Monitor this metric for service quality.",
            f"Most common error: {most_common_error[0]} ({most_common_error[1]} occurrences).",
        ],
    }