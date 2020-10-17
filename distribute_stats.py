import random
stats = ['int','ref','attr','luck','cool','tech','ma','bt','emp']
min = 2
max = 10
pool = 40
result = {}
random.shuffle(stats)
for i,stat in enumerate(stats):
    max = max if (pool-max)/(len(stats)-i) > 2 else min
    point = random.randrange(min,max+1)
    result[stat] = point
    pool -= point
print(result)