---
icon: material/draw
---

# Graphviz Diagrams

## Graphviz SVG's

=== "Trees"
<!-- markdownlint-disable no-inline-html -->
    <center>
<!-- markdownlint-enable no-inline-html -->

    ```dot
    graph G {
      size="1.8"
      node [shape=circle, fontname="fira code", fontsize=28, penwidth=3]
      edge [penwidth=3]
      "-" -- {"x", "+"} 
      "x" -- 3 [weight=2]
      "x" -- 5
      "+" -- 2
      "+" -- 4 [weight=2]
    }
    ```

    <figcaption><b>Tree 1: Tree of Arithmetic Expressions</b></figcaption>

    ```dot
    graph G {
      size="3"
      forcelabels=true
      node [shape=circle, fontname="fira code", fontsize=24, penwidth=3];
      edge [penwidth=3]
      5 -- {4, 32} [color=red]
      31, 32 [label="3"]
      21, 22, 23 [label="2"]
      11, 12, 13, 14, 15 [label="1"]
      01, 02, 03, 04, 05, 06, 07, 08 [label="0"]
      4 -- 31 [color=blue, weight=2]
      4 -- 22 [color=blue]
      31 -- 21 [color=red, weight=3]
      31 -- 12 [color=red]
      32 -- 23 [color=blue]
      32 -- 15 [color=blue, weight=2]
      21 -- 11 [color=blue, weight=3]
      21 -- 02 [color=blue]
      11 -- 01 [color=red]
      12 -- 03 [color=blue]
      22 -- 13 [color=red]
      22 -- 05 [color=red, weight=2]
      13 -- 04 [color=blue]
      23 -- {14, 07} [color=red]
      14 -- 06 [color=blue]
      15 -- 08 [color=red]
      07, 08 [shape=doublecircle]
    }
    ```

    <figcaption><b>Tree 2: Game Tree (of Nim)</b></figcaption>

    </center>

=== "Graphs"

    <center>

    ```dot
    graph G {
      size="2";
      bgcolor=none;
      node [shape=circle, fontsize=30, style=bold];
      edge [style=bold, fontsize=30]
      4 -- 0
      4 -- 0
      4 -- 1
      0 -- 2
      0 -- 2
      0 -- 2
      2 -- 2
      0 -- 3
      1 -- 2
      1 -- 3
      1 -- 1
    }
    ```

    <figcaption>An Unweighted<br/>Undirected<br/>Multi-graph (with loops)</figcaption>

    ```dot
    digraph G {
        size="8"
        node [shape=circle, fontsize=38]
        edge [arrowhead=none]
        subgraph cluster0 {
          0 -> 1
          2, 0, 3, 8, 11, 10 [color=blue, style=bold]
          0 -> 2 [color=blue, style=bold]
          0 -> 3 [color=blue, style=bold]
          2 -> 3
          8 -> 9
          2 -> 9
          8 -> 3 [color=blue, style=bold]
          0 -> 4 -> 10
          10 -> 11 [color=blue, style=bold]
          8 -> 11 [color=blue, style=bold]
          subgraph cluster00 {
            1, 5, 6 [color=red, style=bold]
            1 -> 5 [color=red, style=bold]
            1 -> 6 [color=red, style=bold]
            5 -> 6 [color=red, style=bold]
            label="cycle"
            fontcolor=red
            fontsize=38
            {rank = same; 5; 6;}
          }
        6 -> 7
        2 -> 8
        3 -> 9
        label = "Related Component";
        fontsize=38
        {rank = same; 2; 3;}
        {rank = same; 8; 9;}
        }

        subgraph cluster1 {
        15 -> 16 -> 17
        16 -> 18 -> 19
        label="Related Component"
        fontsize=38
        }

        subgraph cluster2 {
        20 -> 21 -> 22
        20 -> 23
        21 -> 23
        23 -> 24
        label="Related Component"
        fontsize=38
        }
    }
    ```

    <figcaption>
    Graph G Undirected Unweighted Unrelated  
    </figcaption>

## Graphviz inside Admonitions

???- note "graphviz in UnExpanded Block"

    ```dot
    {{ include_file('src/appendix/examples/diagrams/invasion_plan.dot', indent=4) }}
    ```

???+ note "graphviz in Expanded Block"

    ```dot
    {{ include_file('src/appendix/examples/diagrams/invasion_plan.dot', indent=4) }}
    ```

## Graphviz PNG's (lower quality than SVGs)

=== "Graphviz Render"

    ```graphviz dot attack_plan.png
    {{ include_file('src/appendix/examples/diagrams/invasion_plan.dot', indent=4) }}
    ```

=== "Example of Code Syntax"

    **SYNTAX (WATCHOUT) :** NO SPACES BETWEEN ` ``` ` and `graphviz`

    ~~~
    ``` graphviz dot attack_plan.png
    {{ include_file('src/appendix/examples/diagrams/invasion_plan.dot', indent=4) }}
    ```
    ~~~
