---
icon: material/drawing-box
---

# Kroki Diagrams

**Kroki has proven unreliable in CI** therefore we no longer recommend its use.
It will be removed as soon as the last existing diagrams have a local renderer.
For diagrams that do not have a local renderer we will need to export them manually and
embed both the source and rendered image file inside the docs themselves.

<!-- cspell: words blockdiag -->

## Kroki Mermaid

* No Links
* Stand alone SVG

* Fails with 504 as at 8 March 2024

<!-- markdownlint-disable code-fence-style-->

~~~md
```kroki-mermaid theme=forest
  flowchart LR
    A[Start] -> B{Error?};
    B ->|Yes| C[Hmm...];
    C -> D[Debug];
    D -> B;
    B ->|No| E[Yay!];
```
~~~
<!-- markdownlint-enable code-fence-style-->

## Other types

* Fails with 500 as at 8 March 2024

<!-- markdownlint-disable code-fence-style-->
~~~md
```kroki-blockdiag no-transparency=false size=1000x400
  blockdiag {
    blockdiag -> generates -> "block-diagrams";
    blockdiag -> is -> "very easy!!";

    blockdiag [color = "greenyellow"];
    "block-diagrams" [color = "pink"];
    "very easy!!" [color = "orange"];
  }
```
~~~
<!-- markdownlint-enable code-fence-style-->
