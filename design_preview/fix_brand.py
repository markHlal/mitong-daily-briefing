import pathlib
p = pathlib.Path('generate_apple.py')
t = p.read_text(encoding='utf-8')
t = t.replace('AI-芯视界', '米桶 AI')
t = t.replace('Codex AIGC', 'Daily Brief')
p.write_text(t, encoding='utf-8')
print('done')
