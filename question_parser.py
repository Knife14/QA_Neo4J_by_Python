'''
title: 互联网+ 项目 问题分析器
writer: 山客
latest update time: 2021.6.1
'''


class Q_Parser:
    def build_entitydict(self, args: dict) -> dict:
        '''
        :func_name: 构建实体节点
        :input: args - dict:
        :output: entity_dict - dict:
        '''
        entity_dict = {}
        for arg, types in args.items():
            for type in types:
                if type not in entity_dict:
                    entity_dict[type] = [arg]
                else:
                    entity_dict[type].append(arg)

        # print("entity_dict: ", entity_dict)  # test
        return entity_dict

    def sql_transfer(self, question_type: str, entities: list) -> list:
        '''
        :func_name: 根据问题调用相应的sql语句
        :input: question_type - str: 问题类型
                entities - list: 实体节点
        :output: sql - list: 数据关系
        '''
        if not entities:
            return []
        # print("entities: ", entities)  # test

        # 查询语句
        sql = []

        # 查询原因
        # 职能
        if question_type == 'worktype':
            sql += [
                "MATCH (m:Person) -[r]-> (n) where m.name = '{0}' return m.name, type(r), n.name"
                .format(i) for i in entities
            ]
        # 规定
        if question_type == 'constructionmanagement':
            sql += [
                "MATCH (m:subject) -[r]-> (n) where m.name = '{0}' return m.name, type(r), n.name"
                .format(i) for i in entities
            ]
            sql += [
                "MATCH (m:subject) where m.name = '{0}' return m.name,m.content"
                .format(i) for i in entities
            ]
        # 关系
        if question_type == 'relationship':
            try:
                sql += [
                    "MATCH (m) -[r]-> (n) where m.name = '{m_name}' and n.name = '{n_name}' return m.name, type(r), n.name"
                    .format(m_name=entities[0], n_name=entities[1])
                ]
            except:
                pass

        return sql

    def parser_main(self, res_classify: dict) -> list:
        '''
        :func_name: 问题分析主函数
        :input:res_classify - dict: 问题分析结果
        :output: sqls - list: 问题对应数据库（含关系）
        '''
        args = res_classify['content']
        q_types = res_classify['question_types']

        # print("q_types: ", q_types)  # test

        entity_dict = self.build_entitydict(args)  # 构建实体节点

        print("entity_dict: ", entity_dict)  # test

        sqls = []  # output

        for question_type in q_types:
            # 初始化数据关系
            _sql = {}
            _sql['question_type'] = question_type

            sql = []

            # 分类处理问题
            if question_type == 'worktype':
                sql = self.sql_transfer(question_type, entity_dict.get('worktype'))
            elif question_type == 'constructionmanagement':
                sql = self.sql_transfer(question_type, entity_dict.get('constructionmanagement'))
            elif question_type == 'relationship':
                sql = self.sql_transfer(question_type, entity_dict.get('worktype'))

            if sql:
                _sql['sql'] = sql
                sqls.append(_sql)

        # print("sqls: ",sqls)  # test
        return sqls


if __name__ == '__main__':
    test = Q_Parser()
