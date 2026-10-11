"""Export reconciled Power BI input tables from prepared UCI retail lines."""
import argparse
import json
from decimal import Decimal
from pathlib import Path
import pandas as pd


def export(data, output):
    data = data.copy()
    data['invoice_date'] = pd.to_datetime(data.invoice_date, errors='raise')
    data['month'] = data.invoice_date.dt.to_period('M').dt.to_timestamp()
    data['value'] = [Decimal(str(p)) * int(q) for p, q in zip(data.unit_price, data.quantity)]
    window = data.invoice_date.ge('2010-12-01') & data.invoice_date.lt('2011-12-01')
    sales = data.loc[window & data.eligible_sale].copy()
    cancellations = data.loc[window & data.eligible_cancellation].copy()
    for col in ['country', 'customer_id', 'month']:
        assert sales.groupby('invoice_no')[col].nunique(dropna=False).max() == 1, f'Invoice has multiple {col} values'
    customer_first = sales.loc[sales.has_customer_id].groupby('customer_id').month.min()
    sales = sales.join(customer_first.rename('first_month'), on='customer_id')
    sales['customer_group'] = 'Unknown customer'
    sales.loc[sales.has_customer_id & sales.month.eq(sales.first_month), 'customer_group'] = 'First observed purchase month'
    sales.loc[sales.has_customer_id & sales.month.gt(sales.first_month), 'customer_group'] = 'Returning customer'
    orders = sales.groupby('invoice_no', sort=True).agg(
        order_date=('invoice_date', 'min'), month=('month', 'first'),
        country=('country', 'first'), customer_id=('customer_id', 'first'),
        customer_group=('customer_group', 'first'), sales_value_gbp=('value', 'sum'),
        units=('quantity', 'sum'), eligible_lines=('source_row', 'size'),
    ).reset_index()
    cancellations['cancellation_value_gbp'] = -cancellations.value
    cancels = cancellations.groupby(['month', 'country']).cancellation_value_gbp.sum().reset_index()
    countries = pd.DataFrame({'country': sorted(set(orders.country) | set(cancels.country))})
    months = pd.DataFrame({'month': pd.date_range('2010-12-01', '2011-11-01', freq='MS')})
    months['month_label'] = months.month.dt.strftime('%b %Y')
    months['month_sort'] = months.month.dt.year * 100 + months.month.dt.month
    customer_months = sales.loc[sales.has_customer_id, ['customer_id', 'month']].drop_duplicates()
    cohort_data = customer_months.join(customer_first.rename('cohort_month'), on='customer_id')
    sizes = customer_first.value_counts().sort_index()
    activity = cohort_data.groupby(['cohort_month', 'month']).size()
    cohorts = pd.DataFrame([
        {'cohort_month': cohort, 'activity_month': month,
         'months_since_first_observed_purchase': (month.year-cohort.year)*12 + month.month-cohort.month,
         'cohort_size': int(size), 'active_customers': int(activity.get((cohort, month), 0))}
        for cohort, size in sizes.items()
        for month in pd.date_range(cohort, '2011-11-01', freq='MS')
    ])
    stocks = sales.groupby('stock_code').agg(sales_value_gbp=('value', 'sum'), units=('quantity', 'sum'), orders=('invoice_no', 'nunique')).reset_index()
    total = sum(orders.sales_value_gbp, Decimal(0))
    counts = orders.loc[orders.customer_id.notna()].groupby('customer_id').invoice_no.nunique()
    summary = {
        'window': '2010-12-01 inclusive to 2011-12-01 exclusive',
        'sales_value_gbp': str(total), 'cancellation_value_gbp': str(sum(cancels.cancellation_value_gbp, Decimal(0))),
        'orders': len(orders), 'average_order_value_gbp': str(total/len(orders)),
        'identifiable_customers': len(counts), 'repeat_customers': int(counts.ge(2).sum()),
        'repeat_purchase_rate': int(counts.ge(2).sum()) / len(counts),
        'power_query_executed': False, 'dax_executed': False, 'powerbi_report_created': False,
        'validation': 'Exported table metrics reconciled in Python. Power Query, DAX and report rendering require verification in Power BI.',
    }
    assert total == sum(sales.value, Decimal(0)) == sum(stocks.sales_value_gbp, Decimal(0))
    assert orders.invoice_no.is_unique
    assert cohorts.active_customers.le(cohorts.cohort_size).all()
    output.mkdir(parents=True, exist_ok=True)
    for name, table in [('FactOrders', orders), ('FactCancellations', cancels), ('DimMonth', months), ('DimCountry', countries), ('Cohorts', cohorts), ('StockSales', stocks)]:
        table.to_csv(output / f'{name}.csv', index=False, date_format='%Y-%m-%d')
    (output.parent / 'validation.json').write_text(json.dumps(summary, indent=2)+'\n')
    return summary


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('input', type=Path)
    parser.add_argument('--output-dir', type=Path, default=Path('powerbi/data'))
    args = parser.parse_args()
    frame = pd.read_csv(args.input, dtype={'invoice_no':'string', 'stock_code':'string', 'customer_id':'string'})
    print(json.dumps(export(frame, args.output_dir), indent=2))
