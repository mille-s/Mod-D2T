# Dependency graphs

from buddystr import parse
from configparser import ConfigParser
import random
# from pprint import pprint

DEFAULT_ENCODING = 'utf-8'
CONFIG = '/content/drive/My Drive/inlg23/features.conf'
MAX_ORDER_TRIES = 100 # number of times to try to set order
SENTENCE_TAG = '<SENT>'

# Load config
FEAT_MAP = {}
try:
	config = ConfigParser(allow_no_value=True)
	config.read(CONFIG)
	FEAT_MAP = {level: dict(config[level]) for level in config.sections()}
except:
	raise Exception(f"Check your config file {CONFIG}")

# Classes
class Node():
	"""A node in a dependency graph."""

	def __init__(self, label, features={}):
		"""
		Create a node.
		Args:
			label (str):	 label of the node
			features (dict): features of the node
		"""
		try:
			assert isinstance(label, str)
			assert isinstance(features, dict)
		except:
			raise TypeError('Expected Node(label=str, features=dict)')
		if not label:
			label = '_'
		# try:
		# 	assert label
		# except:
		# 	raise ValueError('Label cannot be empty string')
		self.label = label
		self.features = features.copy()		# make a copy otherwise features get mixed up between nodes
	
	def add_features(self, features):
		"""
		Add features to the node.
		Args:
			features (dict): features to add
		"""
		try:
			assert isinstance(features, dict)
		except:
			raise TypeError('Expected add_features(features=dict)')
		self.features.update(features)

	def add_feature(self, key, value):
		"""
		Add a feature to the node.
		Args:
			key (str):   key of the feature
			value (str): value of the feature
		"""
		try:
			assert isinstance(key, str)
			assert isinstance(value, str)
		except:
			raise TypeError('Expected add_feature(key=str, value=str)')
		self.features.update({key: value})
	
	def __str__(self):
		s = self.label
		s += f" [{', '.join(['='.join([k,v]) for (k,v) in self.features.items()])}]"
		return s

	def __repr__(self):
		return f'Node({self.label}, {self.features})'


class DepGraph():
	"""A dependency graph."""

	def __init__(self, level=None, nodes=[], rels=[], precedence=[], inclusions={}, corefs={}, meta={}):
		self.level = level
		self.linear = FEAT_MAP[self.level]['graphtype'] == 'chain'
		self.nodes = []
		self.add_nodes(nodes)
		self.rels = []
		self.add_rels(rels)
		self.precedence = []
		self.add_precedences(precedence)
		self.inclusions = {}
		self.add_inclusions(inclusions)
		self.corefs = {}
		self.add_corefs(corefs)
		self.meta = meta
		self.order = []  # order will be set later when the graph is complete

	def __str__(self):
		return '\n'.join([node.label for node in self.nodes])
	
	def __repr__(self):
		return f'DepGraph({self.level}, {self.nodes}, {self.rels}, {self.precedence}, {self.inclusions}, {self.corefs}, {self.meta})'

	def add_nodes(self, nodes):
		try:
			assert isinstance(nodes, list)
		except:
			raise TypeError('Expected nodes=list')
		for node in nodes:
			self.add_node(node)

	def add_node(self, node):
		try:
			assert isinstance(node, Node)
		except:
			raise TypeError('Node should be an instance of Node')
		self.nodes.append(node)

	def add_rels(self, rels):
		try:
			assert isinstance(rels, list)
		except:
			raise TypeError('Expected rels=list')
		for rel in rels:
			try:
				assert isinstance(rel, tuple)
				assert len(rel) == 3
			except:
				raise TypeError('Each item of rels must be a triplet')
			gov, rel, dep = rel
			self.add_rel(gov, rel, dep)
	
	def add_rel(self, gov, rel, dep):
		try:
			assert isinstance(gov, Node)
			assert isinstance(dep, Node)
			rel = str(rel)
		except:
			raise TypeError('Expected rel=(Node, str, Node)')
		self.rels.append((gov, rel, dep))

	def add_inclusions(self, inclusions):
		try:
			assert isinstance(inclusions, dict)
		except:
			raise TypeError('Expected inclusions=dict')
		for sup, subs in inclusions.items():
			self.add_inclusion(sup, subs)

	def add_inclusion(self, sup, sub=None, subs=None):
		try:
			assert isinstance(sup, Node)
			assert isinstance(sub, Node) or sub is None
			assert isinstance(subs, set) or isinstance(subs, list) or subs is None
		except:
			raise TypeError('Expected sup=Node, sub=Node, subs=set|list')
		try:
			assert sub is None or subs is None
		except:
			raise ValueError('Expected either sub or subs, not both')
		if sub:
			subs = {sub}
		if isinstance(subs, list):
			subs = set(subs)
		if sup not in self.inclusions:
			self.inclusions[sup] = set()
		self.inclusions[sup] = self.inclusions[sup].union(subs)

	def add_corefs(self, corefs):
		try:
			assert isinstance(corefs, dict)
		except:
			raise TypeError('Expected corefs=dict')
		for anaphor, antecedent in corefs.items():
			self.add_coref(anaphor, antecedent)
	
	def add_coref(self, anaphor, antecedent):
		try:
			assert isinstance(anaphor, Node)
			assert isinstance(antecedent, Node)
		except:
			raise TypeError('Expected anaphor=Node, antecedent=Node')
		if anaphor not in self.corefs:
			self.corefs[anaphor] = set()
		self.corefs[anaphor] = self.corefs[anaphor].union({antecedent})

	def add_precedences(self, precedences):
		try:
			assert isinstance(precedences, list)
			if precedences:
				assert min([isinstance(t, tuple) and len(t) == 2 for t in precedences])
		except:
			raise TypeError('Expected precedences=list of couples')
		for node1, node2 in precedences:
			self.add_precedence(node1, node2)

	def add_precedence(self, node1, node2):
		try:
			assert isinstance(node1, Node)
			assert isinstance(node2, Node)
		except:
			raise TypeError('Expected node1=Node, node2=Node')
		if (node2, node1) in self.precedence:
			raise ValueError(f'Inconsistent precedence: {node1} < {node2} and {node2} < {node1}')
		if (node1, node2) not in self.precedence:			
			self.precedence.append((node1, node2))

	def set_order(self):
		# Put embedded nodes before bubbles and bubbles before the contents of their successor
		for sup, subs in self.inclusions.items():
			precs = [prec for prec, s in self.precedence if s == sup]
			for sub in subs:
				self.add_precedence(sub, sup)
				for prec in precs:
					self.add_precedence(prec, sub)
		# For non-linear structures, put gov before deps just to be neat
		if not self.linear:
			for gov, _, dep in self.rels:
				self.add_precedence(gov, dep)
		# Set order
		order = self.nodes
		if len(order) > 1:
			tries = 0
			changed = True
			while changed:
				tries += 1
				changed = False
				# Put preceding nodes first before their successors
				for node1, node2 in self.precedence:
					if order.index(node1) > order.index(node2):
						order.remove(node1)
						order.insert(order.index(node2), node1)
						changed = True
				if tries > MAX_ORDER_TRIES:
					raise Exception(f'Could not set order on {self.__repr__()}')
		self.order = order
	
	# Import
	@classmethod
	def from_buddy(self, file, encoding=DEFAULT_ENCODING):
		"""
		Import multiple structures from a BUDDY .str file.
		Args:
			file (str): 	path to the input file (BUDDY .str)
			encoding (str): file encoding
		Returns:
			list: list of DepGraph objects

		A BUDDY structure is a tuple ((Level, ID), Nodes)
		Nodes is a list of tuples of the format (NodeHead, NodeBody)
		NodeHead is a tuple of the format ('node', Label, ID)
		NodeBody is a list of tupes that represent features, coreferences, successors, inclusion and edges
		Features are tuples of the format ('feature', Feature, Value)
		Coreferences are tuples of the format ('coref', NodeHead)
		Precedences are tuples of the format ('prec', NodeHead)
		Inclusions are tuples of the format ('node', NodeHead)
		Edges are tuples of the format ('edge', Relation, NodeHead)
		"""
		strucs = parse(file, encoding)
		# for debugging purposes
		# file_txt = file.replace('.str_out.str', '.txt')
		# with open(file_txt, 'w', encoding=encoding) as f:
		# 	pprint(strucs, f)
		return [DepGraph._from_buddy_struc(struc) for struc in strucs if struc] # filter out empty structures
	
	@classmethod
	def _from_buddy_struc(self, struc):
		"""
		Converts a single BUDDY structure to a DepGraph object.
		There are no embedded node definitions in BUDDY structures, so this is not recursive.
		"""
		(level, struc_id), buddy_nodes = struc
		# meta = {'id': struc_id, 'level': level}
		meta = {'level': level}
		graph = DepGraph(level=level, meta=meta)
		nodes = {}
		for buddy_node in buddy_nodes:
			((_, label, node_id), node_body) = buddy_node
			if label == 'Text':					# filter out Text nodes
				continue
			# Separate body items by type
			features = dict([item[1:] for item in node_body if item[0] == 'feature'])
			precedence = [item[1][1:] for item in node_body if item[0] == 'prec']
			edges = [item[1:] for item in node_body if item[0] == 'edge']
			embedded_nodes = [item[1:] for item in node_body if item[0] == 'node']
			corefs = [item[1][1:] for item in node_body if item[0] == 'coref']
			# Features
			key = label + str(node_id) 			# buddy node IDs are not always unique
			# A Node object may have been created if it was embedded in a previous node
			if key in nodes:					# node already exists
				node = nodes[key]
				node.add_features(features)
			else:								# new node
				node = Node(label, features)
				nodes[key] = node
				graph.add_node(node)
			# Order
			for prec in precedence:
				succ_label, succ_node_id = prec
				key = succ_label + str(succ_node_id)
				if key in nodes:
					succ_node = nodes[key]
				else:
					succ_node = Node(succ_label)
					nodes[key] = succ_node
					graph.add_node(succ_node)
				graph.add_precedence(node, succ_node)
				# graph.add_rel(node, 'next', succ_node)
			# Edges
			for edge in edges:
				relation, (_, dep_label, dep_node_id) = edge
				key = dep_label + str(dep_node_id)
				if key in nodes:
					dep_node = nodes[key]
				else:
					dep_node = Node(dep_label)
					nodes[key] = dep_node
					graph.add_node(dep_node)
				graph.add_rel(node, relation, dep_node)
			# Embedded nodes
			for buddy_emb_node in embedded_nodes:
				emb_label, emb_node_id = buddy_emb_node
				key = emb_label + str(emb_node_id)
				if key in nodes:
					emb_node = nodes[key]
				else:
					emb_node = Node(emb_label)
					nodes[key] = emb_node
					graph.add_node(emb_node)
				graph.add_inclusion(node, emb_node)
			# Coreferences
			for coref in corefs:
				coref_label, coref_node_id = coref
				key = coref_label + str(coref_node_id)
				if key in nodes:
					coref_node = nodes[key]
				else:
					coref_node = Node(coref_label)
					nodes[key] = coref_node
					graph.add_node(coref_node)
				graph.add_coref(node, coref_node)
		graph.set_order()
		return graph

	# Export
	def to_conllu(self, file=None, text=None, enforce_order=False, enforce_tree=False):
		"""
		Convert to CoNLL-U format.
		CoNLL-U format: ID, FORM, LEMMA, UPOS, XPOS, FEATS, HEAD, DEPREL, DEPS, MISC
		https://universaldependencies.org/format.html
		DEPS is not used in this implementation
		Args:
			file (str): 			path to the output file
			enforce_order (bool): 	if True, node order must be set
			enforce_tree (bool): 	if True, the graph must be a tree
		Returns:
			str: CoNLL-U representation of the tree
		"""
		# if enforce_order:
		# 	try:
		# 		assert self.order
		# 	except:
		# 		raise Exception('Order must be set')		
		# Prepare CoNLL-U table
		e = '_' 	# filler for empty fields
		s = ''		
		if text:
			self.meta.update({'text': text})
		else:
			self.meta.update({'pseudo-text': ' '.join([node.label or e for node in self.order])})
		for key, value in self.meta.items():
			s += f'# {key} = {str(value)}\n'
		lemma_feats = [f for f in FEAT_MAP[self.level] if FEAT_MAP[self.level][f].lower() == 'lemma']
		upos_feats = [f for f in FEAT_MAP[self.level] if FEAT_MAP[self.level][f].lower() == 'upos']
		xpos_feats = [f for f in FEAT_MAP[self.level] if FEAT_MAP[self.level][f].lower() == 'xpos']
		misc_feats = [f for f in FEAT_MAP[self.level] if FEAT_MAP[self.level][f].lower() == 'misc']
		exclude = {f for f in FEAT_MAP[self.level] if FEAT_MAP[self.level].get(f)==''}.union(lemma_feats).union(upos_feats).union(xpos_feats).union(misc_feats)
		for i, node in enumerate(self.order, 1):
			form = node.label
			if form == 'Sentence':
				form = SENTENCE_TAG
			lemma = upos = xpos = e	# default value
			for feat in lemma_feats:
				if feat in node.features:
					lemma = node.features[feat]
					break	# only keep the first one and ignore other candidate features
			for feat in upos_feats:
				if feat in node.features:
					upos = node.features[feat]
					break	# only keep the first one and ignore other candidate features
			for feat in xpos_feats:
				if feat in node.features:
					xpos = node.features[feat]
					break	# only keep the first one and ignore other candidate features
			# Hack for a few specific features
			if node.features.get('class') == '-':
				del node.features['class']
			if node.features.pop('main_rheme', None):
				node.features['main'] = 'Rheme'
			if node.features.pop('main_theme', None):
				node.features['main'] = 'Theme'
			if node.features.pop('NE', None):
				node.features['NE'] = 'NE'
			if node.features.pop('NE', None):
				node.features['NE'] = 'NE'
			if node.features.pop('invariant', None):
				node.features['invariant'] = 'invar'
			# Hack to remove all bools and numbers in features
			exclude = exclude.union({k.lower() for k, v in node.features.items() if v.lower() in ['yes', 'no', 'true', 'false'] or v.isdigit()})
			# remove = 
			# for k in remove:
			# 	del node.features[k]
			feats = '|'.join([f'{k}={v}' for k, v in node.features.items() if k.lower() not in exclude]) or e
			# Don't use HEAD and DEPREL for linear structures
			if self.linear:
				head = e
				deprel = e
			else:
				govs = [(gov, rel) for (gov, rel, dep) in self.rels if dep==node]
				if enforce_tree:
					try:
						assert len(govs) <= 1
					except:
						raise ValueError(f'Invalid tree: more than one head for node {node}')
				if govs:
					head = ','.join([str(self.order.index(gov)+1) for gov, _ in govs])
					deprel = ','.join([rel for _, rel in govs])
				else:
					head, deprel = 0, 'root'
			if form == SENTENCE_TAG:
				feats = e
				head = e
				deprel = e
			misc_dict = {k:v for k,v in node.features.items() if k.lower() in misc_feats}
			# Hacks to rename IDs
			if 'coref_id' in misc_dict:
				misc_dict['coref'] = misc_dict.pop('coref_id')
			if 'id_o' in misc_dict:
				misc_dict['src'] = misc_dict.pop('id_o')
			# Another hack to clear misc_dict for Sentence nodes
			if node.label == 'Sentence':
				misc_dict = {}
			misc = '|'.join([f'{k}={v}' for k, v in misc_dict.items()]) or e
			s += f'{i}\t{form}\t{lemma}\t{upos}\t{xpos}\t{feats}\t{head}\t{deprel}\t{e}\t{misc}\n'
		s += '\n'
		return s

