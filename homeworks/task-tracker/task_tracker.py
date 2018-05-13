import pymysql


class TackTracker:
    STATUS_NEW_TASK = 'New task'
    STATUS_COMPLETED_TASK = 'Completed task'

    def __init__(self, db_name, host, user_name, user_password):
        self._connection = pymysql.connect(host=host,
                                     user=user_name,
                                     password=user_password,
                                     db=db_name,
                                     charset='utf8mb4',
                                     cursorclass=pymysql.cursors.DictCursor)

        self._num_of_users = 0
        self._num_of_tasks = 0
        self._cursor = self._connection.cursor()
        sql_to_save_statuses = "INSERT INTO task_statuses (id, status) VALUES (%s, %s)"
        try:
            self._cursor.executemany(sql_to_save_statuses, [
                                        (0, self.STATUS_NEW_TASK),
                                        (1, self.STATUS_COMPLETED_TASK)
                                        ])
            self._connection.commit()
        except pymysql.err.IntegrityError:  # Если уже записано
            pass

    def add_task(self):
        sql_to_insert_task = f"""
            INSERT INTO tasks (id, parent_id, user_token, task_type)
            VALUES ({self._num_of_tasks}, NULL, NULL, 0)
            """
        self._cursor.execute(sql_to_insert_task)
        self._connection.commit()

        self._num_of_tasks += 1
        return self._num_of_tasks - 1

    def mark_task_completed(self, t_id):
        if t_id >= self._num_of_tasks:
            return f'There are no task with id {t_id}'

        sql_mark_task_completed = f"""
            UPDATE tasks SET task_type=1 WHERE id={t_id} OR parent_id={t_id}
        """
        self._cursor.execute(sql_mark_task_completed)
        self._connection.commit()

    def assign_task_to_user(self, t_id, u_name):
        if t_id >= self._num_of_tasks:
            return f'There are no task with id {t_id}'

        sql_to_create_user = """
            INSERT INTO users (id, login)
            VALUES ({0}, '{1}')
        """.format(self._num_of_users, u_name)
        self._cursor.execute(sql_to_create_user)

        sql_add_user_id_in_tasks = f"""
            UPDATE tasks SET user_token={self._num_of_users} WHERE id={t_id} 
            OR parent_id={t_id}
        """
        self._cursor.execute(sql_add_user_id_in_tasks)
        self._connection.commit()

        self._num_of_users += 1
        return self._num_of_users - 1

    def get_task_status(self, t_id):
        if t_id >= self._num_of_tasks:
            return f'There are no task with id {t_id}'

        sql_to_get_status = f"""
            SELECT task_type FROM tasks WHERE id={t_id}
        """
        self._cursor.execute(sql_to_get_status)
        response = self._cursor.fetchall()

        if response[0]['task_type'] == 1:
            return self.STATUS_COMPLETED_TASK
        else:
            return self.STATUS_NEW_TASK

    def get_tasks_list(self):
        sql_get_tasks_list = """
            SELECT tasks.id, users.login FROM users RIGHT JOIN tasks ON tasks.user_token=users.id;
        """
        self._cursor.execute(sql_get_tasks_list)
        response = self._cursor.fetchall()
        tasks_list = [(table_tuple['id'], table_tuple['login']) for table_tuple in response]
        return tasks_list

    def add_sub_task(self, parent_task, child_task):
        if parent_task >= self._num_of_tasks:
            return f'There are no task with id {parent_task}'
        elif child_task >= self._num_of_tasks:
            return f'There are no task with id {child_task}'

        sql_add_sub_task = f"""
            UPDATE tasks SET parent_id={parent_task} WHERE id={child_task}
        """
        self._cursor.execute(sql_add_sub_task)
        self._connection.commit()

    def _clear_the_base(self):
        sql_to_delete = "DELETE FROM tasks"
        self._cursor.execute(sql_to_delete)
        sql_to_delete = "DELETE FROM users"
        self._cursor.execute(sql_to_delete)
        self._connection.commit()

    def __del__(self):
        self._connection.close()

if __name__ == '__main__':
    t_tracker = TackTracker('testDB', 'localhost', 'test_user', 'password')
    t_tracker._clear_the_base()
    n = t_tracker.add_task()
    t_tracker.mark_task_completed(n)
    t_tracker.assign_task_to_user(0, 'Lion')
    t_tracker.add_task()
    t_tracker.add_task()
    print(t_tracker.get_tasks_list())
    t_tracker.add_sub_task(1, 2)
    t_tracker.mark_task_completed(1)
    t_tracker.assign_task_to_user(1, 'Tiger')