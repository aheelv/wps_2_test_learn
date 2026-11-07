# -*- coding: utf-8 -*-
"""Inject the question JSON into the HTML template to produce a standalone page."""
import sys
tpl_path, data_path, out_path = sys.argv[1], sys.argv[2], sys.argv[3]
tpl = open(tpl_path, encoding='utf-8').read()
data = open(data_path, encoding='utf-8').read()
# Guard against accidental </script> inside JSON text
data = data.replace('</', '<\\/')
assert '__QUIZ_DATA__' in tpl, 'placeholder missing'
html = tpl.replace('__QUIZ_DATA__', data)
with open(out_path, 'w', encoding='utf-8') as f:
    f.write(html)
print('written:', out_path, 'bytes:', len(html.encode('utf-8')))
print('script tags:', html.count('<script'), html.count('</script>'))
