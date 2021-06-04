'''
title: 互联网+ 项目 问题分类器
writer: 山客
the_last_update_time: 2021.6.1
'''

import os
import ahocorasick  # 多模式匹配 AC自动机
from FuzzySearch import *


class Q_Classifier:
	'''
	:title: 问题分析器
	:type: class
	'''
	def __init__(self):
		# 模型初始化
		print("model init loading....")

		cur_dir = '/'.join(os.path.abspath(__file__).split('/')[:-1])  # 路径

		# 特征词路径
		self.worktype_path = os.path.join(cur_dir, 'dict/WorkType.txt')  # 工种
		self.constmanage_path = os.path.join(cur_dir, 'dict/ConstructionManagement.txt')  # 现场施工管理
		# 加载特征词
		self.worktype_word = [i.strip() for i in open(self.worktype_path,encoding="utf-8") if i.strip()]
		self.constmanage_word = [i.strip() for i in open(self.constmanage_path,encoding="utf-8") if i.strip()]

		# 构造领域
		self.region_word = set(self.worktype_word + self.constmanage_word)
		self.region_tree = self.build_actree(list(self.region_word))

		# 构建词典
		self.wordtype_dict = self.build_wordtype_dict()

		# 问句疑问词
		self.role_question_word = [
			'职位', '担任', '作为', '领衔', '身为', '职能',
			'干什么', '干些', '做什么', '做些',
			'干嘛',
		]  # 职能

		self.job_question_word = [
			'内容', '规定', '如何', '包涵',
			'包括', '涵盖', '含括', '覆盖',
			'有多少', '有什么', '有些'
		]  # 工作内容

		self.att_question_word = ['注意', '小心', '担心', '留意']  # 工地注意事项

		self.rela_question_word = [
			'关系', '联系', '关联', '牵连', '干系',
			'有什么关系', '有什么联系', '有什么关联',
			'有什么干系', '有什么牵连'
		]  # 内容关系

		# 模型初始化完毕
		print('model init finished....')

	def build_actree(self, wordList):
		'''
		:func_name: 构建领域
		:input: wordList:set - 工种与施工管理内容的集合
		:output: actree: automaton - 领域
		:effect: 加速过滤特征词
		'''
		actree = ahocorasick.Automaton()

		for index, word in enumerate(wordList):
			actree.add_word(word, (index, word))

		actree.make_automaton()

		return actree

	def build_wordtype_dict(self) -> dict:
		'''
		:func_name: 构建词典
		:input:
		:output: wordtype_dict:dict - 特征词对应类型
		'''
		wordtype_dict = {}

		for word in self.region_word:
			wordtype_dict[word] = []

			if word in self.worktype_word:
				wordtype_dict[word].append('worktype')
			if word in self.constmanage_word:
				wordtype_dict[word].append('constructionmanagement')

		return wordtype_dict

	def filter_ques(self, question: str) -> dict:
		'''
		:func_name: 问句过滤
		:input: question - str: 用户输入问题内容
		:output: final_dict - dict: 精简问题数据
		'''

		# 问句过滤
		region_word = []
		for i in self.region_tree.iter(question):
			word = i[1][1]
			region_word.append(word)
		# print("region word: ", region_word)  # test

		stop_word = []
		for word_1 in region_word:
			for word_2 in region_word:
				if word_1 in word_2 and word_1 != word_2:
					stop_word.append(word_1)
		# print("stop_word: ", stop_word)  # test

		final_word = [i for i in region_word if i not in stop_word]
		final_dict = {i: self.wordtype_dict.get(i) for i in final_word}

		return final_dict

	def check_words(self, words: list, question: str):
		'''
		:func_name: 查询单词
		:input: words: list - 问句疑问词集合; question: str - 用户输入问题内容
		:output: bool - 布尔值，用于判断
		'''

		for word in words:
			if word in question:
				return True

		return False

	def classify(self, question: str) -> dict:
		'''
		:func_name: 问题分类主函数
		:input: question - str: 用户输入问题内容
		:output: data - dict: 问题分析数据
		'''
		data = {}  # 问题分析数据

		# 模糊搜索
		symbol_Punct = [
			'与', '和', '或', '是', '有', '对', '的',
			'包', '如', '要', '干', '作', '含', '覆',
			'关', '联', '牵', '涵', '内', '规', '担',
			'领', '身', '职', '分', '都',
			'!', '。', '，', '？', '?', '!', ',', '.'
		]  # 断句标志
		fuzzy_inputs = []
		fuzzy_ress = []
		index = 0  # 主宾语开始下标

		l = len(question)
		for i in range(l):
			if question[i] in symbol_Punct:
				tmp = question[index: i]
				fuzzy_inputs.append(tmp)
				index = i + 1
			if len(fuzzy_inputs) >= 2:
				break
		# print("fuzzy_inputs: ", fuzzy_inputs)  # test

		for fuzzy_input in fuzzy_inputs:
			fuzzy_ress.append(fuzzyseracher(fuzzy_input, self.constmanage_word + self.worktype_word))
		# print("fuzzy_ress: ", fuzzy_ress)  # test

		# 修改问题
		if fuzzy_ress:
			for i in range(len(fuzzy_ress)):
				if fuzzy_ress[i] and fuzzy_inputs[i]:
					question = question.replace(fuzzy_inputs[i], fuzzy_ress[i])
		# print("question: ", question)  # test

		# 问句过滤
		construction_dict = self.filter_ques(question)
		# print("construction_dict: ", construction_dict)   # test

		if not construction_dict:
			return {}

		data['content'] = construction_dict  # 过滤后的精简问题数据

		# 收集问句当中所涉及到的实体类型
		types = []
		for _type in construction_dict.values():
			types += _type
		# print("types: ", types)  # test

		question_type = 'others'  # 初始化问题的类型
		question_types = []  # 问题总种类

		# 职能
		if self.check_words(self.role_question_word, question) and ('worktype' in types):
			# print("Join Done!")  # test
			question_type = 'worktype'
			question_types.append(question_type)
		# 规定
		if self.check_words(self.job_question_word, question) and ('constructionmanagement' in types):
			# print("Join Done!")  # test
			question_type = 'constructionmanagement'
			question_types.append(question_type)
		# 注意
		if self.check_words(self.att_question_word, question) and ('constructionmanagement' in types):
			# print("Join Done!")  # test
			question_type = 'constructionmanagement'
			question_types.append(question_type)
		# 关系
		if self.check_words(self.rela_question_word, question) and ('worktype' in types):
			# print("Join Done!")  # test
			question_type = 'relationship'
			question_types.append(question_type)

		# 若未能找到相应职位的外部查询信息，则将该职位的描述信息返回
		if question_types == [] and 'worktype' in types:
			question_types = ['worktype']

		data['question_types'] = question_types

		# print("data: ", data)  # test
		return data


if __name__ == '__main__':
	test = Q_Classifier()
	while 1:
		question = input("input a question(if put 'end#',ending ): ")
		if question == "end#":
			print("Thanks using!")
			break
		data = test.classify(question)
		print(data)
