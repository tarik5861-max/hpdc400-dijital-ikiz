# Graph Report - hpdc400  (2026-11-17)

## Corpus Check
- Corpus is ~21,180 words - fits in a single context window. You may not need a graph.

## Summary
- 244 nodes · 301 edges · 45 communities (6 shown, 39 thin omitted)
- Extraction: 99% EXTRACTED · 1% INFERRED · 0% AMBIGUOUS · INFERRED: 3 edges (avg confidence: 0.85)
- Token cost: 0 input · 0 output

## Community Hubs (Navigation)
- Community 0
- Community 1
- Community 2
- Community 3
- Community 4
- Community 5
- Community 6
- Community 7
- Community 8
- Community 9
- Community 10
- Community 11
- Community 12

## God Nodes (most connected - your core abstractions)
1. `main()` - 8 edges
2. `assemble()` - 7 edges
3. `gear_x()` - 7 edges
4. `pose_full()` - 7 edges
5. `_main_call()` - 7 edges
6. `main()` - 6 edges
7. `move()` - 6 edges
8. `_fc_exec()` - 6 edges
9. `freecad_ekran_goruntusu()` - 6 edges
10. `main()` - 5 edges

## Surprising Connections (you probably didn't know these)
- `main()` --calls--> `assemble()`  [INFERRED]
  checks/render.py → assembly/assemble.py
- `main()` --calls--> `assemble()`  [INFERRED]
  checks/check.py → assembly/assemble.py
- `main()` --calls--> `assemble()`  [INFERRED]
  checks/motion_check.py → assembly/assemble.py

## Import Cycles
- None detected.

## Communities (45 total, 39 thin omitted)

### Community 0 - "Community 0"
Cohesion: 0.09
Nodes (17): _ensure_loaded(), _fc_exec(), _freecad(), freecad_animasyon(), freecad_ekran_goruntusu(), freecad_kalip_yuksekligi_ayarla(), freecad_konum(), freecad_montaji_yukle() (+9 more)

### Community 1 - "Community 1"
Cohesion: 0.07
Nodes (10): box(), cut(), cyl(), gear_x(), move(), place(), polyprism(), rot() (+2 more)

### Community 2 - "Community 2"
Cohesion: 0.08
Nodes (25): activation_command, activation_command_timeout, added_modes, agent_interface, default_modes, encoding, excluded_apis, excluded_tools (+17 more)

### Community 3 - "Community 3"
Cohesion: 0.16
Nodes (9): assemble(), local_for(), build_part(), leaves(), load_params(), bbox_overlap(), main(), apply() (+1 more)

### Community 4 - "Community 4"
Cohesion: 0.18
Nodes (11): _ang_y(), _compose(), die_height_angles(), joints(), _mat_rx(), _mat_ry(), _mv(), pose() (+3 more)

### Community 6 - "Community 6"
Cohesion: 0.40
Nodes (5): uv, uvx, freecad, hpdc400, freecad-mcp

## Knowledge Gaps
- **2 isolated node(s):** `uvx`, `uv`
  These have ≤1 connection - possible missing edges. (Counts symbols only; 163 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **39 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `main()` connect `Community 3` to `Community 0`, `Community 1`?**
  _High betweenness centrality (0.019) - this node is a cross-community bridge._
- **Are the 3 inferred relationships involving `assemble()` (e.g. with `main()` and `main()`) actually correct?**
  _`assemble()` has 3 INFERRED edges - model-reasoned connections that need verification._
- **What connects `uvx`, `uv` to the rest of the system?**
  _2 weakly-connected nodes found - possible missing edges._
- **Should `Community 0` be split into smaller, more focused modules?**
  _Cohesion score 0.09388335704125178 - nodes in this community are weakly interconnected._
- **Why does `main()` connect `Community 3` to `Community 1`, `Community 4`?**
  _High betweenness centrality (0.011) - this node is a cross-community bridge._
- **Should `Community 1` be split into smaller, more focused modules?**
  _Cohesion score 0.0746031746031746 - nodes in this community are weakly interconnected._
- **Should `Community 2` be split into smaller, more focused modules?**
  _Cohesion score 0.07692307692307693 - nodes in this community are weakly interconnected._