import yaml  # type: ignore
import csv
from typing import List, Dict, Any, Optional
from datetime import datetime
from collections import defaultdict
import statistics


class SemanticLayer:
    def __init__(self, yaml_path: str):
        with open(yaml_path, 'r') as f:
            self.config = yaml.safe_load(f)['semantic_layer']
        self.metrics = {m['name']: m for m in self.config['measures']}
        self.dimensions = {d['name']: d for d in self.config['dimensions']}
        self.filters = {f['name']: f for f in self.config['filters']}

    def get_schema_for_agent(self) -> Dict[str, Any]:
        return {
            "available_measures": [
                {"name": m['name'], "display_name": m['display_name'],
                 "description": m['description'], "format": m['format']}
                for m in self.config['measures']
            ],
            "available_dimensions": [
                {"name": d['name'], "type": d['type'],
                 "granularity": d.get('granularity', [])}
                for d in self.config['dimensions']
            ],
            "available_filters": [
                {"name": f['name'], "condition": f['condition']}
                for f in self.config['filters']
            ]
        }

    def get_metric_definition(self, metric_name: str) -> Optional[Dict]:
        return self.metrics.get(metric_name)


class QueryExecutor:
    def __init__(self, csv_path: str, semantic_layer: SemanticLayer):
        self.semantic = semantic_layer
        self.rows = []
        with open(csv_path, 'r', newline='') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if not row.get('date') or not row.get('transaction_id'):
                    continue
                try:
                    row['date'] = datetime.strptime(row['date'], '%Y-%m-%d')
                    row['usd_price'] = float(row['usd_price'] or 0)
                    row['local_price'] = float(row['local_price'] or 0)
                    row['cost'] = float(row['cost'] or 0)
                    row['shipping_cost_usd'] = float(row['shipping_cost_usd'] or 0)
                    row['discount_usd'] = float(row['discount_usd'] or 0)
                    row['units_sold'] = int(row['units_sold'] or 0)
                    row['exchange_rate_to_usd'] = float(row['exchange_rate_to_usd'] or 1)
                    row['gdp_per_capita_usd'] = float(row['gdp_per_capita_usd'] or 0)
                    row['population_millions'] = float(row['population_millions'] or 0)
                    self.rows.append(row)
                except (ValueError, TypeError):
                    continue

    def execute(self, measures: List[str], dimensions: List[str] = None,
                filters: List[str] = None) -> Dict[str, Any]:
        dimensions = dimensions or []
        filters = filters or []

        filtered = self.rows
        applied_filters = []
        for f_name in filters:
            f_def = self.semantic.filters.get(f_name)
            if not f_def:
                continue
            condition = f_def['condition']
            if "region = 'North America'" in condition:
                filtered = [r for r in filtered if r['region'] == 'North America']
            elif "region = 'South America'" in condition:
                filtered = [r for r in filtered if r['region'] == 'South America']
            elif "region = 'Europe'" in condition:
                filtered = [r for r in filtered if r['region'] == 'Europe']
            elif "region = 'Asia'" in condition:
                filtered = [r for r in filtered if r['region'] == 'Asia']
            elif "region = 'Oceania'" in condition:
                filtered = [r for r in filtered if r['region'] == 'Oceania']
            elif "region = 'Africa'" in condition:
                filtered = [r for r in filtered if r['region'] == 'Africa']
            elif "region = 'Middle East'" in condition:
                filtered = [r for r in filtered if r['region'] == 'Middle East']
            elif "date >= '2024-07-01' AND date <= '2024-09-30'" in condition:
                filtered = [r for r in filtered if datetime(2024, 7, 1) <= r['date'] <= datetime(2024, 9, 30)]
            elif "product_category = 'Electronics'" in condition:
                filtered = [r for r in filtered if r['product_category'] == 'Electronics']
            elif "product_category = 'Clothing'" in condition:
                filtered = [r for r in filtered if r['product_category'] == 'Clothing']
            elif "product_category = 'Home & Garden'" in condition:
                filtered = [r for r in filtered if r['product_category'] == 'Home & Garden']
            applied_filters.append(f_name)

        def get_group_key(row):
            key = {}
            for dim in dimensions:
                if dim == 'time':
                    key['time_month'] = row['date'].strftime('%Y-%m')
                elif dim == 'geography':
                    key['region'] = row['region']
                    key['country'] = row['country']
                elif dim == 'region':
                    key['region'] = row['region']
                elif dim == 'country':
                    key['country'] = row['country']
                elif dim == 'product_category':
                    key['product_category'] = row['product_category']
            return tuple(sorted(key.items()))

        groups = defaultdict(list)
        for row in filtered:
            groups[get_group_key(row)].append(row)

        results = []
        for group_key, group_rows in groups.items():
            record = {}
            for k, v in group_key:
                record[k] = v

            if 'country' in record and group_rows:
                record['currency'] = group_rows[0]['currency']
                record['country_code'] = group_rows[0]['country_code']
                record['exchange_rate'] = group_rows[0]['exchange_rate_to_usd']

            for measure in measures:
                m_def = self.semantic.metrics.get(measure)
                if not m_def:
                    continue
                sql_expr = m_def['sql_expression']

                if sql_expr == "SUM(usd_price)":
                    record['revenue_usd'] = round(sum(r['usd_price'] for r in group_rows), 2)
                elif sql_expr == "SUM(local_price)":
                    record['revenue_local'] = round(sum(r['local_price'] for r in group_rows), 2)
                elif sql_expr == "SUM(cost)":
                    record['cost'] = round(sum(r['cost'] for r in group_rows), 2)
                elif sql_expr == "SUM(shipping_cost_usd)":
                    record['shipping_cost'] = round(sum(r['shipping_cost_usd'] for r in group_rows), 2)
                elif sql_expr == "SUM(discount_usd)":
                    record['discount'] = round(sum(r['discount_usd'] for r in group_rows), 2)
                elif sql_expr == "SUM(units_sold)":
                    record['units_sold'] = sum(r['units_sold'] for r in group_rows)
                elif sql_expr == "SUM(usd_price - discount_usd)":
                    record['net_revenue'] = round(sum(r['usd_price'] - r['discount_usd'] for r in group_rows), 2)
                elif sql_expr == "SUM(cost + shipping_cost_usd)":
                    record['total_cost'] = round(sum(r['cost'] + r['shipping_cost_usd'] for r in group_rows), 2)
                elif sql_expr == "SUM(usd_price - discount_usd - cost - shipping_cost_usd)":
                    record['margin'] = round(sum(r['usd_price'] - r['discount_usd'] - r['cost'] - r['shipping_cost_usd'] for r in group_rows), 2)
                elif sql_expr == "AVG(usd_price)":
                    record['avg_price_usd'] = round(sum(r['usd_price'] for r in group_rows) / len(group_rows), 2)
                elif sql_expr == "AVG(local_price)":
                    record['avg_price_local'] = round(sum(r['local_price'] for r in group_rows) / len(group_rows), 2)
                elif sql_expr == "COUNT(*)":
                    record['transaction_count'] = len(group_rows)
                elif sql_expr == "AVG(gdp_per_capita_usd)":
                    record['gdp_per_capita'] = round(sum(r['gdp_per_capita_usd'] for r in group_rows) / len(group_rows), 2)
                elif sql_expr == "SUM(population_millions)":
                    record['population'] = round(sum(r['population_millions'] for r in group_rows), 2)
                elif sql_expr == "AVG(usd_price / gdp_per_capita_usd)":
                    record['price_per_gdp'] = round(sum(r['usd_price'] / r['gdp_per_capita_usd'] for r in group_rows) / len(group_rows) * 100, 4)

            if 'margin_pct' in measures and 'margin' in record and 'net_revenue' in record:
                record['margin_pct'] = round(record['margin'] / record['net_revenue'] * 100, 2) if record['net_revenue'] else 0

            results.append(record)

        if results:
            sort_key = list(results[0].keys())[0]
            results = sorted(results, key=lambda x: x.get(sort_key, ''))

        return {
            "data": results,
            "metadata": {
                "row_count": len(results),
                "measures_queried": measures,
                "dimensions_queried": dimensions,
                "filters_applied": applied_filters,
                "api_payload": {"measures": measures, "dimensions": dimensions, "filters": applied_filters},
                "governance_note": "All metrics computed via semantic layer definitions."
            }
        }

    def detect_anomalies(self, dimension: str = 'country', measure: str = 'avg_price_usd'):
        data = self.execute([measure], [dimension], [])['data']
        values = [r[measure] for r in data if measure in r and not isinstance(r[measure], str)]
        if len(values) < 3:
            return []
        mean = statistics.mean(values)
        std = statistics.stdev(values) if len(values) > 1 else 0
        threshold = 1.5 * std
        anomalies = []
        for row in data:
            val = row.get(measure)
            if val is None:
                continue
            diff = abs(val - mean)
            if diff > threshold:
                anomalies.append({
                    **row,
                    'mean': round(mean, 2),
                    'std': round(std, 2),
                    'z_score': round(diff / std, 2) if std else 0,
                    'deviation_pct': round((diff / mean) * 100, 1) if mean else 0
                })
        return sorted(anomalies, key=lambda x: x['z_score'], reverse=True)

    def forecast_revenue(self, periods: int = 3):
        monthly = self.execute(['revenue_usd'], ['time'], [])['data']
        if len(monthly) < 2:
            return []
        monthly = sorted(monthly, key=lambda x: x['time_month'])
        values = [r['revenue_usd'] for r in monthly]
        n = len(values)
        if n < 2:
            return []
        x_mean = sum(range(n)) / n
        y_mean = sum(values) / n
        numerator = sum((i - x_mean) * (values[i] - y_mean) for i in range(n))
        denominator = sum((i - x_mean) ** 2 for i in range(n))
        slope = numerator / denominator if denominator else 0
        intercept = y_mean - slope * x_mean
        last_month = monthly[-1]['time_month']
        forecasts = []
        for i in range(1, periods + 1):
            year, month = int(last_month[:4]), int(last_month[5:])
            month += i
            year += (month - 1) // 12
            month = ((month - 1) % 12) + 1
            pred_month = f"{year}-{month:02d}"
            pred_value = max(0, round(intercept + slope * (n - 1 + i), 2))
            forecasts.append({'time_month': pred_month, 'forecast_revenue_usd': pred_value, 'trend': 'up' if slope > 0 else 'down'})
        return forecasts

    def price_elasticity(self, country: str = None):
        filtered = [r for r in self.rows if not country or r['country'] == country]
        by_category = defaultdict(list)
        for r in filtered:
            by_category[r['product_category']].append(r)
        results = []
        for category, rows in by_category.items():
            if len(rows) < 2:
                continue
            avg_price = sum(r['usd_price'] for r in rows) / len(rows)
            total_units = sum(r['units_sold'] for r in rows)
            results.append({
                'product_category': category,
                'avg_price_usd': round(avg_price, 2),
                'total_units_sold': total_units,
                'elasticity_score': round(total_units / avg_price * 1000, 2)
            })
        return sorted(results, key=lambda x: x['elasticity_score'], reverse=True)