from unittest import TestCase
import time
import socket
import subprocess

class ServerBaseTest(TestCase):
    def setUp(self):
        self.server = subprocess.Popen(['python3', 'server.py'])
        time.sleep(0.5)

    def tearDown(self):
        self.server.terminate()
        self.server.wait()

    def m_send(self, command):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect(('localhost', 5555))
        s.send(command)
        data = s.recv(2048)
        s.close()
        return data

    def test_base_scenario(self):
        task_id = self.m_send(b'ADD 1 5 12345')
        self.assertEqual(b'YES', self.m_send(b'IN 1 ' + task_id))
        self.assertEqual(task_id + b' 5 12345', self.m_send(b'GET 1'))
        self.assertEqual(b'YES', self.m_send(b'IN 1 ' + task_id))
        self.assertEqual(b'YES', self.m_send(b'ACK 1 ' + task_id))
        self.assertEqual(b'NO', self.m_send(b'ACK 1 ' + task_id))
        self.assertEqual(b'NO', self.m_send(b'IN 1 ' + task_id))

    def test_two_tasks(self):
        first_task_id = self.m_send(b'ADD 1 5 12345')
        second_task_id = self.m_send(b'ADD 1 5 12345')
        self.assertEqual(b'YES', self.m_send(b'IN 1 ' + first_task_id))
        self.assertEqual(b'YES', self.m_send(b'IN 1 ' + second_task_id))

        self.assertEqual(first_task_id + b' 5 12345', self.m_send(b'GET 1'))
        self.assertEqual(b'YES', self.m_send(b'IN 1 ' + first_task_id))
        self.assertEqual(b'YES', self.m_send(b'IN 1 ' + second_task_id))
        self.assertEqual(second_task_id + b' 5 12345', self.m_send(b'GET 1'))
        self.assertEqual(b'YES', self.m_send(b'ACK 1 ' + second_task_id))
        self.assertEqual(b'NO', self.m_send(b'ACK 1 ' + second_task_id))

    def _test_files(self):
        # Чтобы запустить этот тест, нужно очистить файл LOGS.txt и закомментировать
        # предыдущие тесты. Проблема в том, что для его проверки нужно отказаться
        # от перезаписывания логов на каждом запуске сервера, но в таком случае
        # падают тесты 1 и 2
        task_id = self.m_send(b'ADD 1 5 12345')
        self.server.terminate()
        self.server.wait()
        self.server = subprocess.Popen(['python3', 'server.py'])
        time.sleep(0.5)
        self.assertEqual(b'YES', self.m_send(b'IN 1 ' + task_id))
        