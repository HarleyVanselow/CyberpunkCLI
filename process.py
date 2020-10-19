body_parts = ['Torso', 'Head', 'Whole', 'Legs',
              'Feet', 'Anywhere', 'Knees', 'Arms']
fixed = []
with open('armor.csv') as a:
	for line in a.readlines()[1:]:
		content = line.rstrip().split(' ')
		description = []
		non_desc = 0
		for i, word in enumerate(content):
			if word not in body_parts and all([p not in word for p in body_parts]):
				description.append(word)
			else:
				non_desc = i
				break
		non_desc = ' '.join(content[non_desc:])
		description = ' '.join(description)		
		covers = ''
		rest = 0
		for i,char in enumerate(non_desc):
			if char.isalpha() or char in [' ','&','/']:
				covers += char
			else:
				rest = i
				break
		rest = non_desc[rest:].split(' ')[:3]
		print(description)
		print(covers)
		fixed.append('\t'.join([description,covers]+rest))

with open('armor_fixed.csv','w') as f:
	for line in fixed:
		f.write(line +'\n')

