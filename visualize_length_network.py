import networkx as nx
import matplotlib.pyplot as plt
from unyts.database import units_network
from unyts.dictionaries import dictionary

def plot_length_network():
    # Fetch all length units from the dictionary
    length_units_set = set()
    for key in dictionary:
        if 'length' in key.lower():
            length_units_set.update(dictionary[key])
    
    # Initialize a directed graph
    G = nx.DiGraph()
    
    # Traverse the unyts_network edges to find Length conversions
    for source_node, (dest_nodes, funcs) in units_network.edges.items():
        source_name = source_node.get_name()
        
        # Only attach to graph if it's a Length unit
        if source_name in length_units_set:
            G.add_node(source_name)
            
            for idx, dest_node in enumerate(dest_nodes):
                dest_name = dest_node.get_name()
                if dest_name in length_units_set:
                    # In a real scenario we could extract the exact conversion factor by calling the function `funcs[idx]` with 1
                    try:
                        factor = funcs[idx](1.0)
                        label = f" x {factor:.4g}"
                    except Exception:
                        label = ""
                    G.add_edge(source_name, dest_name, label=label)

    # Plot the conversion network
    fig, ax = plt.subplots(figsize=(16, 12))
    
    # Perfect white background as requested
    fig.patch.set_facecolor('white')
    ax.set_facecolor('white')
    
    pos = nx.spring_layout(G, k=0.5, iterations=50) # Adjust layout for better spacing
    
    # Draw nodes and edges
    nx.draw(G, pos, ax=ax,
            with_labels=True, 
            node_color='#e0f7fa', 
            node_size=2500, 
            font_size=10, 
            font_weight='bold', 
            edge_color='gray',
            arrows=True,
            arrowsize=20)
            
    # Draw edge labels (conversion factors)
    edge_labels = nx.get_edge_attributes(G, 'label')
    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_size=8, font_color='red')
    
    plt.title("Length Units Conversion Network", fontsize=16, fontweight='bold', pad=20)
    plt.tight_layout()
    plt.show()
    
    # Optionally, save the infographic
    # fig.savefig("length_units_infographic.png", dpi=300, facecolor='white', bbox_inches='tight')

if __name__ == "__main__":
    plot_length_network()
