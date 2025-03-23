# This routine sums the values of different keys
# Needs an additional test (at $$$ below) only to create total field for selected answers 
# and initial consistency needs to ensure these are all numeric answer types


# create some test data
a={1: {'A': 23, 'B': 300}, 2: {'A': 3, 'B': 40}, 5:{'A': 1000, 'B': 2000}}
print('a is: ',a)


# set up variable names for running totals, and record count, as a list
names=[]
for key in a[1]: # $$$ insert extra check here $$$
	name_original=str(key)
	name_total=name_original+'_total'
	names.append([name_original,name_total])

# create new dictionay items
a['Total']={}
a['Total']['record_count']=0
for name in names:
	a['Total'][name[1]]=0

# compute running totals and record count (note only one iteration however many fields to be summed)
for i in iter(a):
	if i!='Total':
		a['Total']['record_count']+=1
		for name in names:
			a['Total'][name[1]]+=a[i][name[0]]

print('a is now: ',a)