# Python Coding Standard Review Rules

**Plugin:** coding-standard  
**Version:** 1.0  

## Checklist

| # | Rule ID | Description | Severity | Check Criteria | Expected Result |
|---|---------|-------------|----------|----------------|-----------------|
| 1 | STD-001 | Variable and Function Naming — snake_case | P2 | All variable and function names must follow `snake_case` convention | No camelCase or PascalCase for non-class identifiers; exceptions: loop vars (i, j, k), constants |
| 2 | STD-002 | Class Naming — PascalCase | P2 | All class names must follow `PascalCase` convention with descriptive nouns | No abbreviations without definition; no single-letter class names except in well-known contexts (e.g., Node) |
| 3 | STD-003 | Constant Definitions — ALL_CAPS | P2 | Module-level constants must be declared in `ALL_UPPERCASE` with underscore separators | Constants are defined at module level; no inline magic numbers without named constant assignment |
| 4 | STD-004 | No Dead Code or Commented-Out Blocks | P3 | Audit files for commented-out code blocks longer than 5 lines without an explanation | Dead code is removed or wrapped in `# TODO:` / `# FIXME:` comments with a tracking issue reference |
| 5 | STD-005 | Function Length — Max 40 Lines per Function | P2 | Verify that no function exceeds 40 lines of executable code (excluding docstrings and blank lines) | Long functions are refactored into smaller units; extract helper methods for clarity |
| 6 | STD-006 | Import Organization — Standard Library, Third Party, Local | P3 | Check import ordering: stdlib → third-party → local project imports, each group sorted alphabetically | Imports are grouped and sorted; no unused imports remain |
| 7 | STD-007 | Docstrings Present for All Public APIs | P2 | Every public function and class must have a docstring describing purpose, parameters, and return value | No public API without documentation; use Google-style or Sphinx-style consistently |
| 8 | STD-008 | Type Hints on All Function Signatures | P2 | Verify that all functions include type hints for parameters and return values | Every function signature is typed; use `Optional`, `List`, `Dict` from `typing` module where needed |

## Execution Notes

Apply Registry verdict, evidence, and threshold rules. With no Python source in the
authorized Slice, mark the plugin N/A; never evaluate another language as Python.
