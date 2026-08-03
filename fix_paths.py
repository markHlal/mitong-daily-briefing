import re

with open('src/generator/website.py', 'r') as f:
    content = f.read()

# Fix three paths: ../output/ -> ./output/
content = content.replace('src="../{latest[\'detail_path\']}"', 'src="./{latest[\'detail_path\']}"')
content = content.replace('src="../{latest[\'highlights_path\']}"', 'src="./{latest[\'highlights_path\']}"')
content = content.replace('src="../{thumb}"', 'src="./{thumb}"')

with open('src/generator/website.py', 'w') as f:
    f.write(content)

print('Fixed 3 image paths from ../ to ./')
