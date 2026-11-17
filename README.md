# Pulse Admin prototype (Mastercard RFP)

Lune's internal admin console for Pulse, as committed in the Mastercard RFP answers.
Open `index.html` in a browser. The file is self-contained.

This is the pitch version. It does not show the internal RFP review marks (answer labels, legends, row tooltips). A small script at the end of `index.html` (`id="pitch-mode"`) hides them. The internal review version stays in the `product` workspace.

## Source
- `src/pulse-admin.src.html`: the prototype source.
- `src/build.py`: builds `index.html`. Run it from the `product` workspace, because it reads the Lune UI skill and the RFP answer sheet there.
- `src/_shared/`: shared CSS, tooltip script, partner model, and the demo merchant rename (`rebrand.py`).

Built from the 13 Nov 2026 version.
