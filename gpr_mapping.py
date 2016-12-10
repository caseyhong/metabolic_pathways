import json
import re
from collections import defaultdict
from collections import Counter
from ast import literal_eval
import pyparsing

thecontent = pyparsing.Word(pyparsing.alphanums) | '+' | '-'
parens = pyparsing.nestedExpr('(', ')', content=thecontent)

def get_gene_set(filename):
	relevant_genes = set()
	filtered_probes = set() 
	bools = ['or', 'and']
	with open(filename) as json_file:
		data = json.load(json_file)
		for rxn in data["reactions"]:
			if len(rxn["gene_reaction_rule"]) > 0:
				rule = rxn["gene_reaction_rule"]
				words = rule.split()
				genes = [w for w in words if w not in bools]
				for g in genes:
					if g not in relevant_genes:
						g = g.replace('(','')
						g = g.replace(')','')
						relevant_genes.add(g.lower())
						filtered_g = g.split('_AT')[0]+"_at" #removes numbers, lowercases 
						filtered_probes.add(filtered_g) 

	return relevant_genes, filtered_probes

def parse_gpr_mapping(filename):
	"""
	INPUT: path to JSON file containing reaction data
	OUTPUT: dict[reaction_id] = [nested list of stringified BiGG gene id's]
	"""
	parsed_mappings = {}
	with open(filename) as json_file:
		data = json.load(json_file)
		for rxn in data["reactions"]:
			if len(rxn["gene_reaction_rule"]) > 0:
				rule = rxn["gene_reaction_rule"]
				rxn_id = rxn["id"]
				words = rule.split()
				hashed_rule = []
				for word in words:
					if word[0] != '(' and word[-1] != ')':
						h = word.replace('_','ZZZZZZ')
						hashed_rule.append(h.encode('ascii'))
					elif word[0] == '(':
						h = word.replace('_','ZZZZZZ')
						hashed_rule.append(h.encode('ascii'))
					else:
						h = word.replace('_','ZZZZZZ')
						hashed_rule.append(h.encode('ascii'))
						hashed_rule.append(')')
				hashed = ''.join(hashed_rule)
				rule_clean = '(' + hashed + ')'
				rule_cleaner = rule_clean.replace('and', '+')
				rule_cleanest = rule_cleaner.replace('or', '-')
				res = parens.parseString(rule_cleanest)
				parsed = res.asList()
				parsed_mappings[rxn_id] = parsed[0]
				# parsed_mappings.append(parsed[0])
	# print parsed_mappings
	return parsed_mappings

#aggregate returns the abiochemical expression value of a reaction given set of genes and corresponding express. value 
#mapping - individual reaction 
#expression - dictionary of gene:expressionval 
#genes - list of genes

def aggregate(mapping, expression, genes):
	"""
	aggregate returns the biochemical expression value of a reaction given set of genes and corresponding express. value
	INPUTS:
		mapping - individual reaction 
		expression - dictionary of gene:expressionval 
		genes - list of genes
	OUTPUT: 
		biochemical exp. value 
	"""
	s = 0
	for i in xrange(len(mapping)):
		if i == 0:
			if mapping[i] in genes:
				s = expression[mapping[i]]
			else:
				s = aggregate(mapping[i], expression, genes)

		# index of gene 
		if i%2==0 and i > 0:
			next = mapping[i]
			operator = mapping[i-1]

			if next in genes:
				if operator == '+':
					s = min(s, expression[next])
				else:
					s = max(s, expression[next])
			else:
				if operator == '+':
					s = min(s, aggregate(next, expression, genes))
				else:
					s = max(s, aggregate(next, expression, genes))
	return s

def get_metabolite_associations(filename):
	"""
	INPUT:
	filename - path to JSON file containing reaction data
	OUTPUT: 
	dictionary[reaction_id] = ([source_metabolites],[target_metabolites])
	"""	
	res = {}
	with open(filename) as json_file:
		data = json.load(json_file)
		for rxn in data["reactions"]:
			rxn_id = rxn["id"].encode('ascii')
			metabolites = rxn["metabolites"]
			reactants = []
			products = []
			for m in metabolites:
				if metabolites[m] > 0:
					## a positive stoichiometric number denotes a PRODUCT of the reaction
					products.append(m.encode('ascii'))
				else:
					## a negative stoichiometric number denotes a REACTANT of the reaction
					reactants.append(m.encode('ascii'))
			res[rxn_id] = reactants,products
	return res

if __name__ == '__main__':
	# genes_of_interest,filtered_probes = parse_recon('./RECON1.json')
	# open('./recon1_genes.txt', 'w').close() #clears file 
	# output = open('./recon1_genes.txt','r+')
	# fg = open('./recon1_filteredGenes.txt','w')

	# for gene in filtered_probes: 
	# 	fg.write(gene+",")

	# for gene in genes_of_interest:
	# 	output.write(gene+",")

	# print 'finished writing!'

	# mappings = parse_gpr_mapping('./RECON1.json')
	# # print mappings
	# test1 = mappings[0]
	# expression1 = {'8639ZZZZZZAT1': 2, '26ZZZZZZAT1': 3, '314ZZZZZZAT2': 4, '314ZZZZZZAT1': 5}
	# test2 = ['2134ZZZZZZAT1', '-', ['2131ZZZZZZAT1', '+', '2132ZZZZZZAT1']]
	# expression2 = {'2134ZZZZZZAT1': 2, '2131ZZZZZZAT1': 3, '2132ZZZZZZAT1': 4}
	# test3 = ['54480ZZZZZZAT1', '-', '337876ZZZZZZAT1', '-', ['79586ZZZZZZAT1', '+', '22856ZZZZZZAT1']]
	# expression3 = {'54480ZZZZZZAT1': 2, '337876ZZZZZZAT1': 3, '79586ZZZZZZAT1': 4, '22856ZZZZZZAT1': 5}
	# test4 = ['3948ZZZZZZAT1', '-', '197257ZZZZZZAT1', '-', '3945ZZZZZZAT1', '-', '160287ZZZZZZAT1', '-', ['3945ZZZZZZAT1', '+', '3939ZZZZZZAT1']]
	# expression4 = {'3948ZZZZZZAT1': 2, '197257ZZZZZZAT1': 3, '3945ZZZZZZAT1': 4, '160287ZZZZZZAT1': 5, '3945ZZZZZZAT1': 6, '3939ZZZZZZAT1': 7}
	# test5 = [['4967ZZZZZZAT1', '+', ['1738ZZZZZZAT1', '+', '8050ZZZZZZAT1']], '+', '1743ZZZZZZAT1']
	# expression5 = {'4967ZZZZZZAT1': 2, '1738ZZZZZZAT1': 3, '8050ZZZZZZAT1': 4, '1743ZZZZZZAT1': 5}

	# genes1 = expression1.keys()
	# genes2 = expression2.keys()
	# genes3 = expression3.keys()
	# genes4 = expression4.keys()
	# genes5 = expression5.keys()

	# print "test 1"
	# print test1
	# print expression1
	# print aggregate(test1, expression1, genes1)
	# print "test 2"
	# print test2
	# print expression2
	# print aggregate(test2, expression2, genes2)
	# print "test 3"
	# print test3
	# print expression3
	# print aggregate(test3, expression3, genes3)
	# print "test 4"
	# print test4
	# print expression4
	# print aggregate(test4, expression4, genes4)
	# print "test 5"
	# print test5
	# print expression5
	# print aggregate(test5, expression5, genes5)

	print get_metabolite_associations('./RECON1.json')
