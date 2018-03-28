# -*- encoding: utf-8 -*-
import re
import collections
import operator

def parse(
    ignore_files=False,
    ignore_urls=[],
    start_at=None,
    stop_at=None,
    request_type="GET",
    ignore_www=False,
    slow_queries=False
):
    regular_expression_for_request_str = r'://\S*\s'
    regular_expression_for_request_values = r'\d"\s\d{3}\s\d*'
    regular_expression_for_type_of_request = r'\b\w{3,4}\shttp'
    regular_expression_for_request_date = r'\d{2}/\w{3,4}/\d{4}\s\d\d:\d\d:\d\d'

    f = open('log.log', 'r')

    dict_request_to_count = collections.defaultdict(int)
    dict_request_to_time = collections.defaultdict(int)

    dict_month_name_to_val = {
        "Jan":1,
        "Feb":2,
        "Mar":3,
        "Apr":4,
        "May":5,
        "June":6,
        "July":7,
        "Aug":8,
        "Sept":9,
        "Oct":10,
        "Nov":11,
        "Dec":12
    };

    if start_at:
        start_at_list = re.findall(r'\w{2,4}', start_at)
        start_at_list[1] = dict_month_name_to_val(start_at_list[1])

    if stop_at:
        stop_at_list = re.findall(r'\w{2,4}', stop_at)
        stop_at_list[1] = dict_month_name_to_val(stop_at_list[1])

    for line in f:
        request_string = re.search(regular_expression_for_request_str, line)
        if request_string:
            request_string = request_string.group()

            type_of_request = re.search(regular_expression_for_type_of_request, line).group()
            type_of_request = type_of_request.split(' ')[0]
            if type_of_request != request_type:
                continue

            request_date = re.search(regular_expression_for_request_date, line).group()
            request_date_list = re.findall(r'\w{2,4}', request_date)

            if start_at:
                if request_date_list[2] < start_at_list[2]:  # Проверяем год
                    continue
                elif request_date_list[1] < start_at_list[1]:  # Проверяем месяц
                    continue
                elif request_date_list[0] < start_at_list[0]:  # Проверяем день
                    continue
                elif request_date_list[3] < start_at_list[3]:  # Проверяем часы
                    continue
                elif request_date_list[4] < start_at_list[4]:  # Проверяем минуты
                    continue
                elif request_date_list[5] < start_at_list[5]:  # Проверяем секунды
                    continue
            if stop_at:
                if request_date_list[2] > stop_at_list[2]:  # Проверяем год
                    continue
                elif request_date_list[1] > stop_at_list[1]:  # Проверяем месяц
                    continue
                elif request_date_list[0] > stop_at_list[0]:  # Проверяем день
                    continue
                elif request_date_list[3] > stop_at_list[3]:  # Проверяем часы
                    continue
                elif request_date_list[4] > stop_at_list[4]:  # Проверяем минуты
                    continue
                elif request_date_list[5] > stop_at_list[5]:  # Проверяем секунды
                    continue                

            request_string = request_string.split('?')[0]
            if ignore_files:
                if re.search(r'://\S*/', line).group().strip() != request_string.strip():
                    continue
            request_string = request_string[3:]
            
            if request_string in ignore_urls:
                continue

            if ignore_www and request_string[:3] == "www":
                request_string = request_string[4:]

            dict_request_to_count[request_string] += 1
            request_values = re.search(regular_expression_for_request_values, line).group()
            request_code = int(request_values[3:6]) # Т.к. знаем, что код состоит из 3 цифр
            request_time = int(request_values[7:])
            dict_request_to_time[request_string] += request_time

    sorted_dict_request_to_count = sorted(dict_request_to_count.items(), key=operator.itemgetter(1), reverse = True)
    sorted_dict_request_to_time = sorted(dict_request_to_time.items(), key=operator.itemgetter(1), reverse = True)

    top_urls = []
    slow_urls = []
    for i in range(5):
        top_urls.append(sorted_dict_request_to_count[i][1])

    for i in range(5):
        slow_urls.append(sorted_dict_request_to_time[i][1] 
            // dict_request_to_count[sorted_dict_request_to_time[i][0]])

    f.close()

    if slow_queries:
        return sorted(slow_urls, reverse = True)

    return top_urls
