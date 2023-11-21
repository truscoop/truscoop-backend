import re

with open('readme.txt') as f:
    text = f.read()
    article = re.sub(r'("(.*),(.*)")', '\1', article)