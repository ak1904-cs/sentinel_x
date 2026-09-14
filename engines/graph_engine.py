"""
Risk-Aware Entity Relationship Graph Engine for Sentinel-X.
Generates interactive PyVis network graphs with risk-colored nodes, entity metadata tooltips,
and weighted relationship edges.
"""
import pandas as pd
from collections import defaultdict, Counter
from pyvis.network import Network
import streamlit.components.v1 as components
from engines.entity_engine import get_entity_engine
from utils.logging_utils import get_logger

logger = get_logger("graph_engine")

def extract_dataframe_entities_and_relationships(df: pd.DataFrame, text_column: str = 'clean_text', top_n: int = 25, min_cooccur: int = 1) -> tuple[list, list, dict]:
    """
    Extract entities and co-occurrence relationships from DataFrame rows using spaCy NER.
    Returns (entities_list, relationships_tuples, entity_risk_map).
    """
    if df.empty or text_column not in df.columns:
        return [], [], {}

    entity_engine = get_entity_engine()
    entity_counts = Counter()
    entity_risk_list = defaultdict(list)
    doc_entities_list = []

    for _, row in df.iterrows():
        text = str(row[text_column]) if pd.notna(row[text_column]) else ""
        risk_cat = row.get('risk_category', 'Low')
        
        extracted = entity_engine.extract_entities(text)
        doc_ents = set()
        
        for ent_info in extracted["entities"]:
            ent_name = ent_info["text"]
            doc_ents.add(ent_name)
            entity_counts[ent_name] += 1
            entity_risk_list[ent_name].append(risk_cat)
            
        doc_entities_list.append(list(doc_ents))

    # Top N entities by frequency
    top_entities = [word for word, _ in entity_counts.most_common(top_n)]
    top_entities_set = set(top_entities)

    # Determine majority risk level for each entity
    entity_risk_map = {}
    for ent in top_entities:
        risks = entity_risk_list[ent]
        if risks:
            entity_risk_map[ent] = Counter(risks).most_common(1)[0][0]
        else:
            entity_risk_map[ent] = "Low"

    # Co-occurrence relationships
    cooccur = defaultdict(int)
    for doc_ents in doc_entities_list:
        valid_ents = [e for e in doc_ents if e in top_entities_set]
        for i in range(len(valid_ents)):
            for j in range(i + 1, len(valid_ents)):
                pair = tuple(sorted([valid_ents[i], valid_ents[j]]))
                cooccur[pair] += 1

    relationships = [(src, dst, weight) for (src, dst), weight in cooccur.items() if weight >= min_cooccur]
    return top_entities, relationships, entity_risk_map

def build_interactive_graph(df: pd.DataFrame = None, entities: list = None, relationships: list = None, text_column: str = 'clean_text', top_n: int = 25, height: str = "600px") -> str:
    """
    Build PyVis network HTML string with risk-aware node styling.
    """
    entity_risk_map = {}
    if df is not None and not df.empty:
        col = text_column if text_column in df.columns else ('clean_text' if 'clean_text' in df.columns else df.columns[0])
        extracted_ents, extracted_rel, entity_risk_map = extract_dataframe_entities_and_relationships(df, text_column=col, top_n=top_n)
        entities = entities or extracted_ents
        relationships = relationships or extracted_rel

    if not entities or len(entities) < 2:
        # Fallback dummy entities for visual demonstration if dataset has < 2 entities
        entities = ["Target Entity A", "Organization X", "Location Alpha", "Incident Site"]
        relationships = [("Target Entity A", "Organization X", 3), ("Organization X", "Location Alpha", 2), ("Target Entity A", "Incident Site", 4)]
        entity_risk_map = {"Target Entity A": "High", "Organization X": "High", "Location Alpha": "Moderate", "Incident Site": "Low"}

    colors_map = {'High': '#FF4B4B', 'Moderate': '#FFA500', 'Low': '#00C853', 'Unknown': '#888888'}

    net = Network(height=height, width="100%", bgcolor="#0E1117", font_color="#FFFFFF", directed=False)

    for ent in entities:
        risk_cat = entity_risk_map.get(ent, 'Low')
        node_color = colors_map.get(risk_cat, '#888888')
        node_title = f"Entity: {ent}\nRisk Level: {risk_cat}"
        net.add_node(ent, label=ent, title=node_title, color=node_color, size=28)

    for rel in relationships:
        if len(rel) == 3:
            src, dst, weight = rel
        else:
            src, dst = rel[0], rel[1]
            weight = 1
        net.add_edge(src, dst, value=weight, title=f"Co-occurrence strength: {weight}", color="#4A5568")

    net_html = net.generate_html(notebook=False)
    net_html = net_html.replace(
        '<div id="mynetwork"></div>',
        f'<div id="mynetwork" style="width: 100%; height: {height}; border: 1px solid #262730; border-radius: 8px;"></div>'
    )
    return net_html

def display_graph_in_streamlit(df: pd.DataFrame, text_column: str = 'clean_text', height: int = 600):
    """Render interactive network graph inside Streamlit container."""
    try:
        html_content = build_interactive_graph(df=df, text_column=text_column, height=f"{height}px")
        components.html(html_content, height=height + 20, scrolling=True)
    except Exception as e:
        logger.error(f"Failed to render Streamlit network graph: {e}")
