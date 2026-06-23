import json
import pandas as pd
import networkx as nx
import os

# Load the raw memory logs
file_path = os.path.join("..", "data", "urban_memory_logs.json")
with open(file_path, "r") as f:
    data = json.load(f)

df = pd.DataFrame(data)

# Aggregate edges just like the visualizer does
edges = df.groupby(['location', 'urban_context', 'violation_type']).size().reset_index(name='weight')

# Build NetworkX Graph
G = nx.Graph()
for _, row in edges.iterrows():
    loc = row['location']
    context = row['urban_context']
    violation = row['violation_type']
    weight = int(row['weight']) # ensure JSON serializable
    
    G.add_node(loc, group="Location", id=loc)
    G.add_node(context, group="Context", id=context)
    G.add_node(violation, group="Violation", id=violation)
    
    # The Causality Path
    G.add_edge(context, violation, weight=weight)
    G.add_edge(violation, loc, weight=weight)

# Convert to a JSON-friendly format
graph_data = nx.node_link_data(G)

# Export directly to the strategist_ai folder
out_path = os.path.join("..", "strategist_ai", "causality_graph.json")
with open(out_path, "w") as f:
    json.dump(graph_data, f, indent=4)

print(f"Exported graph data to {out_path}")
