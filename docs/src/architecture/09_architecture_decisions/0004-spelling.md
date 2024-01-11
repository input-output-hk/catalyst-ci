---
    title: 0004 Spelling
    adr:
        author: Steven Johnson
        created: 09-Jan-2024
        status:  accepted
        extends:
            - 0003-language
    tags:
        - Spelling
---

## Context

Any project contains a large amount of human readable text.
The team is multi-national and it can not be assumed that everyone has a strong
skills with the primary language of the project.

## Assumptions

That everyone on the team has a reasonable grasp of the primary language of the project.

## Decision

That the spelling of the Primary Language will be enforced in CI using:

* [CSpell]
* US English dictionaries
* Technical words
* Custom words on a pre-project basis

Secondary Languages which are used in translating the UI, will also be checked with [CSpell].

## Risks

* That a dictionary for a Secondary language does not exist for CSpell.

It is possible to use custom dictionaries with [CSpell].  
If a standard dictionary does not exist, a custom language dictionary can be added.
This risk is mitigated.

## Consequences

Enforcing spelling in CI helps enforce consistency of all Human Readable text.
By using automation we ensure this consistency, regardless of a contributors proficiency with the primary language

`cspell`

## More Information

* [CSpell]

[CSpell]: http://cspell.org/
