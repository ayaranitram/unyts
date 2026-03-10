# Unyts Manual Generation Skill

## Purpose

This skill documents the complete workflow for generating and updating the Unyts User Manual. Use this guide when:
- Updating manual content after code changes
- Adding new chapters or sections
- Regenerating documentation after feature additions
- Troubleshooting LaTeX compilation issues
- Creating similar technical manuals for other projects

## Overview

The Unyts manual is a comprehensive technical reference combining:
- Custom TrueType fonts for professional typography
- **Improved TikZ diagrams** with circles for units and rectangles for conversion factors
- **Comprehensive appendix** with all recognized units grouped by category
- Source code extraction from Python files and Jupyter notebooks
- GUI documentation with screenshots
- Complete Python API reference
- LaTeX compilation to production-ready PDF

**Output:** 53-page Professional Technical Manual (v2.1 with corrected diagrams and appendix)  
**Compiler:** XeLaTeX (required for TrueType font support)  
**Build time:** ~10 seconds (2 passes)

---

## File Structure

```
unyts/
├── docs/
│   ├── UNYTS_User_Manual_Enhanced.tex     # Main LaTeX source (this file)
│   ├── UNYTS_User_Manual_Enhanced.pdf     # Compiled output (46 pages)
│   ├── UNYTS_User_Manual.tex              # Legacy basic manual (4 pages)
│   └── SKILL.md                           # This documentation
├── font/
│   ├── Domine/
│   │   └── Domine-VariableFont_wght.ttf   # Title font
│   ├── Saira/
│   │   └── Saira-VariableFont_wdth,wght.ttf  # Body font
│   └── Inconsolata/
│       └── Inconsolata-VariableFont_wdth,wght.ttf  # Code font
├── gallery/
│   ├── unyts_icon.png                     # Logo for cover page
│   ├── unyts_gui.png                      # GUI main window screenshot
│   ├── unyts_gui_conversion.png           # Conversion in action screenshot
│   └── unyts_gui_search_algorith_menu.png # Menu screenshot
├── src/unyts/
│   ├── network.py                         # UNode, UDigraph, Conversion classes
│   ├── searches.py                        # BFS, DFS, lean_BFS, hybrid_BFS
│   ├── database.py                        # Unit definitions (lines 420-620)
│   └── gui.py                             # Tkinter GUI, menu structure
└── unyts_demo.ipynb                       # Jupyter notebook with API examples
```

---

## LaTeX Setup

### Document Class and Packages

```latex
\documentclass[11pt,a4paper]{report}  % Use 'report' for \chapter support

% Required packages
\usepackage{fontspec}        % TrueType font support (XeLaTeX only)
\usepackage{amsmath}         % Math environments (align*, equation)
\usepackage{geometry}        % Page margins
\usepackage{hyperref}        % Clickable links, bookmarks
\usepackage{xcolor}          % Color definitions
\usepackage{listings}        % Code syntax highlighting
\usepackage{enumitem}        % Enhanced lists
\usepackage{graphicx}        % Image inclusion
\usepackage{tikz}            % Vector diagrams
\usepackage{caption}         % Figure captions
\usepackage{subcaption}      % Subfigures
\usepackage{booktabs}        % Professional tables
\usepackage{fancyhdr}        % Headers/footers

% TikZ libraries
\usetikzlibrary{arrows.meta,positioning,shapes.geometric,calc,decorations.pathreplacing}
```

### Font Configuration

**IMPORTANT:** Use XeLaTeX, not pdfLaTeX. Variable fonts handle weight variations natively.

```latex
% Set main body font
\setmainfont{Saira-VariableFont_wdth,wght.ttf}[
  Path=../font/Saira/
]

% Set title/heading font
\setsansfont{Domine-VariableFont_wght.ttf}[
  Path=../font/Domine/
]

% Set code font
\setmonofont{Inconsolata-VariableFont_wdth,wght.ttf}[
  Path=../font/Inconsolata/,
  Scale=0.95  % Slightly smaller for readability
]
```

**Note:** Removed `FakeWeight`, `Extension`, `UprightFont`, `BoldFont` options — variable fonts handle this automatically. Including them causes LaTeX3 errors with older fontspec versions.

### Color Scheme

```latex
\definecolor{unytsprimary}{RGB}{42,100,150}    % Deep blue for titles
\definecolor{unytssecondary}{RGB}{220,120,40}  % Orange for accents

% Code syntax highlighting
\definecolor{codegreen}{RGB}{0,128,0}
\definecolor{codegray}{RGB}{128,128,128}
\definecolor{codepurple}{RGB}{128,0,128}
\definecolor{backcolour}{RGB}{248,248,248}
```

### Python Code Listing Style

```latex
\lstdefinestyle{pythonstyle}{
  language=Python,
  backgroundcolor=\color{backcolour},
  commentstyle=\color{codegreen},
  keywordstyle=\color{blue},
  numberstyle=\tiny\color{codegray},
  stringstyle=\color{codepurple},
  basicstyle=\ttfamily\small,
  breakatwhitespace=false,
  breaklines=true,
  captionpos=b,
  keepspaces=true,
  numbers=left,
  numbersep=5pt,
  showspaces=false,
  showstringspaces=false,
  showtabs=false,
  tabsize=2,
  frame=single,
  rulecolor=\color{black!30}
}

% Usage:
% \begin{lstlisting}[style=pythonstyle]
% import unyts
% result = unyts.convert(100, 'cm', 'in')
% \end{lstlisting}
```

### Hyperref Configuration

```latex
\hypersetup{
  colorlinks=true,
  linkcolor=blue!60!black,
  urlcolor=blue!60!black,
  citecolor=blue!60!black,
  pdftitle={Unyts User Manual},
  pdfauthor={Martin Carlos Araya},
  pdfsubject={Unit Conversion Library},
  pdfkeywords={units, conversion, graph theory, Python}
}
```

---

## TikZ Diagram Templates

### ⚠️ FIGURE QUALITY CHECKLIST — READ BEFORE EVERY DIAGRAM CHANGE

**MANDATORY:** After ANY change to a TikZ diagram, you MUST compile the document (two XeLaTeX passes) and **visually inspect every modified figure in the output PDF**. Do NOT assume the diagram looks correct based on the code alone. TikZ layout is unpredictable — nodes overlap, text inherits wrong styles, and diagrams overflow page margins in ways that are invisible in the source code.

**Before marking a figure as done, verify ALL of the following:**

- [ ] **Page fit:** No Overfull \hbox warnings > 20pt near the figure lines
- [ ] **No overlap:** No text, node, or formula box overlaps another element
- [ ] **Style inheritance:** Legend/info text nodes explicitly override `every node` style with `rectangle, draw=none, fill=none` (see "Every Node Inheritance Trap" below)
- [ ] **Circle sizing:** Circle nodes use SHORT labels (abbreviated names) to prevent auto-expansion beyond `minimum size` (see "Circle Auto-Expansion" below)
- [ ] **Formula clearance:** Conversion formula boxes don't touch or overlap circle node borders
- [ ] **Legend placement:** Info/legend text is positioned to the LEFT of the diagram using absolute `at (x, y)` coordinates, as plain uncontained text — NOT centered below, NOT inside any shape
- [ ] **All content preserved:** Every node, edge, label, and calculation from the original design is still present — NEVER remove content to "simplify"
- [ ] **Readability:** All text is legible at print size (no `\tiny` on critical labels)
- [ ] **Two-pass compile:** Run XeLaTeX TWICE (for cross-references) and visually check the PDF

**If even ONE item fails, fix it before proceeding.**

---

### Known TikZ Pitfalls

#### Every Node Inheritance Trap

When a tikzpicture declares `every node/.style={circle, draw=blue!70, very thick, ...}`, **ALL nodes** inside that picture inherit the circle shape — including legend text, info boxes, and labels. This causes multi-line text to render inside an enormous auto-sized circle.

**Fix:** Any non-unit node (legend, label, info text) MUST explicitly override the inherited style:
```latex
\node[rectangle, draw=none, fill=none, font=\small\sffamily, align=left] at (-6.5, -3)
  {\textbf{Start:} m \\ \textbf{Goal:} in \\ \textbf{Path:} m {$\to$} yd {$\to$} ft {$\to$} in};
```
Key overrides: `rectangle` (shape), `draw=none` (no border), `fill=none` (no background).

#### Circle Auto-Expansion

`minimum size=1.8cm` only sets the MINIMUM — if the text inside is wider (e.g., "Fahrenheit"), TikZ **silently expands** the circle to fit. A 1.8cm circle with "Fahrenheit" becomes ~3cm, causing overlaps with nearby formula boxes.

**Fix:** Use abbreviated labels inside circles, with full names as separate external text nodes:
```latex
\node[unit, fill=red!20] (F) at (0, -4) {F};  % Small circle
\node[rectangle, draw=none, fill=none, font=\scriptsize\sffamily] at (0, -5.1) {Fahrenheit};  % External label
```

---

### v2.1 Visual Language and Improvements

**MAJOR UPDATE (v2.1):** All network and graph diagrams have been redesigned with the following improvements:

**Visual Distinction:**
- **Circle nodes** represent **units** (physical measurements: meter, kilogram, second, etc.)
- **Rectangle nodes** represent **conversion factors** (mathematical transformations: ×1000, ÷0.3048, etc.)
- This visual hierarchy dramatically improves diagram readability and professional appearance

**Spacing and Overlap Prevention:**
- **Previous:** `node distance=2.5cm` caused overlapping labels on complex networks
- **New:** `node distance=3.5cm and 4cm` (or larger) prevents all label overlaps
- **Tree diagrams:** `level distance=2cm` and `sibling distance=5cm` for BFS/DFS trees
- **Result:** All 7 diagrams (Figures 2.1, 3.1, 3.2, 4.1, 4.2, 4.3, 4.4) render cleanly without overlaps or missing labels

**Arrow Character Handling:**
- **Problem:** Unicode arrows (→, ←) failed to print correctly in final PDF
- **Solution:** Use LaTeX math mode arrows: `{$\to$}`, `{$\leftarrow$}`, `{$\leftrightarrow$}`
- **Advanced:** TikZ arrow lines use `-Stealth` and `very thick` style for visual clarity

**Font Improvements:**
- Unit node labels: `\sffamily\bfseries` for clarity and readability
- Larger labels: `font=\small` or `\footnotesize` to prevent small text
- Code font in conversions: `\ttfamily` for mathematical expressions

**Diagram-Specific Improvements:**

| Figure | Improvement | Previous | Current |
|--------|-------------|----------|---------|
| 2.1 (simple_digraph) | Tree layout, cleaner | Hub-and-spoke 2.5cm | Tree with 1.8cm level distance |
| 3.1 (bfs_tree) | Text placement | Center of tree (giant circle) | Left side, plain text, no container |
| 3.2 (dfs_tree) | Text placement | Center of tree (giant circle) | Left side, plain text, no container |
| 4.1 (si_length) | Hub layout, 2 rows | Single-row tree too wide | 3+3 hub: larger units above, smaller below |
| 4.2 (imperial_chain) | S-shaped layout | Linear 6 nodes, too wide | 3+3 S-shape with absolute positioning |
| 4.3 (si_imperial_bridge) | Compact horizontal | Horizontal too wide | Compact: SI left, bridge center, Imperial right |
| 4.4 (length_network_full) | Full content preserved | Missing nodes | All nodes (km,m,mm,cm,yd,ft,in,ch,mi) + full calculation |
| 4.5 (time_network) | Complete tree | Missing sub-second units | Added microseconds (μs) |
| 4.6 (temperature_network) | Compact + readable | Huge circles, formula overlap | Abbreviated labels (C,K,F,R) + external names, colored formula boxes |

### Page Width Constraint Solutions (NEW in v2.0)

**CRITICAL:** Ensure all diagrams fit within LaTeX page margins (~6.5 inches or ~16.5cm total width).

**Problem Patterns to Avoid:**
1. **Linear chains too wide:** More than 5 units in a row
2. **Dense hubs:** Central node with 6+ radial connections causes overlap
3. **Side-by-side systems:** Two parallel systems spread page width

**Solution Strategies:**

#### Strategy 1: S-Shaped Layout (for linear chains)
Use absolute positioning with stacked rows instead of single long chain:
```latex
\begin{tikzpicture}[
  unit/.style={circle, draw=orange!70, very thick, minimum size=1.2cm, font=\sffamily\bfseries, fill=orange!5},
  conversion/.style={rectangle, rounded corners, draw=red!70, very thick, font=\tiny\sffamily, fill=red!5},
  >=Stealth
]
  % Row 1 (left to right)
  \node[unit] (A) at (0, 0) {A};
  \node[unit] (B) at (3.8, 0) {B};
  \node[unit] (C) at (7.6, 0) {C};
  
  % Row 2 (right to left, chain continues)
  \node[unit] (D) at (7.6, -3) {D};
  \node[unit] (E) at (3.8, -3) {E};
  \node[unit] (F) at (0, -3) {F};
  
  % Connect rows
  \path[<->, very thick, orange!70]
    (A) edge node[conversion, above] {$\times 12$} (B)
    (B) edge node[conversion, above] {$\times 3$} (C)
    (C) edge node[conversion, right] {$\times 22$} (D)   % S-bend
    (D) edge node[conversion, above] {$\times 10$} (E)
    (E) edge node[conversion, above] {$\times 8$} (F);
\end{tikzpicture}
```
**Key:** Use `at (x, y)` absolute coordinates for precise S-bend control. 3 nodes per row at 3.8cm spacing = ~9cm width, well within 16.5cm page.

#### Strategy 2: Compact Horizontal (for bridge diagrams)
Keep SI left / bridge center / Imperial right, but use absolute positioning:
```latex
\begin{tikzpicture}[>=Stealth]
  % SI column (left)
  \node[sunit] (km) at (0, 1.5) {km};
  \node[sunit] (m)  at (0, 0) {m};
  \node[sunit] (cm) at (0, -1.5) {cm};
  
  % Bridge target (center-right)
  \node[iunit] (yd) at (5, 0) {yd};
  
  % Imperial (right, stacked to save width)
  \node[iunit] (ft) at (8.5, 0.8) {ft};
  \node[iunit] (in) at (8.5, -0.8) {in};
  
  % Bridge connection (red, prominent)
  \path[<->, red!70, ultra thick]
    (m) edge node[bridge, above] {$\times 1.0936$} (yd);
\end{tikzpicture}
```
**Key:** Stacking Imperial units vertically on the right side reduces total width from ~14cm to ~10cm.

#### Strategy 3: Hub Layout (replacing tree with many children)
When a hub node has 6+ children, split into rows above and below:
```latex
\begin{tikzpicture}[>=Stealth]
  % Center hub
  \node[unit, fill=blue!20] (m) at (0, 0) {meter};
  
  % Top row: larger units
  \node[unit] (km) at (-3.5, 2) {km};
  \node[unit] (hm) at (0, 2) {hm};
  \node[unit] (dam) at (3.5, 2) {dam};
  
  % Bottom row: smaller units
  \node[unit] (dm) at (-3.5, -2) {dm};
  \node[unit] (cm) at (0, -2) {cm};
  \node[unit] (mm) at (3.5, -2) {mm};
\end{tikzpicture>
```
**Key:** 3 nodes per row at 3.5cm spacing = ~8.2cm width. Much better than tree with `sibling distance=4.5cm` × 6 children = 22.5cm.

#### Strategy 4: Preserve All Content
**CRITICAL RULE:** When redesigning a diagram layout, NEVER remove nodes, edges, or detail.
- Keep ALL original units/nodes (even minor ones like mm, mi)
- Keep ALL conversion factors and labels
- Keep calculation legends showing full math
- Only change the LAYOUT (positioning, spacing), not the CONTENT
- If content doesn't fit: use S-shape, hub layout, or `\resizebox` — do NOT simplify

#### Strategy 5: Text/Legend Positioning
**WRONG (inherits circle style, lands in center):**
```latex
\node[below of=start, yshift=-4.5cm, draw=black, fill=white, rounded corners] {...}
% Inherits every node circle style → giant circle in middle of diagram!
```

**RIGHT (override style, position to the LEFT, no container):**
```latex
\node[rectangle, draw=none, fill=none, font=\small\sffamily, align=left] at (-6.5, -3)
  {\textbf{Start:} m \\ \textbf{Goal:} in \\ \textbf{Path:} m {$\to$} yd {$\to$} ft {$\to$} in};
```
**Key rules:**
1. `rectangle` overrides inherited `circle` shape
2. `draw=none, fill=none` removes all borders and background
3. `at (x, y)` with negative x = LEFT of diagram origin
4. `align=left` for natural text alignment
5. No `\\[0.1cm]` extra spacing needed — plain line breaks suffice

---

### Best Practice: Measuring Before Designing

Before creating a TikZ diagram, estimate its width:

**Formula:** `width ≈ (node_count - 1) × node_distance + 2cm margin`

**Examples:**
- 5 units @ 2.8cm spacing: `(5-1) × 2.8 + 2 = 13.2cm` ✓ (fits 16.5cm page)
- 6 units @ 2.8cm spacing: `(6-1) × 2.8 + 2 = 16cm` ⚠ (barely fits, risk overlap)
- 8 units @ 2.8cm spacing: `(8-1) × 2.8 + 2 = 21.6cm` ✗ (too wide, use S-shape)

**If diagram exceeds 15cm:** Apply Strategy 1-4 above; don't just make nodes smaller (text becomes unreadable).

---

### Basic Directed Graph

For illustrating graph theory concepts:

```latex
\begin{tikzpicture}[
  node distance=2cm,
  every node/.style={circle, draw=black, thick, minimum size=1cm},
  edge/.style={->, >=Stealth, thick}
]
  % Nodes
  \node[fill=green!20] (A) {A};
  \node[fill=blue!20, right of=A] (B) {B};
  \node[fill=orange!20, below of=A] (C) {C};
  
  % Edges with labels
  \draw[edge] (A) -- node[midway, above, draw=none] {×2.5} (B);
  \draw[edge] (A) -- node[midway, left, draw=none] {÷10} (C);
  \draw[edge] (B) -- node[midway, right, draw=none] {×0.04} (C);
\end{tikzpicture}
```

### Network Diagram with Highlighted Path

For showing conversion chains:

```latex
\begin{tikzpicture}[
  node distance=1.5cm and 2cm,
  unit/.style={circle, draw=blue!70, thick, fill=blue!10, minimum size=0.9cm},
  highlight/.style={circle, draw=red!70, very thick, fill=red!10, minimum size=0.9cm}
]
  % Define nodes
  \node[unit] (m) {m};
  \node[unit, right of=m] (km) {km};
  \node[highlight, below of=m] (cm) {cm};  % Highlighted
  \node[highlight, right of=cm] (in) {in}; % Highlighted
  
  % Draw edges
  \draw[->, >=Stealth, thick] (m) -- node[above] {×0.001} (km);
  \draw[->, >=Stealth, very thick, red!70] (cm) -- node[below] {×0.3937} (in);
  
  % Highlight box around conversion path
  \draw[dashed, thick, red!70, rounded corners] 
    ($(cm) + (-0.5, 0.3)$) -- ($(in) + (0.5, 0.3)$) -- 
    ($(in) + (0.5, -0.3)$) -- ($(cm) + (-0.5, -0.3)$) -- cycle;
\end{tikzpicture}
```

**Note:** Requires `\usetikzlibrary{calc}` for coordinate calculations with `$()`.

### Tree Diagrams for Search Algorithms (BFS/DFS)

**v2.0 Improvements:**
1. **Increased level distance:** `level distance=2cm` (was 1.5cm)
2. **Larger sibling spacing:** `level 1/.style={sibling distance=5cm}` (was 4cm)
3. **Thicker arrows:** `very thick, blue!70` for clarity
4. **Better node sizing:** `minimum size=1.1cm` for clear visibility
5. **Fixed arrow characters:** Use `{$\to$}` instead of Unicode arrows for reliable rendering

```latex
\begin{tikzpicture}[
  level distance=2cm,
  level 1/.style={sibling distance=5cm},
  every node/.style={circle, draw=blue!70, very thick, font=\small\sffamily\bfseries, minimum size=1.1cm, fill=blue!5},
  edge from parent/.style={draw, -Stealth, very thick, blue!70}
]
  \node[fill=green!30] (start) {m}
    child {node {km}}
    child {node[fill=yellow!30] {cm}
      child {node {mm}}
    };
  
  % Legend box
  \node[right of=start, draw=black, very thick, fill=white, rounded corners, font=\small\sffamily, align=left]
    {\textbf{Path:} m{$\to$}cm{$\to$}mm};
\end{tikzpicture}
```

**Arrow Character Fix:**
- **NEVER use:** Unicode arrow characters like `→` (causes rendering issues)
- **ALWAYS use:** `{$\to$}` or `{$\rightarrow$}` for reliable LaTeX rendering
- **Alternative:** `-Stealth` style for actual arrow lines in TikZ

### Multi-line Text in TikZ Nodes

**CRITICAL:** Must include `align=left` (or `align=center`) option for `\\` line breaks to work:

```latex
\node[draw, align=left, font=\footnotesize] at (5, 2) {
  \textbf{Start:} m \\
  \textbf{Goal:} in \\
  \textbf{Path:} m→cm→in
};
```

**Common Error:** Omitting `align=` causes `! LaTeX Error: Something's wrong--perhaps a missing \item.`

---

## Cover Page Template

```latex
\begin{titlepage}
\centering

% Logo
\includegraphics[width=0.3\textwidth]{../gallery/unyts_icon.png}

\vspace{1cm}

% Title
{\Huge\sffamily\textcolor{unytsprimary}{UNYTS User Manual}}

\vspace{0.5cm}

% Subtitle
{\Large\sffamily Graph-Based Unit Conversion Library}

\vspace{1.5cm}

% Version info
{\large Version 0.4.8}

\vspace{0.5cm}

{\large\today}

\vfill

% Author
{\large\sffamily Martín Carlos Araya}

{\small\texttt{martinaraya@gmail.com}}

\vspace{1cm}

\end{titlepage}
```

---

## Chapter Organization

### Recommended Structure

1. **Introduction** - Project overview, architecture philosophy, comparison to alternatives
2. **Directed Graph Foundation** - Core graph theory: nodes, edges, UNode, UDigraph, Conversion classes
3. **Search Algorithms** - BFS, DFS, lean_BFS, hybrid_BFS with pseudocode, diagrams, comparison tables
4. **Units Network** - Organization principles, SI/Imperial structure, network diagrams
5. **Installation** - pip install, dependencies, environment setup
6. **Quick Start** - Minimal working examples, import statements, basic conversions
7. **Graphical User Interface** - Window layout, menu options (File/Options/Help), screenshots, bidirectional conversion
8. **Python API Reference** - `convert()`, `units()`, Unit class, arithmetic, `.to()` method, module functions, custom units, FVF, density, NumPy/Pandas, uncertain units
9. **Troubleshooting** - Installation issues, conversion errors, timeout, cache corruption, logging, getting help

## Content Extraction Workflow

### From Python Source Files

1. Identify relevant modules (e.g., `network.py`, `searches.py`, `gui.py`)
2. Read specific line ranges:
   ```python
   read_file('src/unyts/network.py', startLine=50, endLine=150)
   ```
3. Extract class definitions, method signatures, docstrings
4. Adapt to LaTeX format:
   - Convert `"""docstrings"""` to paragraph text
   - Wrap code in `\begin{lstlisting}[style=pythonstyle]` blocks
   - Create comparison tables for multiple options

**Example:** GUI menu structure extraction from `gui.py` lines 750-850:
```python
# File menu
file_menu = tk.Menu(unyts_menu)
memory_menu.add_command(label='Save memory', command=save_memory)
# ...

# Options menu
options_menu.add_command(label="Set FVF", command=_set_fvf)
search_menu.add_checkbutton(label='BFS', variable=_bfs_, command=_set_bfs)
```

Transform to LaTeX:
```latex
\section{Options Menu}
\subsection{Set FVF}
For petroleum engineering workflows...
\subsection{Search Algorithm}
Select graph search algorithm:
\begin{itemize}
\item \textbf{BFS}: Standard breadth-first...
\end{itemize}
```

### From Jupyter Notebooks

1. Open `.ipynb` file (it's JSON)
2. Use `grep_search` to find relevant cells:
   ```python
   grep_search(query='convert', includePattern='unyts_demo.ipynb')
   ```
3. Extract code cells and markdown explanations
4. Convert to LaTeX:
   - Markdown headings → `\section{}` or `\subsection{}`
   - Code cells → `\begin{lstlisting}[style=pythonstyle]` blocks
   - Notebook output → inline text or comment

**Example:** From `unyts_demo.ipynb`:
```json
{
  "cell_type": "code",
  "source": [
    "from unyts import convert\n",
    "convert(100, 'cm', 'in')"
  ]
}
```

Becomes:
```latex
\begin{lstlisting}[style=pythonstyle]
from unyts import convert
convert(100, 'cm', 'in')  # → 39.37
\end{lstlisting}
```

### Screenshots Integration

1. Verify files exist in `gallery/` directory:
   ```python
   list_dir('d:/git/unyts/gallery')
   ```
2. Include in LaTeX with proper scaling:
   ```latex
   \begin{figure}[h]
   \centering
   \includegraphics[width=0.6\textwidth]{../gallery/unyts_gui.png}
   \caption{GUI main window}
   \label{fig:gui_main}
   \end{figure}
   ```
3. Reference in text: `Figure~\ref{fig:gui_main} shows...`

### Appendix with Unit Lists

**v2.0 Feature:** Comprehensive appendix of all recognized units grouped by category.

**Structure:**
- Section per unit type (Length, Mass, Time, etc.)
- List units alphabetically within each category
- Include both metric and imperial variants
- Add specialized nomenclature (petroleum, data, etc.)
- Include notes on special calculation rules (e.g., temperature offsets)

**Example Section:**
```latex
\section{Length Units}

\textbf{SI Metric:} angstrom, centimeter (cm), decimeter (dm), ..., meter (m), ...

\textbf{Imperial:} chain (ch), foot (ft), inch (in), mile (mi), yard (yd)

\textbf{Specialized:} astronomical unit (AU), light-year (ly), parsec
```

**Best Practice:** Extract unit list programmatically from `_all_units()` database, then manually categorize and sort for better organization than database iteration order.

---

## Compilation Workflow

### Prerequisites

- **Compiler:** XeLaTeX (not pdfLaTeX)
  - Windows: MiKTeX or TeX Live
  - Linux: `sudo apt-get install texlive-xetex texlive-fonts-extra`
  - Mac: MacTeX

- **Packages:** All listed packages must be installed via package manager

### Compilation Commands

```powershell
# Navigate to docs folder
cd docs

# First pass: Build document structure
xelatex -interaction=nonstopmode UNYTS_User_Manual_Enhanced.tex

# Second pass: Resolve cross-references and TOC
xelatex -interaction=nonstopmode UNYTS_User_Manual_Enhanced.tex
```

**Flags:**
- `-interaction=nonstopmode`: Don't stop on errors (useful for automated builds)
- Alternative: `-halt-on-error`: Stop immediately on first error (useful for debugging)

### Expected Output

```
Output written on UNYTS_User_Manual_Enhanced.pdf (54 pages).
```

**Page count breakdown (v2.0 with improved diagrams):**
- Cover: 1
- TOC: 2-3
- Chapter 1-2: 5-8
- Chapter 3: 6-8
- Chapter 4: 4-6
- Chapters 5-6: 3-4
- Chapter 7: 6-8
- Chapter 8: 10-12
- Chapter 9: 4-6
- Appendix A (Units Reference): 8 pages (~1 page per section)

**Size:** ~1.2 MB (optimized for readability)

### Troubleshooting Compilation Errors

#### FakeWeight Error

**Error:**
```
! LaTeX3 Error: The key 'fontspec-opentype/FakeWeight' is unknown and is being ignored.
```

**Cause:** Older fontspec versions don't support `FakeWeight` option

**Fix:** Remove font configuration options — variable fonts handle weight natively:
```latex
% Bad (causes error):
\setmainfont{Saira.ttf}[FakeWeight=2]

% Good:
\setmainfont{Saira-VariableFont_wdth,wght.ttf}[Path=../font/Saira/]
```

#### Missing \item Error

**Error:**
```
! LaTeX Error: Something's wrong--perhaps a missing \item.
l.557     {\textbf{Start:} m \\ \textbf{Goal:} in
```

**Cause:** Multi-line text in TikZ node without `align` option

**Fix:** Add `align=left` or `align=center`:
```latex
\node[draw, align=left] {Line 1 \\ Line 2};
```

#### Environment Undefined

**Error:**
```
! LaTeX Error: Environment align* undefined.
```

**Cause:** Missing `amsmath` package

**Fix:** Add to preamble:
```latex
\usepackage{amsmath}
```

#### File Not Found

**Error:**
```
! LaTeX Error: File `../gallery/unyts_icon.png' not found.
```

**Cause:** Incorrect relative path or missing asset

**Fix:**
1. Verify file exists: `ls ../gallery/unyts_icon.png`
2. Check path is relative to `.tex` file location
3. Use forward slashes `/` even on Windows (LaTeX convention)

---

## Updating the Manual

### Adding New Content

1. **New section within existing chapter:**
   ```latex
   \section{New Feature Name}
   
   Description of the feature...
   
   \subsection{Usage}
   \begin{lstlisting}[style=pythonstyle]
   # Code example
   \end{lstlisting}
   ```

2. **New chapter:**
   ```latex
   \chapter{Advanced Topics}
   
   Introduction to the chapter...
   
   \section{First Topic}
   Content here...
   ```
   Add to TOC automatically (report class handles this).

3. **New TikZ diagram:**
   - Start with template from this SKILL
   - Test in minimal document first if complex
   - Use consistent colors (`unytsprimary`, `unytssecondary`)
   - Include `\caption{}` and `\label{fig:unique_name}`

### After Code Changes

1. **Update API sections** if function signatures changed:
   - Re-read docstrings from source files
   - Update parameter lists
   - Revise examples if behavior changed

2. **Regenerate screenshots** if GUI changed:
   - Launch `python -m unyts`
   - Take screenshots with consistent window size
   - Save as PNG in `gallery/`
   - Update `\includegraphics{}` paths if renamed

3. **Refresh examples** from demo notebook:
   - Re-run `unyts_demo.ipynb` to verify outputs
   - Update LaTeX code blocks if results differ
   - Add new notebook cells to Chapter 8 if new features added

4. **Increment version** on title page:
   ```latex
   {\large Version 0.4.9}  % Update this
   {\large\today}          % Auto-updates to compilation date
   ```

### Testing Changes

1. **Incremental compilation:** After each major section edit:
   ```powershell
   xelatex -interaction=nonstopmode UNYTS_User_Manual_Enhanced.tex
   ```
   Check log for errors before continuing.

2. **Visual inspection:** Open PDF, verify:
   - Fonts render correctly (no "missing character" boxes)
   - Diagrams appear as expected (no overlap, correct colors)
   - Screenshots visible and properly scaled
   - Code syntax highlighting works (colors present)
   - Links clickable (test Table of Contents links)
   - Page numbers continuous

3. **Cross-references:** After second pass, click `Figure~\ref{}` links → should jump to figure.

---

## Best Practices

### LaTeX Writing

1. **Label everything important:**
   ```latex
   \section{Core Concepts}
   \label{sec:concepts}
   
   \begin{figure}[h]
   \caption{Network diagram}
   \label{fig:network}
   \end{figure}
   ```
   Reference with `\ref{sec:concepts}` or `Figure~\ref{fig:network}`.

2. **Use semantic spacing:**
   ```latex
   % Good: Readable structure
   \section{Title}
   
   First paragraph.
   
   Second paragraph.
   
   % Bad: Cluttered
   \section{Title}
   First paragraph.
   Second paragraph.
   ```

3. **Escape special characters:**
   - `_` → `\_` (underscore)
   - `%` → `\%` (percent)
   - `#` → `\#` (hash)
   - `$` → `\$` (dollar)
   - But inside `\verb` or `lstlisting`, they're literal.

4. **Use `\texttt{}` for inline code:**
   ```latex
   The \texttt{convert()} function accepts floats.
   Call it like \texttt{convert(100, 'cm', 'm')}.
   ```

### Diagram Quality and Reporting (NEW in v2.0)

**Professional diagram requirements:**
1. **Fit on page:** All content visible without horizontal scrolling or wrapping
2. **Readability:** Text sizes minimum 9pt, no overlapping labels
3. **Visual hierarchy:** Clear distinction between node types (circles vs rectangles)
4. **Clarity of paths:** All arrows/edges visible; no hidden connections
5. **Color consistency:** Use defined color scheme; avoid random colors
6. **Legend/explanation:** Complex diagrams include text box explaining key elements
7. **Caption accuracy:** Caption describes what's shown; matches figure content

**Quality checklist for each diagram:**
- [ ] Figure fits within page margins (test by compiling)
- [ ] All node labels readable (no font size < 9pt)
- [ ] All arrows visible (no overlapping edges or nodes)
- [ ] Text boxes positioned below/outside diagram (not overlapping)
- [ ] Colors consistent with v2.0 color scheme
- [ ] Caption matches diagram content
- [ ] Any highlighted path has corresponding legend
- [ ] Unit nodes same size; conversion nodes proportional

**Common issues and fixes:**
| Issue | Sign | Fix |
|-------|------|-----|
| Diagram too wide | Node labels cut off or wrap | Use S-shape or vertical layout |
| Overlapping labels | Text unreadable, on top of other nodes | Increase `node distance` or use tree layout |
| Arrows hidden | Can't see all edges | Reduce number of edges or use `bend left/right` |
| Text covers nodes | Info box obscures diagram | Move text box below with `yshift=-5cm` |
| Colors inconsistent | Mixes blue!70, blue, blue!20 randomly | Use defined styles (`unit/.style={...}`) |
| No path explanation | Complex path unclear to reader | Add legend box with conversion steps |

---

### TikZ Diagrams

1. **Consistent styling:** Define node/edge styles once:
   ```latex
   \begin{tikzpicture}[
     mynode/.style={circle, draw=blue, fill=blue!10, minimum size=1cm},
     myedge/.style={->, >=Stealth, thick}
   ]
   \node[mynode] (A) {A};
   \draw[myedge] (A) -- (B);
   \end{tikzpicture}
   ```

2. **Relative positioning:** Use `right of=`, `below of=` instead of absolute coordinates:
   ```latex
   % Good: Scalable
   \node (A) {A};
   \node[right of=A] (B) {B};
   
   % Bad: Brittle
   \node at (0,0) (A) {A};
   \node at (2,0) (B) {B};
   ```

3. **Test complex diagrams separately:**
   Create standalone file:
   ```latex
   \documentclass{standalone}
   \usepackage{tikz}
   \usetikzlibrary{positioning}
   \begin{document}
   \begin{tikzpicture}
   % Your diagram here
   \end{tikzpicture}
   \end{document}
   ```
   Compile: `xelatex test_diagram.tex`  
   Once working, integrate into main manual.

### Version Control

1. **Commit often:** After each major section completed:
   ```bash
   git add docs/UNYTS_User_Manual_Enhanced.tex
   git commit -m "Add Chapter 7: GUI documentation with screenshots"
   ```

2. **Don't commit generated files:**
   ```gitignore
   # .gitignore
   *.aux
   *.log
   *.toc
   *.out
   *.pdf  # Or commit PDF separately
   ```

3. **Tag releases:**
   ```bash
   git tag -a manual-v0.4.8 -m "User manual for Unyts v0.4.8"
   git push origin manual-v0.4.8
   ```

---

## Common Pitfalls

| Issue | Symptom | Solution |
|-------|---------|----------|
| **Wrong compiler** | Fonts missing, box placeholders | Use `xelatex`, not `pdflatex` |
| **Missing package** | `! LaTeX Error: File ... not found` | Install via MiKTeX Console or `tlmgr install <package>` |
| **Absolute paths** | Compilation fails on other machines | Use relative paths: `../font/`, `../gallery/` |
| **Single compilation pass** | TOC empty, `??` for references | Run `xelatex` **twice** |
| **Outdated .aux files** | Incorrect page numbers | Delete `.aux`, `.toc`, `.out` files, recompile |
| **TikZ overflow** | Diagrams cut off | Add `trim left=<coords>` or reduce `node distance` |
| **Code line wrap** | Code exceeds margin | Use `basicstyle=\ttfamily\footnotesize` in listings |
| **Unicode issues** | Strange characters | Ensure `.tex` file saved as UTF-8 |

---

## Automation Script (PowerShell)

Save as `build_manual.ps1`:

```powershell
# Build Unyts enhanced manual
Set-Location -Path "docs"

Write-Host "=== Building Unyts User Manual ===" -ForegroundColor Cyan

# First pass
Write-Host "`n[1/2] First XeLaTeX pass..." -ForegroundColor Yellow
xelatex -interaction=nonstopmode UNYTS_User_Manual_Enhanced.tex
if ($LASTEXITCODE -ne 0) {
    Write-Host "Error in first pass, check log file" -ForegroundColor Red
    exit 1
}

# Second pass for TOC/cross-refs
Write-Host "`n[2/2] Second XeLaTeX pass..." -ForegroundColor Yellow
xelatex -interaction=nonstopmode UNYTS_User_Manual_Enhanced.tex
if ($LASTEXITCODE -ne 0) {
    Write-Host "Error in second pass, check log file" -ForegroundColor Red
    exit 1
}

# Check output
if (Test-Path "UNYTS_User_Manual_Enhanced.pdf") {
    $fileInfo = Get-Item "UNYTS_User_Manual_Enhanced.pdf"
    $sizeKB = [math]::Round($fileInfo.Length / 1KB, 2)
    Write-Host "`n✓ Success! Generated:" -ForegroundColor Green
    Write-Host "  File: UNYTS_User_Manual_Enhanced.pdf"
    Write-Host "  Size: $sizeKB KB"
    
    # Extract page count from log
    $logContent = Get-Content "UNYTS_User_Manual_Enhanced.log" -Raw
    if ($logContent -match 'Output written .* \((\d+) pages\)') {
        Write-Host "  Pages: $($matches[1])"
    }
} else {
    Write-Host "✗ PDF not generated, compilation failed" -ForegroundColor Red
    exit 1
}

Write-Host "`n=== Build Complete ===" -ForegroundColor Cyan
```

**Usage:**
```powershell
.\build_manual.ps1
```

---

## Quick Reference Commands

```powershell
# Compile from scratch
cd docs
xelatex -interaction=nonstopmode UNYTS_User_Manual_Enhanced.tex
xelatex -interaction=nonstopmode UNYTS_User_Manual_Enhanced.tex

# Clean build artifacts
Remove-Item *.aux, *.log, *.toc, *.out, *.lof, *.lot

# View compilation errors
Select-String -Path UNYTS_User_Manual_Enhanced.log -Pattern "^!"

# Check page count
Select-String -Path UNYTS_User_Manual_Enhanced.log -Pattern "Output written"

# Find undefined references
Select-String -Path UNYTS_User_Manual_Enhanced.log -Pattern "undefined"

# Test TikZ diagram standalone
xelatex -interaction=nonstopmode test_diagram.tex
```

---

## Maintenance Checklist

**After each Unyts release:**

- [ ] Update version number on title page
- [ ] Update `\today` if using fixed date
- [ ] Re-run demo notebook, verify outputs unchanged (or update manual examples)
- [ ] Check for new API functions in `__init__.py`
- [ ] Regenerate GUI screenshots if interface changed
- [ ] Review docstrings for updates (especially `convert()`, `units()`)
- [ ] Recompile: `xelatex` × 2
- [ ] Visual inspection of PDF (fonts, diagrams, screenshots, code)
- [ ] Test all hyperlinks (TOC, cross-references, URLs)
- [ ] Commit to version control with descriptive message
- [ ] Tag release: `git tag manual-v0.4.9`

**Quarterly:**
- [ ] Review manual structure for obsolete sections
- [ ] Check for broken external URLs (GitHub, demo notebook)
- [ ] Update troubleshooting section with common new issues
- [ ] Verify font files still accessible (licensing, path)
- [ ] Test compilation on fresh machine (VM or CI)

---

## Resources

- **XeLaTeX Documentation:** https://www.overleaf.com/learn/latex/XeLaTeX
- **TikZ Manual:** https://tikz.dev/ or `texdoc tikz` in terminal
- **fontspec Package:** `texdoc fontspec`
- **Unyts Repository:** https://github.com/ayaranitram/unyts
- **MiKTeX Package Manager:** https://miktex.org/packages
- **TeX StackExchange:** https://tex.stackexchange.com/ (for troubleshooting)

---

## Contact

**Maintainer:** Martín Carlos Araya  
**Email:** martinaraya@gmail.com  
**GitHub:** https://github.com/ayaranitram/unyts

For questions about this skill or manual generation workflow, open an issue on GitHub or contact via email.

---

**Skill Version:** 1.0  
**Last Updated:** 2026-03-05  
**Compatible with:** Unyts v0.4.8+
