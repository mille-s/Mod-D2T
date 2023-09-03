# Convert from Buddy .str format to ConLL-U
# Usage: python convert.py -i <input_dir> -o <output_dir> -t <text_file> -e <encoding>

import sys, os, argparse
from depgraph import DepGraph
import re

# Defaults
STR_DIR = 'str'
CONLLU_DIR = 'conllu'
ENCODING = 'utf-8'
TEXT = '00-Text.txt'

def normalize_text(text):
	"""Normalizes a single text by removing useless spaces and capitalizing sentences."""
	text = re.sub(r' ([\.,])', r'\1', text)
	text = re.sub(r'\.\.', '.', text)
	text = re.sub(r'\. ([\w])', lambda x: '. ' + x.group(1).upper(), text)
	text = text.replace(r'_', ' ')
	text = text.replace('&', '\\&')
	return text

# Process
parser = argparse.ArgumentParser(description='Convert from Buddy .str format to ConLL-U')
parser.add_argument('-i', '--input', help='Input directory where .str files will be read', default=STR_DIR)
parser.add_argument('-o', '--output', help='Output directory where .conllu files will be written', default=CONLLU_DIR)
parser.add_argument('-t', '--text', help='Text file that contains text outputs', default=TEXT)
parser.add_argument('-e', '--encoding', help='Character encoding (same for all input and output files)', default=ENCODING)
args = parser.parse_args()

print(f"Converting `{args.input}/*.str` to `{args.output}/*.conllu` with encoding {args.encoding}...")
splits = [f for f in os.listdir(args.input) if os.path.isdir(os.path.join(args.input, f))]
for split in sorted(splits):
	print(f"  {split}/")
	texts = [l.strip() for l in open(os.path.join(args.input, split, args.text), 'r', encoding=args.encoding).readlines() if l.strip()]
	files = [f for f in os.listdir(os.path.join(args.input, split)) if f.endswith('.str')]
	out_tex = False
	for file in sorted(files):
		print(f"    {file}")
		path_str = os.path.join(args.input, split, file)
		graphs = DepGraph.from_buddy(path_str)
		path_conllu = os.path.join(args.output, split, file.replace('.str', '.conllu'))
		os.makedirs(os.path.dirname(path_conllu), exist_ok=True)
		with open(path_conllu, 'w', encoding=args.encoding) as f:
			for i, (graph, text) in enumerate(zip(graphs, texts), 1):
				text = normalize_text(text)
				conllu = graph.to_conllu(text=text)
				f.write(conllu)
