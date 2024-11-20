import matplotlib.pyplot as plt
import numpy as np
def create_success_rate_gauge(success_rate):
    """Create a gauge chart showing success rate."""
    plt.figure(figsize=(8, 4))
    success_rate = max(
        0,
        min(100, float(success_rate) if isinstance(success_rate, (int, float)) else 0),
    )

    angles = np.linspace(0, 180, 100)
    values = np.ones(100) * success_rate

    plt.plot(angles, values)
    plt.fill_between(angles, 0, values, alpha=0.3)
    plt.title(f"Success Rate: {success_rate:.1f}%")

    plt.savefig("success_rate.png", bbox_inches="tight", dpi=300)
    plt.close()