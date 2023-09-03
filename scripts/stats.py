# Compiles statistics on ConLL-U files
# Usage: python stats.py -i <corpus_dir> -o <output_dir> -e <encoding>

import os, argparse
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import re
# Can't use `conllu` module because it doesn't support multiple heads

# Defaults
INPUT_DIR = 'conllu'
OUTPUT_DIR = 'tex'
ENCODING = 'utf-8'
MEANS_FILE = 'stats_means.tex'
TOTALS_FILE = 'stats_totals.tex'

def get_stats(file, encoding=ENCODING, meta={}):
    stats = []
    init_sent = {'tokens': 0, 'sentences': 0}
    with open(file, 'r', encoding=encoding) as f:
        lines = f.readlines()
        sent = init_sent.copy()
        for line in lines:
            if not line.strip():
                sent['toks_per_sent'] = sent['tokens'] / sent['sentences']
                sent.update(meta)
                stats.append(sent)
                sent = init_sent.copy()
            elif line.startswith('#'):
                feat, value = line[1:].split('=', 1)
                sent[feat.strip()] = value.strip()
            elif line.split('\t', 2)[1] == '<SENT>':
                sent['sentences'] += 1
            elif line.split('\t', 2)[1] == '.':
                sent['tokens'] += 1
                sent['sentences'] += 1
            else:
                sent['tokens'] += 1
    return pd.DataFrame(stats)

def main(corpus=INPUT_DIR, encoding=ENCODING):
    stats = pd.DataFrame()
    splits = [f for f in os.listdir(corpus) if os.path.isdir(os.path.join(corpus, f))]
    for split in splits:
        files = [f for f in os.listdir(os.path.join(corpus, split)) if f.endswith('.conllu')]
        for file in files:
            order, layer = re.match(r'(\d+)-(\w+)\.conllu', file).groups()
            order = int(order)
            path = os.path.join(corpus, split, file)
            meta = {'split': split, 'file': file, 'layer': layer, 'order': order}
            file_stats = get_stats(path, encoding, meta)
            stats = pd.concat([stats, file_stats], ignore_index=True)
    return stats

# Execute from command line
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Compiles statistics on ConLL-U files')
    parser.add_argument('-i', '--input', help='Directory where .conllu files reside', default=INPUT_DIR)
    parser.add_argument('-o', '--output', help='Directory where to save the statistics in LaTeX', default=OUTPUT_DIR)
    parser.add_argument('-e', '--encoding', help='Character encoding (same for all input and output files)', default=ENCODING)
    args = parser.parse_args()

    print(f"Compiling statistics for `{args.input}`...")
    stats = main(args.input, args.encoding)
    stats['Layer'] = stats['file'].str.split('-').str[1].str.split('.').str[0]
    stats = stats[['Layer', 'tokens', 'sentences', 'toks_per_sent', 'order']]
    
    stats_mean = stats.groupby(['Layer']).mean().round(1).sort_values(by='order')
    stats_mean.drop(['order'], axis=1, inplace=True)
    stats_mean.columns = ['Tokens', 'Sentences', 'Tokens/Sentence']
    stats_mean.reset_index(inplace=True)
    stats_mean.style.to_latex(os.path.join(args.output, MEANS_FILE))
    print(f"  saved `{args.output}/{MEANS_FILE}`")

    stats_total = stats.groupby(['Layer']).sum().sort_values(by='order')
    stats_total.drop(['order', 'toks_per_sent'], axis=1, inplace=True)
    stats_total.columns = ['Tokens', 'Sentences']
    stats_total.reset_index(inplace=True)
    stats_total.style.to_latex(os.path.join(args.output, TOTALS_FILE))
    print(f"  saved `{args.output}/{TOTALS_FILE}`")

# FOR DEV USE ONLY
# class Args():
#     input = '../conllu'
#     output = '../tex'
#     encoding = 'utf-8'
# args = Args()