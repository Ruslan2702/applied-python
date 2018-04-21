import datetime
import pickle
import socket

num_id = -1
# Следующие 2 значения записываются только при создании файла!
queue_dict = {}  # По ключу (имя очереди) лежат списки с кортежами из заданий:
                            # на первом месте length, на втором - data, на третьем - id

queues_status = {} # По ключу (имя очереди) лежат списки с кортежами из
                              # запущенных заданий: на первом месте - флаг: True -
                              # задание не выполняется и его можно брать на выполнение,
                              # на втором - время запуска (или None)
PERIOD = 300 # 5 минут

file_name = 'MYLOG.txt'
# Код для перезаписи файла. Выполняется 1 раз при первом запуске сервера!
# Также можно написать отдельный скрипт под это дело
with open(file_name, 'wb') as f:
    pickle.dump({}, f)
    pickle.dump({}, f)

def write_into_file(q_all, q_status):
    with open(file_name, 'wb') as f:
        pickle.dump(q_all, f)
        pickle.dump(q_status, f)

def read_from_file():
    with open(file_name, 'rb') as f:
        q_all = pickle.load(f)
        q_status = pickle.load(f)
        # print(q_all)
        # print(q_status)
    return (q_all, q_status)

def listen():
    connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    connection.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    connection.bind(('0.0.0.0', 5555))
    connection.listen(10)
    (queue_dict, queues_status) = read_from_file()

    while True:
        try:
            current_connection, address = connection.accept()
        except KeyboardInterrupt:
            break

        input_string = current_connection.recv(2048)
        input_list = input_string.split()
        if len(input_list) < 2:
            current_connection.send(b'INCORRECT DATA')
            current_connection.close()
            continue

        command_type = input_list[0]
        if command_type == b'ADD':
            global num_id
            num_id += 1
            queue_name = input_list[1]
            length = input_list[2].decode('utf8')
            data = input_list[3].decode('utf8')
            s_num_id = str(num_id)
            if queue_name not in queue_dict:
                queue_dict[queue_name] = [(length, data, s_num_id)]
                queues_status[queue_name] = [[True, None]]
                current_connection.send(s_num_id.encode('utf8'))
                current_connection.close()
                write_into_file(queue_dict, queues_status)
                continue
            else:
                queue_dict[queue_name].append((length, data, s_num_id))
                queues_status[queue_name].append([True, None])
                current_connection.send((str(num_id)).encode('utf8'))
                current_connection.close()
                write_into_file(queue_dict, queues_status)
                continue

        elif command_type == b'GET':
            queue_name = input_list[1]
            if (queue_name not in queue_dict or len(queue_dict[queue_name]) == 0 or
                            not any([x[0] for x in queues_status[queue_name]])):
                current_connection.send(b'NONE')
                current_connection.close()
                continue
            else:
                idx = 0
                for i, task_status in enumerate(queues_status[queue_name]):
                    if not task_status[0]:
                        task_was_started_in = queues_status[queue_name][i][1]
                        delta = datetime.datetime.now() - task_was_started_in
                        if delta.total_seconds() > PERIOD:
                            task_status[0] = True
                            idx = i
                            break
                    else:
                        idx = i
                        break

                task_to_get = queue_dict[queue_name][idx]
                id = task_to_get[2]
                length = task_to_get[0]
                data = task_to_get[1]
                response_string = '{0} {1} {2}'.format(id, length, data).encode('utf8')
                current_connection.send(response_string)
                queues_status[queue_name][idx][0] = False
                queues_status[queue_name][idx][1] = datetime.datetime.now()
                current_connection.close()
                write_into_file(queue_dict, queues_status)
                continue

        elif command_type == b'IN':
            queue_name = input_list[1]
            id_to_check = input_list[2].decode('utf8')
            flag = False

            for t in queue_dict[queue_name]:
                if t[2] == id_to_check:
                    flag = True
            if flag:
                current_connection.send(b'YES')
                current_connection.close()
                continue
            else:
                current_connection.send(b'NO')
                current_connection.close()
                continue

        elif command_type == b'ACK':
            queue_name = input_list[1]
            id_to_check = input_list[2].decode('utf8')
            idx = None
            for i, t in enumerate(queue_dict[queue_name]):
                if t[2] == id_to_check:
                    idx = i
            if idx is not None:
                queue_dict[queue_name].pop(idx)
                queues_status[queue_name].pop(idx)
                current_connection.send(b'YES')
                current_connection.close()
                write_into_file(queue_dict, queues_status)
                continue
            else:
                current_connection.send(b'NO')
                current_connection.close()
                continue

        else:
            current_connection.send(b'INCORRECT DATA')
            current_connection.close()
            continue



if __name__ == '__main__':
    listen()
