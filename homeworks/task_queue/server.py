import datetime
import pickle
import socket


class TcpServer:
    task_id = 0
    log_file = 'LOGS.txt'
    PERIOD = 300


    def __init__(self):
        self._queue_dict = {}
        self._queues_status = {}
        self._save_info_to_file(TcpServer.log_file, self._queue_dict, self._queues_status)


    def start_listening(self):
        self._connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._connection.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self._connection.bind(('0.0.0.0', 5555))
        self._connection.listen(10)

        while True:
            try:
                self._current_connection, self._address = self._connection.accept()
            except KeyboardInterrupt:
                break

            (self._queue_dict, self._queues_status) = self._get_info_from_file(TcpServer.log_file)

            input_string = self._current_connection.recv(2048)
            input_list = input_string.split()
            if len(input_list) < 2:
                self._current_connection.send(b'INCORRECT DATA')
                self._current_connection.close()

            command_type = input_list[0]
            if command_type == b'ADD':
                num_id = self._add_task_in_queue(input_list)
                self._current_connection.send(num_id.encode('utf8'))
                self._current_connection.close()

            elif command_type == b'GET':
                response = self._get_task_from_queue(input_list)
                self._current_connection.send(response.encode('utf8'))
                self._current_connection.close()

            elif command_type == b'IN':
                response = self._is_task_in_queue(input_list)
                self._current_connection.send(response.encode('utf8'))
                self._current_connection.close()

            elif command_type == b'ACK':
                response = self._ack_task(input_list)
                self._current_connection.send(response.encode('utf8'))
                self._current_connection.close()

            else:
                self._current_connection.send(b'INCORRECT DATA')
                self._current_connection.close()


    def _add_task_in_queue(self, input_list):
        s_num_id = str(TcpServer.task_id)
        TcpServer.task_id += 1
        queue_name = input_list[1]
        length = input_list[2].decode('utf8')
        data = input_list[3].decode('utf8')
        if queue_name not in self._queue_dict:
            self._queue_dict[queue_name] = [(length, data, s_num_id)]
            self._queues_status[queue_name] = [[True, None]]
        else:
            self._queue_dict[queue_name].append((length, data, s_num_id))
            self._queues_status[queue_name].append([True, None])
        self._save_info_to_file(TcpServer.log_file, self._queue_dict, self._queues_status)
        return s_num_id


    def _get_task_from_queue(self, input_list):
        queue_name = input_list[1]
        if (queue_name not in self._queue_dict or len(self._queue_dict[queue_name]) == 0 or
                not any([x[0] for x in self._queues_status[queue_name]])):
            return 'NONE'
        else:
            idx = 0
            for i, task_status in enumerate(self._queues_status[queue_name]):
                if not task_status[0]:
                    task_was_started_in = self._queues_status[queue_name][i][1]
                    delta = datetime.datetime.now() - task_was_started_in
                    if delta.total_seconds() > TcpServer.PERIOD:
                        task_status[0] = True
                        idx = i
                        break
                else:
                    idx = i
                    break
            task_to_get = self._queue_dict[queue_name][idx]
            id = task_to_get[2]
            length = task_to_get[0]
            data = task_to_get[1]
            response_string = '{0} {1} {2}'.format(id, length, data)
            self._queues_status[queue_name][idx][0] = False
            self._queues_status[queue_name][idx][1] = datetime.datetime.now()
            self._save_info_to_file(TcpServer.log_file, self._queue_dict, self._queues_status)
            return response_string


    def _is_task_in_queue(self, input_list):
        queue_name = input_list[1]
        id_to_check = input_list[2].decode('utf8')
        flag = False

        for t in self._queue_dict[queue_name]:
            if t[2] == id_to_check:
                flag = True
        if flag:
            return 'YES'
        else:
            return 'NO'


    def _ack_task(self, input_list):
        queue_name = input_list[1]
        id_to_check = input_list[2].decode('utf8')
        idx = None
        for i, t in enumerate(self._queue_dict[queue_name]):
            if t[2] == id_to_check:
                idx = i
        if idx is not None:
            self._queue_dict[queue_name].pop(idx)
            self._queues_status[queue_name].pop(idx)
            self._save_info_to_file(TcpServer.log_file, self._queue_dict, self._queues_status)
            return 'YES'
        else:
            return 'NO'


    def _save_info_to_file(self, file_name, queues, status):
        with open(file_name, 'wb') as f:
            pickle.dump(queues, f)
            pickle.dump(status, f)


    def _get_info_from_file(self, file_name):
        with open(file_name, 'rb') as f:
            queues = pickle.load(f)
            status = pickle.load(f)
        return (queues, status)


if __name__ == '__main__':
    myserver = TcpServer()
    myserver.start_listening()