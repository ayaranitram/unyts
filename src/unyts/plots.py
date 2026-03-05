import networkx as nx
import matplotlib.pyplot as plt
from typing import Union, List, Tuple

# Import strictly internal calculation & network methods natively
from unyts.converter import _clean_input, _converter
from unyts.database import units_network
from unyts.dictionaries import dictionary
from unyts.network import UNode

def get_path(from_unit: str, to_unit: str) -> list:
    """
    Returns the conversion path from one unit to another
    following the same search algorithm of the main converter.
    """
    # Use unyts's internal algorithm to trace exactly how the path traverses
    _, f_unit, t_unit = _clean_input(1, from_unit, to_unit)
    _, path = _converter(1, f_unit, t_unit)
    return path

def _get_node_category(node_name: str) -> str:
    """Finds the root category dict key (type) of a unit."""
    for key, values in dictionary.items():
        base_cat = key.split('_')[0]
        if isinstance(values, (list, tuple, set)) and node_name in values:
            return base_cat
        elif isinstance(values, dict):
            if node_name in values:
                return base_cat
            for v_list in values.values():
                if node_name in v_list:
                    return base_cat
    return 'Unknown'

def _is_alias(conv_func) -> bool:
    """Checks if a conversion function mathematically evaluates to an identity factor (1)."""
    try:
        return conv_func(1.0) == 1.0
    except Exception:
        return False

def plot_network(unit_types: Union[str, List[str]] = None, path_pair: Tuple[str, str] = None):
    """
    Plots the unyts conversion network based on parameters:
    a) unit_types: Unit categories like 'Length'. Colors by category mode, removes aliases.
    b) path_pair: Provide (from_unit, to_unit). Highlights strictly their conversion path 
       calculating exact algorithm sequence via get_path (keeps inclusive aliases).
    c) (None): Plats everything, utilizing dashed dual-colored links bridging different domains.
    """
    G = nx.DiGraph()
    
    if isinstance(unit_types, str):
        unit_types = [unit_types]
        
    path_nodes = []
    if path_pair is not None:
        raw_path = get_path(path_pair[0], path_pair[1])
        if raw_path:
            # Drop structural arithmetic operators, keeping strictly standard UNode components
            path_nodes = [n.get_name() for n in raw_path if isinstance(n, UNode)]
            
    # Iterate across unit_network mappings natively populated inside database.py
    for src_node, connections in units_network.edges.items():
        src_name = src_node.get_name()
        src_cat = _get_node_category(src_name)
        
        if path_pair is not None and src_name not in path_nodes:
            continue
            
        if path_pair is None and unit_types is not None and src_cat not in unit_types:
            continue
            
        G.add_node(src_name, category=src_cat)
        
        children, convs = connections
        for child, conv in zip(children, convs):
            child_name = child.get_name()
            child_cat = _get_node_category(child_name)
            
            if path_pair is not None and child_name not in path_nodes:
                continue
                
            if path_pair is None and unit_types is not None and child_cat not in unit_types:
                continue
                
            is_alias = _is_alias(conv)
            
            # Remove aliases only if NOT traversing a specific directed path logic 
            if path_pair is None and is_alias:
                continue
                
            G.add_edge(src_name, child_name, is_alias=is_alias, src_cat=src_cat, dst_cat=child_cat)

    if not len(G.nodes):
        print("No nodes found for the given criteria.")
        return

    # Base Color Layout Setup
    categories = sorted(list(set(nx.get_node_attributes(G, 'category').values())))
    cmap = plt.get_cmap('tab20')
    cat_colors = {cat: cmap(i / max(1, len(categories))) for i, cat in enumerate(categories)}
    node_colors = [cat_colors.get(data['category'], 'gray') for node, data in G.nodes(data=True)]

    # Rigid figure sizing and clean forced white backing (Requested Style)
    fig, ax = plt.subplots(figsize=(16, 12))
    fig.patch.set_facecolor('white')
    ax.set_facecolor('white')

    pos = nx.spring_layout(G, k=0.6, iterations=55, seed=42)

    # General plot definitions
    nx.draw_networkx_nodes(G, pos, ax=ax, node_color=node_colors, node_size=1000, alpha=0.9, edgecolors='white', linewidths=2)
    nx.draw_networkx_labels(G, pos, ax=ax, font_size=8, font_weight='bold')

    if path_pair is not None:
        # Option B: Replot strict ordered connections of sequence logic specifically 
        path_edges = [(path_nodes[i], path_nodes[i+1]) for i in range(len(path_nodes)-1) if G.has_edge(path_nodes[i], path_nodes[i+1])]
        nx.draw_networkx_edges(G, pos, ax=ax, edgelist=path_edges, edge_color='red', width=3.0, arrows=True, arrowsize=20)
    
    elif unit_types is not None:
        # Option A: Normal edges filtering
        nx.draw_networkx_edges(G, pos, ax=ax, edge_color='gray', width=1.0, alpha=0.6, arrows=True, arrowsize=15)
        
    else:
        # Option C: Universal map bridge layering
        normal_edges = []
        bridge_edges = []
        for u, v, data in G.edges(data=True):
            if data['src_cat'] != data['dst_cat']:
                bridge_edges.append((u, v, data))
            else:
                normal_edges.append((u, v))
                
        nx.draw_networkx_edges(G, pos, ax=ax, edgelist=normal_edges, edge_color='lightgray', alpha=0.5, arrows=True, arrowsize=10)
        
        # Dual-Colored Double Dashed Lines Implementation for bridge transitions
        for u, v, data in bridge_edges:
            src_c = cat_colors.get(data['src_cat'], 'gray')
            dst_c = cat_colors.get(data['dst_cat'], 'gray')
            # Outer layer path
            nx.draw_networkx_edges(G, pos, ax=ax, edgelist=[(u, v)], edge_color=[dst_c], width=5.0, style='dashed', alpha=0.9, arrows=True, arrowsize=15)
            # Inner inverse layer path
            nx.draw_networkx_edges(G, pos, ax=ax, edgelist=[(u, v)], edge_color=[src_c], width=2.0, style='dashed', alpha=1.0, arrows=False)

    # Re-draw layout bounds manually
    handles = [plt.Line2D([0], [0], marker='o', color='w', markerfacecolor=color, markersize=12, label=cat)
               for cat, color in cat_colors.items()]
    plt.legend(handles=handles, title="Unit Categories", loc='best', fancybox=True, shadow=True, title_fontsize=12)

    plt.title("Unyts Mathematical Conversion Map", fontsize=20, fontweight='bold', pad=20)
    plt.axis("off")
    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    # Remove aliases and chart specifically Length units only (Requirement A)
    # plot_network(unit_types='Length')
    
    # Render specifically algorithmic conversion line (Requirement B)
    # plot_network(path_pair=('km', 'ft'))
    
    # Generate massive visualization mapping complete system bridging (Requirement C)
    # plot_network()
    pass