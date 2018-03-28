# -*- encoding: utf-8 -*-
import re
import collections
import operator
import datetime


def check_date(line, start_at, stop_at):
            regular_expression_for_request_date = r'\d{2}/\w{3,4}/\d{4}\s\d\d:\d\d:\d\d'
            request_date_str = re.search(regular_expression_for_request_date, line).group()
            month = re.findall(r'\w{2,4}', request_date_str)[1]
            year = re.findall(r'\w{2,4}', request_date_str)[2]
            dict_month_name_to_val = {
                "Jan":"1",
                "Feb":"2",
                "Mar":"3",
                "Apr":"4",
                "May":"5",
                "June":"6",
                "July":"7",
                "Aug":"8",
                "Sept":"9",
                "Oct":"10",
                "Nov":"11",
                "Dec":"12"
            };
            request_date_str = request_date_str.replace(month, dict_month_name_to_val[month])
            request_date_str = request_date_str.replace(year, year[2:])
            request_datetime = datetime.datetime.strptime(request_date_str, "%d/%m/%y %H:%M:%S")
            if request_datetime < start_at:
                return False  
            elif request_datetime > stop_at:
                return False
            else:
                return True


def check_flags(line, request_string, request_type, ignore_files, ignore_urls, ignore_www):
    regular_expression_for_type_of_request = r'\b\w{3,4}\shttp'
    type_of_request = re.search(regular_expression_for_type_of_request, line).group()
    type_of_request = type_of_request.split(' ')[0]
    if type_of_request != request_type:
        return False

    request_string = request_string.split('?')[0]
    if ignore_files:
        if re.search(r'://\S*/', line).group().strip() != request_string.strip():
            return False
    request_string = request_string[3:]
    
    if request_string in ignore_urls:
        return False

    if ignore_www and request_string[:3] == "www":
        request_string = request_string[4:]

    return request_string


def get_request_values(line, ):    
    regular_expression_for_request_values = r'\d"\s\d{3}\s\d*'
    request_values = re.search(regular_expression_for_request_values, line).group()
    request_code = int(request_values[3:6]) # Т.к. знаем, что код состоит из 3 цифр
    request_time = int(request_values[7:])
    return request_code, request_time


def parse(ignore_files=False, ignore_urls=[], start_at=None, 
            stop_at=None, request_type="GET", ignore_www=False, slow_queries=False):
    regular_expression_for_request_str = r'://\S*\s'
    f = open('log.log', 'r')
    dict_request_to_count = collections.defaultdict(int)
    dict_request_to_time = collections.defaultdict(int)

    for line in f:
        request_string = re.search(regular_expression_for_request_str, line)
        if request_string:
            request_string = request_string.group()
            request_string = check_flags(line, request_string, request_type, ignore_files, ignore_urls, ignore_www)
            if not request_string:
                continue
            if start_at or stop_at:
                if not check_date(line, start_at, stop_at):
                    continue
            dict_request_to_count[request_string] += 1
            request_code, request_time = get_request_values(line,)
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
