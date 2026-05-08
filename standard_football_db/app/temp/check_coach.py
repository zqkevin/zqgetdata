import json

data = json.load(open('data/teams_with_players.json', encoding='utf-8'))
coach_ids = [t['coach']['id'] for t in data if t.get('coach')]
print(f'总教练数: {len(coach_ids)}')
print(f'唯一教练数: {len(set(coach_ids))}')

from collections import Counter
counter = Counter(coach_ids)
duplicates = {k: v for k, v in counter.items() if v > 1}
print(f'重复的教练ID: {len(duplicates)}个')
for cid, count in list(duplicates.items())[:5]:
    print(f'  ID {cid}: 出现{count}次')
