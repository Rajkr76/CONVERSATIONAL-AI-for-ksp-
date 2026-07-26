"""Relationship graph extraction service for React Flow visualization."""

from app.schemas.chat import SQLResult, GraphData, GraphNode, GraphEdge


# ─── Entity column mapping ──────────────────────────────────────
ENTITY_COLUMNS = {
    "fir": {
        "id_cols": ["fir_id", "fir.id"],
        "label_cols": ["fir_number", "fir.fir_number", "title"],
        "color": "#6366f1",  # Indigo
    },
    "accused": {
        "id_cols": ["accused_id", "accused.id"],
        "label_cols": ["accused_name", "accused.name"],
        "color": "#ef4444",  # Red
    },
    "victim": {
        "id_cols": ["victim_id", "victim.id"],
        "label_cols": ["victim_name", "victim.name"],
        "color": "#22c55e",  # Green
    },
    "officer": {
        "id_cols": [
            "officer_id", "officer.id",
            "reporting_officer_id", "investigating_officer_id",
        ],
        "label_cols": ["officer_name", "officer.name", "badge_number"],
        "color": "#3b82f6",  # Blue
    },
    "location": {
        "id_cols": ["location_id", "location_history.id"],
        "label_cols": ["location_name", "location_history.location_name"],
        "color": "#f59e0b",  # Amber
    },
    "financial": {
        "id_cols": ["transaction_id", "financial_transaction.id"],
        "label_cols": ["bank_name", "from_account", "to_account"],
        "color": "#8b5cf6",  # Purple
    },
}


class GraphService:
    """Extracts entity relationships from SQL results for React Flow."""

    def extract_graph(self, result: SQLResult) -> GraphData | None:
        """Analyze SQL result columns and rows to build a relationship graph."""
        if not result.rows or not result.columns:
            return None

        columns_lower = [c.lower() for c in result.columns]

        # Detect which entity types are present
        detected_entities = {}
        for entity_type, config in ENTITY_COLUMNS.items():
            for id_col in config["id_cols"]:
                if id_col in columns_lower:
                    label_col = None
                    for lc in config["label_cols"]:
                        if lc in columns_lower:
                            label_col = lc
                            break
                    detected_entities[entity_type] = {
                        "id_col": id_col,
                        "label_col": label_col,
                        "color": config["color"],
                    }
                    break

        # Need at least 2 entity types for a relationship graph
        if len(detected_entities) < 2:
            return None

        nodes_map: dict[str, GraphNode] = {}
        edges_set: set[tuple[str, str]] = set()
        edges: list[GraphEdge] = []

        for row in result.rows[:100]:  # Limit to 100 rows
            row_lower = {k.lower(): v for k, v in row.items()}
            row_node_ids = []

            for entity_type, config in detected_entities.items():
                entity_id = row_lower.get(config["id_col"])
                if entity_id is None:
                    continue

                node_id = f"{entity_type}_{entity_id}"

                if node_id not in nodes_map:
                    label = (
                        str(row_lower.get(config["label_col"], entity_id))
                        if config["label_col"]
                        else str(entity_id)[:8]
                    )
                    nodes_map[node_id] = GraphNode(
                        id=node_id,
                        label=label,
                        type=entity_type,
                        data={
                            "color": config["color"],
                            "entity_id": str(entity_id),
                        },
                    )

                row_node_ids.append(node_id)

            # Create edges between all entities found in the same row
            for i in range(len(row_node_ids)):
                for j in range(i + 1, len(row_node_ids)):
                    edge_key = tuple(sorted([row_node_ids[i], row_node_ids[j]]))
                    if edge_key not in edges_set:
                        edges_set.add(edge_key)
                        source_type = row_node_ids[i].split("_")[0]
                        target_type = row_node_ids[j].split("_")[0]
                        edges.append(GraphEdge(
                            id=f"e_{row_node_ids[i]}_{row_node_ids[j]}",
                            source=row_node_ids[i],
                            target=row_node_ids[j],
                            label=f"{source_type} → {target_type}",
                        ))

        if not nodes_map or not edges:
            return None

        return GraphData(
            nodes=list(nodes_map.values()),
            edges=edges,
        )


# Singleton
graph_service = GraphService()
