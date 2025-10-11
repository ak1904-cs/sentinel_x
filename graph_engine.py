from pyvis.network import Network
import streamlit.components.v1 as components
import pandas as pd

def build_graph(entities, relationships):
    net = Network(height="600px", width="100%", bgcolor="#111", font_color="white")

    for e in entities:
        net.add_node(e, label=e, title=e)

    for src, dst in relationships:
        net.add_edge(src, dst)

    return net

def display_graph(df, text_column="text"):
    """
    Creates a simple co-occurrence graph for top words in the dataset.
    """
    # Extract top keywords
    text = " ".join(df[text_column].astype(str))
    words = pd.Series(text.split()).value_counts().head(10).index.tolist()

    # Create dummy relationships
    relationships = [(words[i], words[j]) for i in range(len(words)) for j in range(i+1, len(words)) if i % 2 == 0]

    net = build_graph(words, relationships)
    net.save_graph("graph.html")

    # Show inside Streamlit
    html_file = open("graph.html", "r", encoding="utf-8")
    components.html(html_file.read(), height=600)
