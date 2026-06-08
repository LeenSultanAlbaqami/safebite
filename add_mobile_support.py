from pathlib import Path

frontend = Path("frontend")

for html_file in frontend.glob("*.html"):

    content = html_file.read_text(encoding="utf-8")

    if "mobile.css" in content:
        continue

    insert_code = """
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<link rel="stylesheet" href="mobile.css">
"""

    if "</head>" in content:
        content = content.replace("</head>", insert_code + "\n</head>")
        html_file.write_text(content, encoding="utf-8")
        print("Updated:", html_file.name)

print("Done")