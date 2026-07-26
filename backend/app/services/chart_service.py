"""Chart auto-detection service — analyzes SQL results to pick the best chart type."""

from app.schemas.chat import SQLResult, ChartData


class ChartService:
    """Analyzes SQL result columns and data to auto-select chart visualization."""

    # Column name heuristics for chart type detection
    TIME_KEYWORDS = {"date", "month", "year", "week", "day", "quarter", "time", "period"}
    CATEGORY_KEYWORDS = {"type", "status", "category", "name", "station", "district", "rank", "gender", "severity"}
    NUMERIC_KEYWORDS = {"count", "total", "sum", "avg", "average", "amount", "number", "percentage", "rate"}

    def detect_chart_type(self, result: SQLResult) -> ChartData | None:
        """Analyze SQL result and return chart configuration if applicable."""
        if not result.rows or not result.columns or len(result.columns) < 2:
            return None

        columns = [c.lower() for c in result.columns]

        # Identify column roles
        label_col = None
        value_cols = []
        is_time_series = False

        for i, col in enumerate(columns):
            col_lower = col.lower()
            if any(kw in col_lower for kw in self.TIME_KEYWORDS):
                label_col = i
                is_time_series = True
            elif any(kw in col_lower for kw in self.CATEGORY_KEYWORDS):
                if label_col is None:
                    label_col = i
            elif any(kw in col_lower for kw in self.NUMERIC_KEYWORDS):
                value_cols.append(i)
            else:
                # Check if values are numeric
                sample_values = [
                    row.get(result.columns[i])
                    for row in result.rows[:5]
                    if row.get(result.columns[i]) is not None
                ]
                if sample_values and all(
                    isinstance(v, (int, float)) or (
                        isinstance(v, str) and v.replace(".", "").replace("-", "").isdigit()
                    )
                    for v in sample_values
                ):
                    value_cols.append(i)
                elif label_col is None:
                    label_col = i

        # Defaults
        if label_col is None:
            label_col = 0
        if not value_cols:
            # Use all non-label numeric columns
            for i in range(len(columns)):
                if i != label_col:
                    value_cols.append(i)

        if not value_cols:
            return None

        # Extract labels
        labels = [
            str(row.get(result.columns[label_col], ""))
            for row in result.rows[:50]
        ]

        # Build datasets
        colors = [
            "rgba(99, 102, 241, 0.8)",   # Indigo
            "rgba(244, 63, 94, 0.8)",     # Rose
            "rgba(34, 197, 94, 0.8)",     # Green
            "rgba(251, 146, 60, 0.8)",    # Orange
            "rgba(168, 85, 247, 0.8)",    # Purple
        ]

        datasets = []
        for idx, col_i in enumerate(value_cols[:5]):
            col_name = result.columns[col_i]
            data = []
            for row in result.rows[:50]:
                val = row.get(col_name, 0)
                try:
                    data.append(float(val) if val is not None else 0)
                except (ValueError, TypeError):
                    data.append(0)

            datasets.append({
                "label": col_name,
                "data": data,
                "backgroundColor": colors[idx % len(colors)],
                "borderColor": colors[idx % len(colors)].replace("0.8", "1"),
                "borderWidth": 2,
            })

        # Determine chart type
        num_categories = len(set(labels))
        chart_type = self._pick_chart_type(
            num_categories=num_categories,
            is_time_series=is_time_series,
            num_datasets=len(datasets),
            row_count=len(result.rows),
        )

        # Build title
        value_names = [result.columns[c] for c in value_cols[:3]]
        label_name = result.columns[label_col]
        title = f"{', '.join(value_names)} by {label_name}"

        return ChartData(
            chart_type=chart_type,
            title=title.title(),
            labels=labels,
            datasets=datasets,
        )

    def _pick_chart_type(
        self,
        num_categories: int,
        is_time_series: bool,
        num_datasets: int,
        row_count: int,
    ) -> str:
        """Heuristically pick the best chart type."""
        if is_time_series:
            return "line" if num_datasets <= 3 else "area"

        if num_categories <= 6 and num_datasets == 1:
            return "pie"

        if num_categories <= 20:
            return "bar"

        return "area"


# Singleton
chart_service = ChartService()
