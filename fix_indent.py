# Fix indentation: ROW 1-6 + FOOTER need to be inside the if block
with open("app.py", "r", encoding="utf-8") as f:
    lines = f.readlines()

output = []
in_dashboard = False
in_row_section = False  # we are inside rows 1-6 or footer that need indenting

for i, line in enumerate(lines):
    stripped = line.lstrip()
    
    # Detect start of dashboard if-block body
    if stripped.startswith("if page == "):
        in_dashboard = True
        output.append(line)
        continue
    
    # Detect start of row sections (wrong indentation - at column 0 instead of 4 spaces)
    if in_dashboard and line.startswith("# ====") and "ROW" in line:
        in_row_section = True
        output.append("    " + line)  # indent the comment
        continue
    
    # The "col" definitions right after ROW headers are at column 0
    if in_row_section and (line.startswith("col") and "=" in line and "st.columns" in line):
        output.append("    " + line)
        continue
    
    # "with col" blocks inside row sections
    if in_row_section and line.startswith("# ---"):
        output.append("    " + line)
        continue
    
    if in_row_section and line.startswith("with col"):
        output.append("    " + line)
        continue
    
    # The FOOTER section markdown lines are also at wrong indentation
    if in_row_section and stripped.startswith("# FOOTER"):
        # This is part of the mis-indented block
        output.append("    " + line)
        continue
    
    if in_row_section and stripped.startswith("st.markdown"):
        output.append("    " + line)
        continue
    
    if in_row_section and stripped.startswith('"""') or (in_row_section and line.startswith('<div') or line.startswith('<h4') or line.startswith('<p') or line.startswith('</div')):
        output.append("    " + line)
        continue
    
    if in_row_section and stripped.startswith("unsafe_allow_html"):
        output.append("    " + line)
        continue
    
    if in_row_section and stripped.startswith(")"):
        output.append("    " + line)
        continue
    
    # Detect end of row sections - elif or other top-level constructs
    if in_row_section and (stripped.startswith("elif page ==") or stripped.startswith("# ====") and "SINGLE" in stripped):
        in_row_section = False
        output.append(line)
        continue
    
    if in_row_section and stripped.startswith("# ====") and "FOOTER" in stripped:
        # Still in row section
        output.append("    " + line)
        continue
    
    # All other lines in row_section get indented
    if in_row_section:
        output.append("    " + line)
        continue
    
    output.append(line)

with open("app.py", "w", encoding="utf-8") as f:
    f.writelines(output)

print("Done. Validating...")
