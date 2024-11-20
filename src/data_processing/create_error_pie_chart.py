import matplotlib.pyplot as plt

def create_error_pie_chart(error_categories):
    """Create a pie chart showing error distribution."""
    plt.figure(figsize=(10, 6))
    if not error_categories or not any(error_categories.values()):
        plt.text(
            0.5,
            0.5,
            "No Error Data Available",
            horizontalalignment="center",
            verticalalignment="center",
            transform=plt.gca().transAxes,
        )
        plt.axis("off")
    else:
        non_zero_errors = {k: v for k, v in error_categories.items() if v > 0}
        if non_zero_errors:
            labels = [
                k[:20] + "..." if len(k) > 20 else k for k in non_zero_errors.keys()
            ]
            values = list(non_zero_errors.values())
            plt.pie(values, labels=labels, autopct="%1.1f%%", startangle=90)
        else:
            plt.text(
                0.5,
                0.5,
                "All Error Counts Are Zero",
                horizontalalignment="center",
                verticalalignment="center",
                transform=plt.gca().transAxes,
            )
            plt.axis("off")

    plt.title("Error Distribution")
    plt.savefig("error_distribution.png", bbox_inches="tight", dpi=300)
    plt.close()