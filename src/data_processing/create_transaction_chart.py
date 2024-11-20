import matplotlib.pyplot as plt

def create_transaction_chart(successful_count, failed_transactions, promotexter_count):
    """Create a bar chart showing transaction statistics."""
    plt.figure(figsize=(10, 6))

    # Validate inputs
    successful_count = max(
        0, successful_count if isinstance(successful_count, (int, float)) else 0
    )
    failed_transactions = max(
        0, failed_transactions if isinstance(failed_transactions, (int, float)) else 0
    )
    promotexter_count = max(
        0, promotexter_count if isinstance(promotexter_count, (int, float)) else 0
    )

    labels = ["Successful", "Failed", "SMS Sent"]
    values = [successful_count, failed_transactions, promotexter_count]
    colors = ["#2ecc71", "#e74c3c", "#3498db"]

    if any(values):
        plt.bar(labels, values, color=colors)
    else:
        plt.text(
            0.5,
            0.5,
            "No Transaction Data Available",
            horizontalalignment="center",
            verticalalignment="center",
            transform=plt.gca().transAxes,
        )
        plt.axis("off")

    plt.title("Transaction Overview")
    plt.ylabel("Number of Transactions")
    plt.xticks(rotation=45)
    plt.savefig("transaction_overview.png", bbox_inches="tight", dpi=300)
    plt.close()