# Phase 5.1 visual QA

Reviewed the current WPF contact sheet on 29 October 2026: coherent reopened two/three-row selection, shortening to one row, recovered mixed regions/pages, and Calibri selection. Rows and highlights align and remain separate; surrounding text stays in place. The source body is now fully visible at 100% in the recorded selection states. At four app zooms, separate assertions verify both page-relative 0.01 pt caret alignment and actual viewport containment. Captures are 96 DPI, not physical input or OS display-scale certification.

Initial visual review found native hidden-caret panning at high zoom and a screenshot taken before the zoom/render dispatcher update. PositionSelection now suppresses the native unwrapped-caret scroll request and brings the proposed caret/selection row into view. The tests wait for the dispatcher before capture. These findings and old captures are retained in timestamped development runs.

Poppler full-page 96-DPI PNGs for all six convenience examples are retained in review-poppler; export-contact-sheet.png shows top details including Word two/three/one rows, Calibri/Arial and the second mixed page. Independent 72/144-DPI comparisons cover complete pages and unchanged content. This contact sheet is supporting visual evidence, not a replacement for those quantitative checks.
