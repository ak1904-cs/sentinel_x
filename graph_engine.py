# graph_engine.py
from pyvis.network import Network
import streamlit.components.v1 as components  # For app integration
import pandas as pd
import nltk
from nltk import pos_tag, word_tokenize
from collections import defaultdict, Counter
import re

# REVISION: Download NLTK data if needed (run once in your environment)
try:
    nltk.data.find('tokenizers/punkt')
    nltk.data.find('taggers/averaged_perceptron_tagger')
except LookupError:
    nltk.download('punkt')
    nltk.download('averaged_perceptron_tagger')

def extract_entities(df, text_column='clean_text', top_n=15):
    """
    Extract top entities (nouns/keywords) from the DataFrame using NLTK POS tagging.
    For OSINT threat profiling: Nouns proxy for actors/locations (e.g., "jihad", "ISIS").
    
    Args:
        df (pd.DataFrame): Input DataFrame.
        text_column (str): Text column (default: 'clean_text' from data_loader).
        top_n (int): Number of top entities.
    
    Returns:
        list: Top entities.
    """
    if df.empty or text_column not in df.columns:
        return []
    
    all_nouns = []
    for text in df[text_column].dropna().astype(str):
        tokens = word_tokenize(text)
        tagged = pos_tag(tokens)
        # Focus on nouns (NN/NNP) as entity proxies
        nouns = [word.lower() for word, pos in tagged if pos.startswith('NN')]
        all_nouns.extend(nouns)
    
    # Filter noise (stop words, short/non-alpha)
    stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'is', 'are'}
    filtered_nouns = [
        n for n in all_nouns 
        if n not in stop_words and len(n) > 2 and re.match(r'^[a-zA-Z]+$', n)
    ]
    
    return [word for word, _ in Counter(filtered_nouns).most_common(top_n)]

def build_relationships(df, entities, text_column='clean_text', min_cooccur=2):
    """
    Build co-occurrence edges: Connect entities in the same post >= min_cooccur times.
    For radicalization: E.g., "isis" and "recruitment" linked if co-mentioned.
    
    Args:
        df (pd.DataFrame): Input DataFrame.
        entities (list): Entities to connect.
        text_column (str): Text column.
        min_cooccur (int): Min co-occurrences for an edge.
    
    Returns:
        list: [(src, dst, weight)] tuples.
    """
    cooccur = defaultdict(lambda: defaultdict(int))
    
    for text in df[text_column].dropna().astype(str):
        present_entities = [ent for ent in entities if ent in text.lower()]
        for i in range(len(present_entities)):
            for j in range(i + 1, len(present_entities)):
                src, dst = present_entities[i], present_entities[j]
                cooccur[src][dst] += 1
                cooccur[dst][src] += 1  # Undirected graph
    
    relationships = []
    for src in cooccur:
        for dst in cooccur[src]:
            weight = cooccur[src][dst]
            if weight >= min_cooccur:
                relationships.append((src, dst, weight))
    
    return relationships

def build_graph(entities=None, relationships=None, df=None, text_column='clean_text', top_n=15, min_cooccur=2, use_dummy=False):
    """
    Build PyVis network. Supports your original (entities/relationships lists) or DF-based (extracts automatically).
    
    Args:
        entities (list, optional): Pre-extracted entities.
        relationships (list, optional): Pre-built edges.
        df (pd.DataFrame, optional): If provided, extracts entities/relationships (for app integration).
        text_column (str): Text column if using DF.
        top_n (int): Top entities if extracting.
        min_cooccur (int): Min co-occurrences if extracting.
        use_dummy (bool): If True, use your original dummy relationships (for testing).
    
    Returns:
        str: HTML string for the graph (use with components.html).
    """
    # REVISION: Handle both original style (lists) and new DF style
    if df is not None:
        if df.empty:
            raise ValueError("DataFrame is empty. No graph to build.")
        entities = entities or extract_entities(df, text_column, top_n)
        relationships = relationships or build_relationships(df, entities, text_column, min_cooccur)
        if use_dummy and len(entities) > 1:
            # Fallback to your original dummy logic
            relationships = [(entities[i], entities[j]) for i in range(len(entities)) for j in range(i+1, len(entities)) if i % 2 == 0]
    
    if not entities or len(entities) < 2:
        raise ValueError("Need at least 2 entities for a graph.")
    
    if not relationships:
        # Add minimal connections if none
        relationships = [(entities[0], entities[1])] if len(entities) >= 2 else []
    
    # REVISION: Risk coloring if DF provided (aggregate from 'risk_category')
    colors = {'High': 'red', 'Moderate': 'orange', 'Low': 'green', 'Unknown': 'gray'}
    node_colors = {ent: 'gray' for ent in entities}
    node_titles = {ent: f"Entity: {ent}" for ent in entities}
    
    if df is not None and 'risk_category' in df.columns:
        entity_risk = defaultdict(list)
        for _, row in df.iterrows():
            text_lower = row[text_column].lower()
            for ent in entities:
                if ent in text_lower:
                    entity_risk[ent].append(row['risk_category'])
        
        for ent in entities:
            if entity_risk[ent]:
                majority = Counter(entity_risk[ent]).most_common(1)[0][0]
                node_colors[ent] = colors.get(majority, 'gray')
                node_titles[ent] += f"\nRisk: {majority} (appears in {len(entity_risk[ent])} posts)"
    
    # Build network (your original style, enhanced)
    net = Network(height="600px", width="100%", bgcolor="#111", font_color="white", directed=False)
    
    for ent in entities:
        net.add_node(ent, label=ent, title=node_titles[ent], color=node_colors[ent], size=25)
    
    for src, dst in relationships:
        weight = 1  # Default
        # If relationships have weights (from cooccur), use them
        if isinstance(relationships[0], tuple) and len(relationships[0]) == 3:
            for r_src, r_dst, w in relationships:
                if (r_src == src and r_dst == dst) or (r_dst == src and r_src == dst):
                    weight = w
                    break
        net.add_edge(src, dst, value=weight, title=f"Connection strength: {weight}")
    
    # REVISION: Generate HTML string directly (no file save/read)
    net_html = net.generate_html(notebook=False)
    
    # Optional: Tweak HTML for better Streamlit fit
    net_html = net_html.replace(
        '<div id="mynetwork"></div>', 
        '<div id="mynetwork" style="width: 100%; height: 600px; border: 1px solid #333;"></div>'
    )
    
    return net_html

# REVISION: Updated display_graph to use the new build_graph (for backward compat)
def display_graph(df, text_column="text"):
    """
    Display graph in Streamlit. Uses 'clean_text' by default for better results.
    """
    try:
        # REVISION: Call the enhanced build_graph with DF
        graph_html = build_graph(df=df, text_column=text_column or 'clean_text')
        components.html(graph_html, height=600, scrolling=True)
    except Exception as e:
        # Fallback warning (import streamlit as st if using outside app)
        print(f"Graph generation failed: {e}")  # Or st.warning if in app context
