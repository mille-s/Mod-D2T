# Extract a single text from ConLL-U files
# Usage: python extract.py -x <text_index> -i <input_dir> -o <output_dir> -e <encoding>

import sys, os, argparse
from depgraph import DepGraph
import re

# Defaults
IN_DIR = 'conllu/train'
OUT_DIR = 'extracted'
ENCODING = 'utf-8'
TEXT_TEX = 'text.tex'

# Functions
def clean_tex(text):
	text = text[0].upper() + text[1:]
	return text.replace('&', '\\&').replace('_', '\\_')

# Process arguments
parser = argparse.ArgumentParser(description='Extract a text from ConLL-U files')
parser.add_argument('-x', '--extract', help='Index of the text to extract', type=int, default=1)
parser.add_argument('-i', '--input', help='Input directory where .conllu files will be read', default=IN_DIR)
parser.add_argument('-o', '--output', help='Output directory where extracted files will be written', default=OUT_DIR)
parser.add_argument('-e', '--encoding', help='Character encoding (same for all input and output files)', default=ENCODING)
args = parser.parse_args()

if args.extract < 1:
	raise Exception('Extraction index must be positive')

# Process files
print(f"Extracting structures for text #{args.extract}...")
files = [f for f in os.listdir(args.input) if f.endswith('.conllu')]
for file in sorted(files):
	print(f"  {file}")
	path_in = os.path.join(args.input, file)
	path_out = os.path.join(args.output, file)
	path_text = os.path.join(args.output, TEXT_TEX)
	os.makedirs(os.path.dirname(path_out), exist_ok=True)
	with open(path_in, 'r', encoding=args.encoding) as f_in:
		lines = f_in.readlines()
	text_tex = False
	i = 1
	stack = []
	for line in lines:
		if line.strip():
			stack.append(line.strip())
			if line.startswith('# text = '):
				text = line.replace('# text = ', '').strip()
		else:
			if i == args.extract:
				with open(path_out, 'w', encoding=args.encoding) as f_out:
					f_out.write('\n'.join(stack))
				if not text_tex:
					with open(path_text, 'w', encoding=args.encoding) as f_text:
						f_text.write(f'% text # {i}\n')
						f_text.write(clean_tex(text))
					text_tex = True
				break
			i += 1
			stack = []
	if not text_tex:
		raise Exception(f'Extraction index too high, max is {i-1}')

print(f"  Text: {text}")
