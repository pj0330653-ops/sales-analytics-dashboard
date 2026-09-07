"""
build_report.py
Builds Sales_Report.xlsx from the cleaned data + summary CSVs.
Uses openpyxl so every number on the report is a live formula,
not a hardcoded Python-computed value.

Run: python build_report.py
Output: Sales_Report.xlsx
"""

import pandas as pd
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.chart import LineChart, BarChart, PieChart, Reference
from openpyxl.utils import get_column_letter

FONT_NAME = "Arial"
HEADER_FILL = PatternFill("solid", fgColor="1F4E78")
HEADER_FONT = Font(name=FONT_NAME, bold=True, color="FFFFFF", size=11)
TITLE_FONT = Font(name=FONT_NAME, bold=True, size=16, color="1F4E78")
KPI_LABEL_FONT = Font(name=FONT_NAME, bold=True, size=10, color="595959")
KPI_VALUE_FONT = Font(name=FONT_NAME, bold=True, size=18, color="1F4E78")
THIN = Side(style="thin", color="D9D9D9")
BORDER = Border(left=THIN, right=THIN, top=THIN, bottom=THIN)

clean = pd.read_csv("../data/sales_data_clean.csv")
monthly = pd.read_csv("../data/monthly_trend.csv")
region = pd.read_csv("../data/region_summary.csv")
category = pd.read_csv("../data/category_summary.csv")
reps = pd.read_csv("../data/rep_leaderboard.csv")

wb = Workbook()

# ---------------------------------------------------------------------------
# Sheet 1: Raw Data  (source for every formula in the workbook)
# ---------------------------------------------------------------------------
ws_data = wb.active
ws_data.title = "Raw Data"
ws_data.append(list(clean.columns))
for cell in ws_data[1]:
    cell.font = HEADER_FONT
    cell.fill = HEADER_FILL
for row in clean.itertuples(index=False):
    ws_data.append(list(row))
for col_idx, col in enumerate(clean.columns, 1):
    ws_data.column_dimensions[get_column_letter(col_idx)].width = 14
n_data_rows = len(clean) + 1  # + header

# ---------------------------------------------------------------------------
# Sheet 2: Dashboard (KPIs + charts)
# ---------------------------------------------------------------------------
ws = wb.create_sheet("Dashboard")
ws.sheet_view.showGridLines = False
ws["B2"] = "Sales Analytics Dashboard"
ws["B2"].font = TITLE_FONT
ws["B3"] = "FY2024–FY2025 · All figures in ₹"
ws["B3"].font = Font(name=FONT_NAME, italic=True, size=10, color="808080")

# --- KPI cards (formulas referencing Raw Data) ---
kpi_defs = [
    ("Total Revenue", f"=SUM('Raw Data'!L2:L{n_data_rows})", "₹#,##0"),
    ("Total Orders", f"=COUNTA('Raw Data'!A2:A{n_data_rows})", "#,##0"),
    ("Units Sold", f"=SUM('Raw Data'!H2:H{n_data_rows})", "#,##0"),
    ("Avg Order Value", f"=SUM('Raw Data'!L2:L{n_data_rows})/COUNTA('Raw Data'!A2:A{n_data_rows})", "₹#,##0"),
]
start_col = 2  # column B
for i, (label, formula, fmt) in enumerate(kpi_defs):
    col = start_col + i * 3
    letter = get_column_letter(col)
    ws.merge_cells(start_row=5, start_column=col, end_row=5, end_column=col + 1)
    ws.merge_cells(start_row=6, start_column=col, end_row=7, end_column=col + 1)
    lbl_cell = ws.cell(row=5, column=col, value=label)
    lbl_cell.font = KPI_LABEL_FONT
    val_cell = ws.cell(row=6, column=col, value=formula)
    val_cell.font = KPI_VALUE_FONT
    val_cell.number_format = fmt
    val_cell.alignment = Alignment(vertical="center")
    for r in (5, 6, 7):
        for c in (col, col + 1):
            ws.cell(row=r, column=c).fill = PatternFill("solid", fgColor="EAF1FA")

# --- Monthly trend table (feeds the line chart) ---
ws["B10"] = "Monthly Revenue Trend"
ws["B10"].font = Font(name=FONT_NAME, bold=True, size=12)
headers = ["Month", "Revenue", "Orders", "Units"]
for j, h in enumerate(headers):
    c = ws.cell(row=11, column=2 + j, value=h)
    c.font = HEADER_FONT
    c.fill = HEADER_FILL
for i, row in enumerate(monthly.itertuples(index=False), start=12):
    ws.cell(row=i, column=2, value=row.order_month)
    ws.cell(row=i, column=3, value=row.revenue).number_format = "₹#,##0"
    ws.cell(row=i, column=4, value=row.orders)
    ws.cell(row=i, column=5, value=row.units)
last_month_row = 11 + len(monthly)

line = LineChart()
line.title = "Monthly Revenue Trend"
line.style = 10
line.y_axis.title = "Revenue (₹)"
line.x_axis.title = "Month"
line.height = 8
line.width = 18
data_ref = Reference(ws, min_col=3, min_row=11, max_row=last_month_row)
cats_ref = Reference(ws, min_col=2, min_row=12, max_row=last_month_row)
line.add_data(data_ref, titles_from_data=True)
line.set_categories(cats_ref)
ws.add_chart(line, f"G11")

# --- Region summary table (feeds bar chart) ---
region_start = last_month_row + 3
ws.cell(row=region_start, column=2, value="Region-wise Performance").font = Font(name=FONT_NAME, bold=True, size=12)
r_headers = ["Region", "Revenue", "Orders", "Avg Order Value"]
for j, h in enumerate(r_headers):
    c = ws.cell(row=region_start + 1, column=2 + j, value=h)
    c.font = HEADER_FONT
    c.fill = HEADER_FILL
for i, row in enumerate(region.itertuples(index=False), start=region_start + 2):
    ws.cell(row=i, column=2, value=row.region)
    ws.cell(row=i, column=3, value=row.revenue).number_format = "₹#,##0"
    ws.cell(row=i, column=4, value=row.orders)
    ws.cell(row=i, column=5, value=row.avg_order_value).number_format = "₹#,##0"
region_end_row = region_start + 1 + len(region)

bar = BarChart()
bar.title = "Revenue by Region"
bar.style = 10
bar.y_axis.title = "Revenue (₹)"
bar.height = 8
bar.width = 18
b_data = Reference(ws, min_col=3, min_row=region_start + 1, max_row=region_end_row)
b_cats = Reference(ws, min_col=2, min_row=region_start + 2, max_row=region_end_row)
bar.add_data(b_data, titles_from_data=True)
bar.set_categories(b_cats)
ws.add_chart(bar, f"G{region_start}")

# --- Category summary table (feeds pie chart) ---
cat_start = region_end_row + 3
ws.cell(row=cat_start, column=2, value="Category-wise Revenue Share").font = Font(name=FONT_NAME, bold=True, size=12)
c_headers = ["Category", "Revenue", "Units Sold"]
for j, h in enumerate(c_headers):
    c = ws.cell(row=cat_start + 1, column=2 + j, value=h)
    c.font = HEADER_FONT
    c.fill = HEADER_FILL
for i, row in enumerate(category.itertuples(index=False), start=cat_start + 2):
    ws.cell(row=i, column=2, value=row.category)
    ws.cell(row=i, column=3, value=row.revenue).number_format = "₹#,##0"
    ws.cell(row=i, column=4, value=row.units_sold)
cat_end_row = cat_start + 1 + len(category)

pie = PieChart()
pie.title = "Revenue Share by Category"
pie.height = 8
pie.width = 12
p_data = Reference(ws, min_col=3, min_row=cat_start + 1, max_row=cat_end_row)
p_cats = Reference(ws, min_col=2, min_row=cat_start + 2, max_row=cat_end_row)
pie.add_data(p_data, titles_from_data=True)
pie.set_categories(p_cats)
ws.add_chart(pie, f"G{cat_start}")

# --- Sales rep leaderboard ---
rep_start = cat_end_row + 3
ws.cell(row=rep_start, column=2, value="Sales Rep Leaderboard (Top 10)").font = Font(name=FONT_NAME, bold=True, size=12)
rep_headers = ["Sales Rep", "Region", "Revenue", "Orders"]
for j, h in enumerate(rep_headers):
    c = ws.cell(row=rep_start + 1, column=2 + j, value=h)
    c.font = HEADER_FONT
    c.fill = HEADER_FILL
for i, row in enumerate(reps.head(10).itertuples(index=False), start=rep_start + 2):
    ws.cell(row=i, column=2, value=row.sales_rep)
    ws.cell(row=i, column=3, value=row.region)
    ws.cell(row=i, column=4, value=row.revenue).number_format = "₹#,##0"
    ws.cell(row=i, column=5, value=row.orders)

for col_letter, width in zip("BCDEF", [22, 16, 14, 16, 12]):
    ws.column_dimensions[col_letter].width = width

wb.save("Sales_Report.xlsx")
print("Saved Sales_Report.xlsx")
