---
description: Custom Skill mapping guidelines for plotting the unyts directional units network. Use this when prompted to visualize units or modify plots.py
---

# unyts Network Plotting Skill

`unyts` uses an internal mathematical topology linking directional references between units. Conversions occur through directed graphical maps tracking paths mathematically rather than through direct dictionaries.

### Requirements when updating topological infographics:
1. **Tool Restrictions:** Use the `networkx` and `matplotlib.pyplot` libraries primarily.
2. **Obtaining Node Paths**  
   Do not simulate graph traversals. Use the natively wrapped `get_path` hook mapped against the internal `unyts.converter._clean_input` and `unyts.converter._converter` functions traversing explicitly validated routes avoiding arbitrary tree traversals. Remove literal mathematical components (like divisions `/` resolving via `isinstance(node, UNode)`).
3. **Filtering Unnecessary Noise:**  
   Ignore purely aesthetic unit aliases (e.g., metric casing combinations). They evaluate a conversion function against factor `1.0`. Only include them when generating a specific path-mapping iteration representing a user's terminal entry.
4. **Bridging Networks:**  
   When visualizing multiple unit categories simultaneously via `unyts.dictionaries.dictionary`, cross-category conversions should distinctly mark bridge gaps crossing classification borders explicitly visually mapping dual-line colorization overlaps linking multiple boundaries visually.
5. **Absolute White BGs:**  
   Never assume matplotlib handles exporting/visual defaults correctly. Constrain layouts explicitly using absolute patches on plots `fig.patch.set_facecolor('white')`.
