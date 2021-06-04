'''
title: 互联网+ 项目 答案检索器
writer: 山客
latest update time: 2021.6.1
'''

from py2neo import Graph


class A_Search:
    def __init__(self):
        self.g = Graph("http://localhost:7474", auth=("neo4j", "aA1129~@"))
        self.num_limit = 20

    def search_main(self, sqls: list) -> list:
        '''
        :func_name: 答案检索主函数
        :input: sql - list: 问题数据关系
        :output: final_answers - list: 答案
        '''
        final_answers = []

        for sql in sqls:
            # 遍历问题数据关系
            question_type = sql['question_type']
            queriers = sql['sql']
            answers = []

            # print("len(query): " + str(len(queriers)))  # test

            for query in queriers:
                ress = self.g.run(query).data()
                answers += ress

            # print("answers: ", answers)  # test
            # print("len(answers): ", len(answers))  # test

            final_answer = self.answer_prettify(question_type, answers)

            if final_answer:
                final_answers.append(final_answer)

        return final_answers

    def answer_prettify(self, question_type: str, answers: list) -> list:
        '''
        :func_name: 调用回答模板
        :input: question_type - str: 问题类型
                answers - list: 回答
        :output:final_answer - list: 最终回答
        '''
        final_answer = []

        if not answers:
            return final_answer

        # 职能
        if question_type == 'worktype':
            subject = answers[0]['m.name']  # 主语
            desc = [i['type(r)'] for i in answers]  # 行为描述
            object = [i['n.name'] for i in answers]  # 对象 / 宾语
            # content = answers[0]['type(r)'] + answers[0]['n.name']  # test
            # print("desc: ", desc)  # test
            # print("content: ", object)  # test
            '''
            final_answer += subject
            for i in range(len(desc)):
                final_answer += desc[i]
                final_answer += object[i]
                if i < len(desc) - 1:
                    final_answer += ';'
                else:
                    final_answer += '。'
            '''
            final_answer = '{m_name}需要:\n{n_name}'.format(
                m_name=subject, n_name=';\n'.join(desc[i] + object[i] for i in range(len(desc)))
            )

        # 规定/内容
        elif question_type == 'constructionmanagement':
            try:
                tmp_answers = answers[:len(answers) - 1]

                subject = tmp_answers[0]['m.name']  # 主语
                desc = [i['type(r)'] for i in tmp_answers]  # 行为描述
                object = [i['n.name'] for i in tmp_answers]  # 对象 / 宾语
                # content = answers[0]['type(r)'] + answers[0]['n.name']  # test
                # print("desc: ", desc)  # test
                # print("content: ", object)  # test
                final_answer = '{m_name}:\n{content}'.format(
                    m_name=subject, content=';\n'.join(desc[i] + object[i] for i in range(len(desc)))
                )
            except:
                subject = answers[0]['m.name']  # 主语
                object = answers[0]['m.content']  # 对象 / 宾语
                final_answer = subject + '是' + object

        # 关系
        elif question_type == 'relationship':
            subject = answers[0]['m.name']  # 主语
            desc = [i['type(r)'] for i in answers]  # 行为描述
            object = answers[0]['n.name']  # 对象 / 宾语
            # content = answers[0]['type(r)'] + answers[0]['n.name']  # test
            # print("desc: ", desc)  # test
            # print("content: ", object)  # test
            final_answer = '{m_name}负责{relationship}{n_name}'.format(
                m_name=subject, n_name=object, relationship='、'.join(desc[i] for i in range(len(desc))))

        return final_answer


if __name__ == '__main__':
    test = A_Search()
