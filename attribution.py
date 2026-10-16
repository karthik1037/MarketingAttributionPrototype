

from decimal import Decimal
from database import get_connection

CHANNELS = {
    "paid_social": "Paid Social",
    "influencer": "Influencer Marketing",
    "word_of_mouth": "Word of Mouth",
    "farmers_market": "Farmers Markets / Pop-ups"
}


def calculate_attribution():
    results = {
        channel: {
            "first_touch": Decimal("0"),
            "last_touch": Decimal("0"),
            "linear": Decimal("0")
        }
        for channel in CHANNELS
    }

    unattributed_revenue = Decimal("0")
    total_revenue = Decimal("0")
    attributed_orders = 0

    connection = get_connection()

    try:
        orders = connection.execute("""
            SELECT order_id, visitor_id, total_amount, ordered_at
            FROM orders
            ORDER BY ordered_at, order_id
        """).fetchall()

        for order in orders:
            revenue = Decimal(str(order["total_amount"]))
            total_revenue += revenue

            # Include only touchpoints before the order.
            # ID resolves ordering when timestamps match.
            touchpoints = connection.execute("""
                SELECT channel
                FROM touchpoints
                WHERE visitor_id = ?
                  AND visited_at <= ?
                ORDER BY visited_at, touchpoint_id
            """, (
                order["visitor_id"],
                order["ordered_at"]
            )).fetchall()

            channels = [
                row["channel"]
                for row in touchpoints
                if row["channel"] in CHANNELS
            ]

            if not channels:
                unattributed_revenue += revenue
                continue

            attributed_orders += 1

            # First-touch model
            results[channels[0]]["first_touch"] += revenue

            # Last-touch model
            results[channels[-1]]["last_touch"] += revenue

            # Linear model
            credit = revenue / Decimal(len(channels))

            for channel in channels:
                results[channel]["linear"] += credit

    finally:
        connection.close()

    formatted_results = []

    for channel, values in results.items():
        formatted_results.append({
            "channel": CHANNELS[channel],
            "first_touch": round(
                float(values["first_touch"]), 2
            ),
            "last_touch": round(
                float(values["last_touch"]), 2
            ),
            "linear": round(
                float(values["linear"]), 2
            )
        })

    return {
        "channels": formatted_results,
        "total_revenue": round(float(total_revenue), 2),
        "unattributed_revenue": round(
            float(unattributed_revenue), 2
        ),
        "attributed_orders": attributed_orders,
        "total_orders": len(orders)
    }


if __name__ == "__main__":
    report = calculate_attribution()

    print("\nBONFIRE PEPPER CO. — ATTRIBUTION REPORT")
    print("-" * 75)

    print(
        f"{'Channel':25}"
        f"{'First Touch':15}"
        f"{'Last Touch':15}"
        f"{'Linear':15}"
    )

    for row in report["channels"]:
        print(
            f"{row['channel']:25}"
            f"${row['first_touch']:<14.2f}"
            f"${row['last_touch']:<14.2f}"
            f"${row['linear']:<14.2f}"
        )

    print("-" * 75)
    print(f"Total revenue: ${report['total_revenue']:.2f}")
    print(
        "Unattributed revenue: "
        f"${report['unattributed_revenue']:.2f}"
    )
    print(
        f"Attributed orders: {report['attributed_orders']}"
    )

