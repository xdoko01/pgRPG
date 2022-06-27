def translate_str(for_trans: str, trans_dict: dict, prefix: str) -> str:
	'''Substitute words in for_trans string that start
	with prefix by values from the trans_dict dictionary.
	'''

	trans_str = for_trans

	for k, v in trans_dict.items():
		trans_str = trans_str.replace(prefix + str(k), str(v))
	
	return trans_str

if __name__ == '__main__':

	for_trans = "hello %player. You have scored %score and achieved %level of experience."
	trans_dict = {"player": "O. Dokoupil", "score": 500, "level": 25}

	print(translate_str(for_trans=for_trans, trans_dict=trans_dict, prefix='%'))
