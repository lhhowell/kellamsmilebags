#!/usr/bin/env python3
"""
Rebuild APResearch_BookmarkBuilder_MiddleSchool.html → APEnvSci_BookmarkBuilder_MS.html

Targeted changes only — no rewrite.
Preserves WORDS array, google.script.run wiring, all other functionality.

Usage:
  Put this script in the same folder as the source file and run:
    python3 rebuild_APEnvSci_BookmarkBuilder_MS.py

  Or edit SRC/DEST below to point at absolute paths.
"""
import re, os, sys

SRC  = "APResearch_BookmarkBuilder_MiddleSchool.html"
DEST = "APEnvSci_BookmarkBuilder_MS.html"

if not os.path.exists(SRC):
    sys.exit(f"✗ Source file not found: {SRC}")

with open(SRC, 'r', encoding='utf-8') as f:
    html = f.read()

original_len = len(html)
log = []

# ───────────────────────────────────────────────────────────────────
# 1. FLUSH-SIDES SADDLE-FOLD  (Standard #10)
#    - .bookmark-pair gap → 0 on screen
#    - @media print .bookmark-pair gap → 0
#    - Dashed cut/fold line on right edge of first bookmark
# ───────────────────────────────────────────────────────────────────
# Screen rule — matches the default .bookmark-pair{display:flex;gap:40px...}
html, n = re.subn(
    r'(\.bookmark-pair\s*\{[^}]*?gap:)\s*\d+px',
    lambda m: m.group(1) + '0',
    html
)
log.append(f"[1a] .bookmark-pair gap → 0 in all CSS blocks ({n} matches — covers screen + @media print)")

# Inject flush-fold guard + dashed cut/fold line at end of first <style>
fold_css = """
/* ─── FLUSH-SIDES SADDLE-FOLD (Standard #10) ─── */
.bookmark-pair { gap:0 !important; }
.bookmark-pair .bookmark:first-child {
  border-right: 2px dashed rgba(0,0,0,.35);
}
@media print {
  .bookmark-pair { gap:0 !important; }
  .bookmark-pair .bookmark:first-child {
    border-right: 2px dashed #777 !important;
  }
}
"""
html, n = re.subn(r'</style>', fold_css + '\n</style>', html, count=1)
log.append(f"[1b] Flush-fold guard + dashed cut/fold line injected ({n} match)")

# ───────────────────────────────────────────────────────────────────
# 2. savePDF() INLINE CSS (~line 413)
#    Step 1a's regex already caught this (same selector pattern inside
#    the JS template string). Verify by re-scanning.
# ───────────────────────────────────────────────────────────────────
remaining_gap = re.findall(r'\.bookmark-pair\s*\{[^}]*?gap:\s*\d+px', html)
if remaining_gap:
    for g in remaining_gap:
        html = html.replace(g, re.sub(r'gap:\s*\d+px', 'gap:0', g))
    log.append(f"[2]  savePDF() inline CSS gap cleanup ({len(remaining_gap)} stragglers)")
else:
    log.append(f"[2]  savePDF() inline CSS — already clean from step 1a")

# ───────────────────────────────────────────────────────────────────
# 3. WORDS DATA — scrub "Kellam" from attribution lines
# ───────────────────────────────────────────────────────────────────
subs = [
    ('Your Kellam Scientist',   'Your AP Env Sci Scientist'),
    (' · Kellam High School',   ''),
    (', Kellam High School',    ''),
    (' Kellam High School',     ''),
    ('Class of 2026',           'Class of 2026'),  # keep as-is (valid)
]
for old, new in subs:
    count = html.count(old)
    if count and old != new:
        html = html.replace(old, new)
        log.append(f"[3]  '{old}' → '{new}' ({count} replacements)")

# ───────────────────────────────────────────────────────────────────
# 4. FULL REBRAND
# ───────────────────────────────────────────────────────────────────
# <title>
html, n = re.subn(
    r'<title>[^<]*</title>',
    '<title>Smile Bags — AP Env Sci Bookmark Builder (Middle School)</title>',
    html, count=1
)
log.append(f"[4a] <title> updated ({n} match)")

# Brand sprinkles
for old, new, label in [
    ('KELLAM SMILE BAGS',  'SMILE BAGS',  '[4b] Hero/footer brand caps'),
    ('Kellam Smile Bags',  'Smile Bags',  '[4c] Brand title case'),
]:
    count = html.count(old)
    html = html.replace(old, new)
    log.append(f"{label}: '{old}' → '{new}' ({count} replacements)")

# AP Research → AP Environmental Science in visible copy
# (Done BEFORE Amy Stone swap so the hero line is predictable)
count = len(re.findall(r'\bAP Research\b', html))
html = re.sub(r'\bAP Research\b', 'AP Environmental Science', html)
log.append(f"[4d] 'AP Research' → 'AP Environmental Science' ({count} replacements)")

# Middle School Edition label — keep it, still accurate
# (no change needed)

# Hero teacher line: Amy Stone → Honaker, linked per Standard #12
AMY_LINK = ('<a href="APEnvSci_Teacher_Guide.html" '
            'style="color:inherit;text-decoration:none;'
            'border-bottom:1px dotted currentColor;">Honaker</a>')
count = html.count('Amy Stone')
html = html.replace('Amy Stone', AMY_LINK)
log.append(f"[4e] Amy Stone → Honaker (linked to APEnvSci_Teacher_Guide.html) ({count} replacements)")

# Back button target
count = html.count('APResearch_Menu.html')
html = html.replace('APResearch_Menu.html', 'APEnvSci_Menu.html')
log.append(f"[4f] Back link: APResearch_Menu.html → APEnvSci_Menu.html ({count} replacements)")

# Bookmark-foot sub-line (.bm-bfoot-s): strip "Kellam High School"
for old, new in [
    ('AP Environmental Science · Kellam High School',
     'AP Environmental Science · Honaker'),
    ('AP Environmental Science &middot; Kellam High School',
     'AP Environmental Science &middot; Honaker'),
]:
    count = html.count(old)
    if count:
        html = html.replace(old, new)
        log.append(f"[4g] .bm-bfoot-s: '{old}' → '{new}' ({count} replacements)")

# Unified footer line (may or may not exist in this file — scan & replace)
footer_pattern = r'Smile Bags\s*·\s*A Word &amp; Wonder Experience[^<"\n]{0,120}'
footer_target  = ('Smile Bags · A Word &amp; Wonder Experience · '
                  'AP Environmental Science · Honaker · Spring 2026')
matches = re.findall(footer_pattern, html)
html = re.sub(footer_pattern, footer_target, html)
# also try with the literal & (not entity)
footer_pattern2 = r'Smile Bags\s*·\s*A Word & Wonder Experience[^<"\n]{0,120}'
footer_target2  = ('Smile Bags · A Word & Wonder Experience · '
                   'AP Environmental Science · Honaker · Spring 2026')
matches2 = re.findall(footer_pattern2, html)
html = re.sub(footer_pattern2, footer_target2, html)
log.append(f"[4h] Standardized footer applied ({len(matches)+len(matches2)} matches)")

# ───────────────────────────────────────────────────────────────────
# 5. VERIFY — anything left over?
# ───────────────────────────────────────────────────────────────────
def scan(label, needle):
    hits = [(i, ln.strip()) for i, ln in enumerate(html.splitlines(), 1)
            if needle in ln]
    return label, hits

checks = [scan('Kellam',       'Kellam'),
          scan('AP Research',  'AP Research'),
          scan('APResearch',   'APResearch'),
          scan('Amy Stone',    'Amy Stone')]

# Write output
with open(DEST, 'w', encoding='utf-8') as f:
    f.write(html)

# ── Report ──
print(f"\n═══ REBUILD COMPLETE ═══")
print(f"  Source: {SRC}  ({original_len:,} bytes)")
print(f"  Output: {DEST}  ({len(html):,} bytes)")
print(f"  Delta:  {len(html) - original_len:+,} bytes\n")

print("── Change log ──")
for line in log:
    print(f"  {line}")

print("\n── Residual scan ──")
all_clean = True
for label, hits in checks:
    if hits:
        all_clean = False
        print(f"  ⚠ Remaining '{label}' mentions: {len(hits)}")
        for i, ln in hits[:6]:
            print(f"     L{i}: {ln[:100]}")
    else:
        print(f"  ✓ No '{label}' mentions remain")

if all_clean:
    print("\n✓ ALL CLEAN — ready to drop into GitHub.")
else:
    print("\n⚠ Review residuals above. 'Kellam High School' inside the")
    print("  long descriptive body text of WORDS may be legitimate; the")
    print("  branding rule only bars it from fixed UI chrome and")
    print("  attributions. Confirm before deploying.")
