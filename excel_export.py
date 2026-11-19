
from pathlib import Path
import os
import tempfile

from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment
from openpyxl.utils import get_column_letter

from database import get_connection
from attribution import calculate_attribution


BASE_DIR = Path(__file__).resolve().parent
EXPORT_DIR = BASE_DIR / "exports"
EXCEL_FILE = EXPORT_DIR / "Marketing_Attribution_Report.xlsx"


def format_sheet(ws):
    """Format worksheet headers and columns."""

    ws.freeze_panes = "A2"
    ws.auto_filter.ref = ws.dimensions

    for cell in ws[1]:
        cell.font = Font(bold=True, color="FFFFFF")
        cell.fill = PatternFill(
            fill_type="solid",
            fgColor="1F4E78"
        )
        cell.alignment = Alignment(
            horizontal="center"
        )

    for column in ws.columns:
        max_length = 0
        column_letter = get_column_letter(
            column[0].column
        )

        for cell in column:
            if cell.value is not None:
                max_length = max(
                    max_length,
                    len(str(cell.value))
                )

        ws.column_dimensions[column_letter].width = min(
            max(max_length + 3, 14),
            40
        )


def write_table(ws, headers, records):
    """Write database records into a worksheet."""

    ws.append(headers)

    for record in records:
        values = []

        for value in record:
            if value is None:
                values.append("")
            else:
                values.append(value)

        ws.append(values)

    format_sheet(ws)


def export_workbook():
    """
    Export current database records and attribution
    calculations into an Excel workbook.

    Returns the generated workbook path.
    """

    EXPORT_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    connection = get_connection()

    try:
        # 1. Visitors
        visitors = connection.execute("""
            SELECT visitor_id, first_seen
            FROM visitors
            ORDER BY first_seen
        """).fetchall()

        # 2. Touchpoints
        touchpoints = connection.execute("""
            SELECT
                touchpoint_id,
                visitor_id,
                channel,
                visited_at
            FROM touchpoints
            ORDER BY visited_at, touchpoint_id
        """).fetchall()

        # 3. Orders
        order_columns = [
            row["name"]
            for row in connection.execute(
                "PRAGMA table_info(orders)"
            )
        ]

        selected_order_columns = [
            "order_id",
            "visitor_id",
            "total_amount",
            "ordered_at"
        ]

        if "survey_source" in order_columns:
            selected_order_columns.append(
                "survey_source"
            )

        orders = connection.execute(
            f"""
            SELECT {", ".join(selected_order_columns)}
            FROM orders
            ORDER BY ordered_at, order_id
            """
        ).fetchall()

    finally:
        connection.close()

    # 4. Existing attribution calculations
    report = calculate_attribution()

    workbook = Workbook()

    # Visitors worksheet
    ws = workbook.active
    ws.title = "Visitors"

    write_table(
        ws,
        ["Visitor ID", "First Seen"],
        visitors
    )

    # Touchpoints worksheet
    ws = workbook.create_sheet("Touchpoints")

    write_table(
        ws,
        [
            "Touchpoint ID",
            "Visitor ID",
            "Channel",
            "Visited At"
        ],
        touchpoints
    )

    # Orders worksheet
    ws = workbook.create_sheet("Orders")

    order_headers = [
        column.replace("_", " ").title()
        for column in selected_order_columns
    ]

    write_table(
        ws,
        order_headers,
        orders
    )

    # Attribution summary worksheet
    ws = workbook.create_sheet("Attribution_Summary")

    ws.append(["Metric", "Value"])
    ws.append(["Report Generated", __import__("datetime").datetime.now().isoformat(timespec="seconds")])
    ws.append(["Total Revenue", report["total_revenue"]])
    ws.append(["Unattributed Revenue", report["unattributed_revenue"]])
    ws.append(["Total Orders", report["total_orders"]])
    ws.append(["Attributed Orders", report["attributed_orders"]])

    ws.append([])
    ws.append([
        "Channel",
        "First Touch Revenue",
        "Last Touch Revenue",
        "Linear Revenue"
    ])

    for row in report["channels"]:
        ws.append([
            row["channel"],
            row["first_touch"],
            row["last_touch"],
            row["linear"]
        ])

    format_sheet(ws)

    # Save safely using a temporary file.
    # The previous workbook remains intact if saving fails.

    temporary_path = None

    try:
        with tempfile.NamedTemporaryFile(
            suffix=".xlsx",
            dir=EXPORT_DIR,
            delete=False
        ) as temporary_file:
            temporary_path = Path(temporary_file.name)

        workbook.save(temporary_path)

        os.replace(
            temporary_path,
            EXCEL_FILE
        )

    except Exception:
        if temporary_path and temporary_path.exists():
            temporary_path.unlink()
        raise

    return EXCEL_FILE
