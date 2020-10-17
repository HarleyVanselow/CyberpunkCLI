import random
stats = ['int','ref','attr','luck','cool','tech','ma','bt','emp']
min_stat = 2
max_stat = 10
pool = 40
result = {}
random.shuffle(stats)
for i,stat in enumerate(stats):
    max_stat = min(10, pool - (len(stats) - i - 1) * min_stat)
    point = random.randrange(min_stat, max_stat + 1)
    result[stat] = point
    pool -= point
print(result)