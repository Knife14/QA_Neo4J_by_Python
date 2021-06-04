'''
title: 模糊检索
writer: 山客
the_last_update_date: 2021.6.1
'''

import re  # 正则表达式匹配
from fuzzywuzzy import fuzz  # str相似度


def fuzzyseracher(user_input, collection):
    suggestions = []
    pattern = '.*'.join(user_input)  # Converts 'djm' to 'd.*j.*m'
    regex = re.compile(pattern)  # Compiles a regex.
    for item in collection:
        match = regex.search(item)  # Checks if the current item matches the regex.
        if match:
            suggestions.append(item)

    # print("len(suggestions): ", len(suggestions))  # test
    # print("suggestions: ", suggestions)  # test

    # 若匹配长度为1，直接返回该字符串
    if len(suggestions) == 1:
        return suggestions[0]

    # 若存在匹配相似度达100的字符串，直接返回该字符串
    suggestions = sorted(suggestions, key=lambda x: fuzz.ratio(user_input, x))

    try:
        suggestion = suggestions.pop()
    except:
        suggestion = ""

    return suggestion


if __name__ == '__main__':
    collection = ['django_migrations.py',
                  'django_admin_log.py',
                  'main_generator.py',
                  'migrations.py',
                  'api_user.doc',
                  'user_group.doc',
                  'accounts.txt',
    ]

    print(fuzzyseracher('djm', collection))
