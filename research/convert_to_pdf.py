#!/usr/bin/env python3
"""Convert the coconut research markdown to a styled PDF."""

import markdown
from weasyprint import HTML

INPUT = "coconut-seedling-classification-swarm-research.md"
OUTPUT = "coconut-seedling-classification-swarm-research.pdf"

with open(INPUT, "r") as f:
    md_content = f.read()

html_body = markdown.markdown(
    md_content,
    extensions=["tables", "fenced_code", "toc", "codehilite"],
)

full_html = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
  @page {{
    size: A4;
    margin: 2cm 2.5cm;
    @bottom-center {{
      content: "Page " counter(page) " of " counter(pages);
      font-size: 9px;
      color: #888;
    }}
  }}
  body {{
    font-family: 'DejaVu Sans', 'Helvetica Neue', Arial, sans-serif;
    font-size: 11pt;
    line-height: 1.6;
    color: #1a1a1a;
  }}
  h1 {{
    font-size: 22pt;
    color: #1a5f2a;
    border-bottom: 3px solid #1a5f2a;
    padding-bottom: 8px;
    margin-top: 0;
  }}
  h2 {{
    font-size: 16pt;
    color: #2d7a3e;
    border-bottom: 1px solid #ccc;
    padding-bottom: 4px;
    margin-top: 28px;
    page-break-after: avoid;
  }}
  h3 {{
    font-size: 13pt;
    color: #3a8a4e;
    margin-top: 20px;
    page-break-after: avoid;
  }}
  h4 {{
    font-size: 11.5pt;
    color: #444;
    margin-top: 16px;
    page-break-after: avoid;
  }}
  table {{
    border-collapse: collapse;
    width: 100%;
    margin: 12px 0;
    font-size: 10pt;
    page-break-inside: avoid;
  }}
  th {{
    background-color: #1a5f2a;
    color: white;
    padding: 8px 10px;
    text-align: left;
    font-weight: 600;
  }}
  td {{
    padding: 6px 10px;
    border-bottom: 1px solid #ddd;
  }}
  tr:nth-child(even) {{
    background-color: #f5f9f5;
  }}
  blockquote {{
    border-left: 4px solid #1a5f2a;
    background: #f0f7f0;
    padding: 12px 16px;
    margin: 16px 0;
    font-style: italic;
    color: #333;
  }}
  code {{
    background: #f4f4f4;
    padding: 1px 5px;
    border-radius: 3px;
    font-size: 9.5pt;
    font-family: 'DejaVu Sans Mono', 'Courier New', monospace;
  }}
  pre {{
    background: #f8f8f8;
    border: 1px solid #ddd;
    border-radius: 4px;
    padding: 14px;
    font-size: 8.5pt;
    line-height: 1.4;
    overflow-x: auto;
    page-break-inside: avoid;
    font-family: 'DejaVu Sans Mono', 'Courier New', monospace;
  }}
  pre code {{
    background: none;
    padding: 0;
  }}
  hr {{
    border: none;
    border-top: 2px solid #1a5f2a;
    margin: 24px 0;
  }}
  strong {{
    color: #1a1a1a;
  }}
  ul, ol {{
    margin: 8px 0;
    padding-left: 24px;
  }}
  li {{
    margin: 4px 0;
  }}
  a {{
    color: #1a5f2a;
    text-decoration: none;
  }}
</style>
</head>
<body>
{html_body}
</body>
</html>"""

HTML(string=full_html).write_pdf(OUTPUT)
print(f"PDF generated: {OUTPUT}")
