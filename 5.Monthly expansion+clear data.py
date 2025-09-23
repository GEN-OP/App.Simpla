import pandas as pd
import os
from dateutil.rrule import rrule, MONTHLY
from datetime import datetime
from dateutil.relativedelta import relativedelta

# Paths
input_excel_path = r"C:\Users\george.nadrag\00. Coduri structurate\04. Date si validare XLSX\4.transformed_data.xlsx"
output_excel_path = r"C:\Users\george.nadrag\00. Coduri structurate\05. Monthly Split Logic\5.expanded_monthly_rows.xlsx"
os.makedirs(os.path.dirname(output_excel_path), exist_ok=True)

COLUMNS_TO_DROP = [
    'validation_issues', 'invoice_number_confidence', 'invoice_date_confidence',
    'vendor_name_confidence', 'items_details_confidence', 'total_amount_confidence',
    'total_without_vat_confidence', 'currency_confidence', 'vat_amount_confidence',
    'Unnamed: 10', 'considered', 'vat_valid', 'date_serv_start', 'date_serv_end'
]

def calculate_prorated_value(total_value, days_in_month, total_days):
    if total_days == 0:
        return 0
    return round((total_value / total_days) * days_in_month, 2)

def fallback_to_invoice_month(row):
    invoice_date = pd.to_datetime(row['invoice_date'], dayfirst=True)
    month_start = invoice_date.replace(day=1)
    row['Luna Serviciu'] = month_start.strftime('%d/%m/%Y')
    row['Valoare Considerata'] = row['total_without_vat']
    row['SPLIT'] = 0
    return [row]

def split_invoice_by_month(row):
    if row.get('considered') != 1:
        return []

    start_date_str = row.get('date_serv_start')
    end_date_str = row.get('date_serv_end')
    total_without_vat = row.get('total_without_vat', 0)

    if pd.isna(start_date_str) or pd.isna(end_date_str) or start_date_str == 'N/A' or end_date_str == 'N/A':
        return fallback_to_invoice_month(row)

    try:
        start_date = pd.to_datetime(start_date_str, dayfirst=True).date()
        end_date = pd.to_datetime(end_date_str, dayfirst=True).date()
    except Exception:
        return fallback_to_invoice_month(row)

    if start_date > end_date:
        return fallback_to_invoice_month(row)

    if start_date.year == end_date.year and start_date.month == end_date.month:
        row['Valoare Considerata'] = total_without_vat
        row['Luna Serviciu'] = start_date.replace(day=1).strftime('%d/%m/%Y')
        row['SPLIT'] = 0
        return [row]

    expanded_rows = []
    splits = list(rrule(MONTHLY, dtstart=start_date, until=end_date))
    monthly_days = {}

    # Count actual days per month in the interval
    current_day = start_date
    while current_day <= end_date:
        key = current_day.replace(day=1)
        monthly_days[key] = monthly_days.get(key, 0) + 1
        current_day += pd.Timedelta(days=1)

    total_days = sum(monthly_days.values())
    value_accumulator = 0

    for i, (month_start, days) in enumerate(monthly_days.items()):
        prorated = calculate_prorated_value(total_without_vat, days, total_days)
        if i == len(monthly_days) - 1:
            prorated = round(total_without_vat - value_accumulator, 2)
        else:
            value_accumulator += round(prorated, 2)

        new_row = row.copy()
        new_row['Valoare Considerata'] = prorated
        new_row['Luna Serviciu'] = month_start.strftime('%d/%m/%Y')
        new_row['SPLIT'] = 1
        expanded_rows.append(new_row)

    return expanded_rows

def main():
    try:
        df = pd.read_excel(input_excel_path)
        print(f"✅ Loaded {len(df)} rows from input.")
    except Exception as e:
        print(f"❌ Failed to read input file: {e}")
        return

    df_considered = df[df['considered'] == 1].copy()
    total_input_sum = df_considered['total_without_vat'].sum()

    rows = []
    for _, row in df.iterrows():
        rows.extend(split_invoice_by_month(row))

    df_expanded = pd.DataFrame(rows)
    df_expanded.drop(columns=[col for col in COLUMNS_TO_DROP if col in df_expanded.columns], inplace=True, errors='ignore')

    total_output_sum = df_expanded['Valoare Considerata'].sum()
    diff = round(total_output_sum - total_input_sum, 2)

    try:
        df_expanded.to_excel(output_excel_path, index=False)
        print(f"✅ Saved {len(df_expanded)} rows to: {output_excel_path}")
        print(f"📊 Total CONSIDERED input total_without_vat: {total_input_sum:.2f}")
        print(f"📊 Total output Valoare Considerata: {total_output_sum:.2f}")
        print(f"🔍 Difference: {diff:.2f}")
    except Exception as e:
        print(f"❌ Error saving output: {e}")

if __name__ == "__main__":
    main()
