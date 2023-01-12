
def leaf_process(tree: dict):
	
	print(f'LeafProcess START- Node name: {tree["name"]}, Node type: {tree["type"]}')
	print(f'LeafProcess ENDS- Node name: {tree["name"]}, Node type: {tree["type"]}, Returns {tree["returns"]}')

	return tree['returns']

def selector_process(tree: dict):
	
	print(f'SelectorProcess START- Node name: {tree["name"]}, Node type: {tree["type"]}')

	children = tree.get('children', [])
			
	for child in children:
		result = process(child) #self.methods[child['type']](child)
		if result == 'SUCCESS':
			print(f'SequenceProcess END- Node name: {tree["name"]}, Node type: {tree["type"]}, Returns: SUCCESS')
			return 'SUCCESS'

	print(f'SelectorProcess END- Node name: {tree["name"]}, Node type: {tree["type"]}, Returns: FAILURE')
	return 'FAILURE'

def sequence_process(tree: dict):
	
	print(f'SequenceProcess START- Node name: {tree["name"]}, Node type: {tree["type"]}')

	children = tree.get('children', [])
			
	for child in children:
		result = process(child) #self.methods[child['type']](child)
		if result != 'SUCCESS':
			print(f'SequenceProcess END- Node name: {tree["name"]}, Node type: {tree["type"]}, Returns: FAILURE')
			return 'FAILURE'

	print(f'SequenceProcess END- Node name: {tree["name"]}, Node type: {tree["type"]}, Returns: SUCCESS')
	return 'SUCCESS'

methods = {
	'sequence': sequence_process,
	'selector': selector_process,
	'leaf': leaf_process
}

def process(tree):
	methods[tree['type']](tree)


if __name__ == "__main__":

	b_tree_data = {
			"type": "selector",
			"name": "AI Root",
			"children": [
				{
					"type": "sequence",
					"name": "Chase Player",
					"children": [
						{
							"type": "leaf",
							"name": "Rotate to face BB entry",
							"script": ["some_script_name_and_path", {"face_entity": "$target"}],
							"returns": "SUCCESS"
						},
						{
							"type": "leaf",
							"name": "BTT_ChasePlayer",
							"returns": "SUCCESS"
						},
						{
							"type": "leaf",
							"name": "Move To",
							"script": ["some_move_to_script", {"position": "$targetPosition"}],
							"returns": "SUCCESS"
						}
					]
				},
				{
					"type": "sequence",
					"name": "Patrol",
					"children": [
						{
							"type": "leaf",
							"name": "BTT_FindRandomPatrol",
							"returns": "FAILURE"
						},
						{
							"type": "leaf",
							"name": "Move To",
							"returns": "SUCCESS"
						},
						{
							"type": "leaf",
							"name": "Wait",
							"script": ["wait_script", {"time_ms": 1000}],
							"returns": "FAILURE"
						}
					]
				},
				{
					"type": "leaf",
					"name": "Wait",
					"returns": "SUCCESS"
				}
			]
		}
	
	process(b_tree_data)
