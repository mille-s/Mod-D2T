# Convert ConLL-U files to simplified .tex tables
# Usage: python export.py -i <input_dir> -o <output_dir> -e <encoding>


import sys, os, argparse, shutil
import pandas as pd
import re

ENCODING = 'utf-8'
TEXT_TEX = 'text.tex'
COLUMNS = {
	'predargnorm': ['ID', 'Semanteme', '_lemma', '_upos', '_xpos', 'Features', 'Head', 'Rel', '_deps', 'Misc'],
	'predargagg': ['ID', 'Semanteme', '_lemma', '_upos', '_xpos', 'Features', 'Head', 'Rel', '_deps', 'Misc'],
	'predargpos': ['ID', 'Semanteme', '_lemma', 'POS', '_xpos', 'Features', 'Head', 'Rel', '_deps', 'Misc'],
	'predargcomm': ['ID', 'Semanteme', '_lemma', 'POS', '_xpos', 'Features', 'Head', 'Rel', '_deps', 'Misc'],
	'dsynt': ['ID', 'Lexeme', '_lemma', 'POS', '_xpos', 'Features', 'Head', 'Rel', '_deps', 'Misc'],
	'ssynt': ['ID', 'Lexeme', '_lemma', 'POS', '_xpos', 'Features', 'Head', 'Rel', '_deps', 'Misc'],
	'ssyntagg': ['ID', 'Lexeme', '_lemma', 'POS', '_xpos', 'Features', 'Head', 'Rel', '_deps', 'Misc'],
	'reg': ['ID', 'Lexeme', '_lemma', 'POS', '_xpos', 'Features', 'Head', 'Rel', '_deps', 'Misc'],
	'dmorphlin': ['ID', 'Word', '_lemma', 'POS', '_xpos', 'Features', '_head', '_deprel', '_deps', 'Misc'],
	'smorphtext': ['ID', 'Word', '_lemma', 'POS', '_xpos', '_feat', '_head', '_deprel', '_deps', 'Misc']
}

def load_conllu(file, encoding=ENCODING):
	# Load CoNLL-U file
	level = os.path.basename(file).split('.')[0].split('-')[1].lower()
	cols = COLUMNS[level]
	df = pd.read_csv(file, sep='\t', comment='#', header=None, names=cols, encoding=encoding)
	# Drop useless columns
	drop_cols = [col for col in cols if col.startswith('_')]
	df = df.drop(drop_cols, axis=1)
	return df

def to_tex(df):
	# Shorten feature names
	if 'Features' in df.columns:
		df['Features'] = df['Features'].replace(r'\w+=', '', regex=True).str.lower()
	if 'Coref' in df.columns:
		df['Coref'] = df['Coref'].replace(r'\w+=', '', regex=True).str.lower()
	return df.style.to_latex()

if __name__ == '__main__':
	# Parse arguments
	parser = argparse.ArgumentParser()
	parser.add_argument('-i', '--input', help='Input directory where .conllu files will be read')
	parser.add_argument('-o', '--output', help='Output directory where .tex files will be written')
	parser.add_argument('-e', '--encoding', help='Character encoding (same for all input and output files)', default=ENCODING)
	args = parser.parse_args()

	# Process files
	print(f"Exporting .tex files...")
	files = [f for f in os.listdir(args.input) if f.endswith('.conllu')]
	for file in sorted(files):
		tex_file = re.sub(r'\.conllu$', '.tex', file)
		print(f"  {tex_file}")
		path_in = os.path.join(args.input, file)
		path_out = os.path.join(args.output, tex_file)
		os.makedirs(os.path.dirname(path_out), exist_ok=True)
		with open(path_out, 'w') as o:
			o.write(to_tex(load_conllu(path_in, args.encoding)))
	path_text_in = os.path.join(args.input, TEXT_TEX)
	path_text_out = os.path.join(args.output, TEXT_TEX)
	print(f"  {TEXT_TEX}")
	shutil.copyfile(path_text_in, path_text_out)
