import datetime
import pickle
import socket


PERIOD = 300 # 5 минут

class Saver:
    def __init__(self, file_name):
        self._file = file_name

    def write_into_file(self, obj_to_save):
        with open(self._file, 'wb') as f:
            pickle.dump(obj_to_save, f)

    def read_from_file(self):
        with open(self._file, 'rb') as f:
            load_obj = pickle.load(f)
        return load_obj


class Queue:
    def __init__(self):
        self._queues_dict = {}
        self._queues_status = {}
        self._next_id = 0
        Saver.write_into_file(Saver('MYLOG.txt'), self)

    def add_task_in_queue(self, input_list, next_id):
        queue_name = input_list[1]
        length = input_list[2].decode('utf8')
        data = input_list[3].decode('utf8')
        if queue_name not in self._queues_dict:
            self._queues_dict[queue_name] = [(length, data, next_id)]
            self._queues_status[queue_name] = [[True, None]]
        else:
            self._queues_dict[queue_name].append((length, data, next_id))
            self._queues_status[queue_name].append([True, None])

    def get_task_from_queue(self, input_list):
        queue_name = input_list[1]
        if (queue_name not in self._queues_dict or len(self._queues_dict[queue_name]) == 0 or
                not any([x[0] for x in self._queues_status[queue_name]])):
            return 'NONE'
        else:
            idx = 0
            for i, task_status in enumerate(self._queues_status[queue_name]):
                if not task_status[0]:
                    task_was_started_in = self._queues_status[queue_name][i][1]
                    delta = datetime.datetime.now() - task_was_started_in
                    if delta.total_seconds() > PERIOD:
                        task_status[0] = True
                        idx = i
                        break
                else:
                    idx = i
                    break
            task_to_get = self._queues_dict[queue_name][idx]
            id = task_to_get[2]
            length = task_to_get[0]
            data = task_to_get[1]
            response_string = '{0} {1} {2}'.format(id, length, data)
            self._queues_status[queue_name][idx][0] = False
            self._queues_status[queue_name][idx][1] = datetime.datetime.now()
            return response_string

    def is_task_in_queue(self, input_list):
        queue_name = input_list[1]
        id_to_check = input_list[2].decode('utf8')
        flag = False
        if queue_name not in self._queues_dict:
            return 'NO'

        for t in self._queues_dict[queue_name]:
            if t[2] == id_to_check:
                flag = True
        if flag:
            return 'YES'
        else:
            return 'NO'

    def ack_task(self, input_list):
        queue_name = input_list[1]
        id_to_check = input_list[2].decode('utf8')
        idx = None
        for i, t in enumerate(self._queues_dict[queue_name]):
            if t[2] == id_to_check:
                idx = i
        if idx is not None:
            self._queues_dict[queue_name].pop(idx)
            self._queues_status[queue_name].pop(idx)
            return 'YES'
        else:
            return 'NO'





def listen(q, saver):
    connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    connection.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    connection.bind(('0.0.0.0', 5555))
    connection.listen(10)

    while True:
        try:
            current_connection, address = connection.accept()
        except KeyboardInterrupt:
            break

        q = saver.read_from_file()

        input_string = current_connection.recv(2048)
        input_list = input_string.split()
        if len(input_list) < 2:
            current_connection.send(b'INCORRECT DATA')
            current_connection.close()

        command_type = input_list[0]
        if command_type == b'ADD':
            s_num_id = str(q._next_id)
            q.add_task_in_queue(input_list, s_num_id)
            q._next_id += 1
            saver.write_into_file(q)
            current_connection.send((s_num_id).encode('utf8'))

        elif command_type == b'GET':
            response_string = q.get_task_from_queue(input_list)
            saver.write_into_file(q)
            current_connection.send(response_string.encode('utf8'))

        elif command_type == b'IN':
            response_string = q.is_task_in_queue(input_list)
            current_connection.send(response_string.encode('utf8'))

        elif command_type == b'ACK':
            response_string = q.ack_task(input_list)
            saver.write_into_file(q)
            current_connection.send(response_string.encode('utf8'))

        current_connection.close()



if __name__ == '__main__':
    q = Queue()
    saver = Saver('MYLOG.txt')
    listen(q, saver)
