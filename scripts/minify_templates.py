import os
import re

TEMPLATE_DIR = os.environ.get("TEMPLATE_DIR", os.path.join(os.path.dirname(__file__), '..', 'tabflow', 'tabflow_app', 'templates'))

# Regex patterns for removing comments and extra whitespace
django_comment_pattern = re.compile(r'{%\s*comment\s*%}.*?{%\s*endcomment\s*%}', re.DOTALL)
html_comment_pattern = re.compile(r'<!--.*?-->', re.DOTALL)
whitespace_pattern = re.compile(r'>\s+<')


def minify_template_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    # Remove Django comments
    content = django_comment_pattern.sub('', content)
    # Remove HTML comments
    content = html_comment_pattern.sub('', content)
    # Remove whitespace between tags
    content = whitespace_pattern.sub('> <', content)
    # Remove leading/trailing whitespace on each line
    content = '\n'.join(line.strip() for line in content.splitlines() if line.strip())
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)


def minify_templates():
    for root, dirs, files in os.walk(TEMPLATE_DIR):
        for file in files:
            if file.endswith('.html'):
                filepath = os.path.join(root, file)
                minify_template_file(filepath)
                print(f"Minified: {filepath}")

if __name__ == "__main__":
    minify_templates()
