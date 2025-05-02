---
icon: material/draw
---

# Mermaid Diagrams

Mermaid diagrams can be embedded inline.

``` mermaid
graph LR
  A[Start] --> B{Error?};
  B -->|Yes| C[Hmm...];
  C --> D[Debug];
  D --> B;
  B ---->|No| E[Yay!];

  click A "https://www.github.com" _blank

```
