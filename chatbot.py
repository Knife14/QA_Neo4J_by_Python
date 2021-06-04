'''
title: 互联网+ 项目 问答系统机器人
writer: 山客
date: 2021.5.18
'''

from question_classifier import *
from question_parser import *
from answer_search import *


class ChatBot:
	'''
	:title: 问答系统机器人
	:type: class
	'''
	def __init__(self):
		self.classifier = Q_Classifier()  # 问题划分类
		self.parser = Q_Parser()  # 问题分析器
		self.searcher = A_Search()  # 搜索回答

	def main(self, question: str) -> str:
		'''
		:func_name: 主函数
		:input: question: str - 用户输入问题
		:output: final_answer: str - 问答系统分析回答
		'''
		answer = "您的问题太过深奥啦！我的智能程度还有限……"

		res_classify = self.classifier.classify(question)
		print("res_classify: ", res_classify)

		if not res_classify:
			# 若问题分析没有结果，直接返回answer
			return answer

		res_sql = self.parser.parser_main(res_classify)
		# print('res_sql: ', res_sql)

		final_answer = self.searcher.search_main(res_sql)

		if not final_answer:
			return answer
		else:
			answer = ''.join(final_answer[0])
			return answer


if __name__ == '__main__':
	runsever = ChatBot()
	while 1:
		question = input('咨询(输入end#时咨询结束):')
		if question == "end#":
			print("咨询结束，期待您再次使用我们的问答系统！")
			break
		answer = runsever.main(question)
		print('客服:', answer)
