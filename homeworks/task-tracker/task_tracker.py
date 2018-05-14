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

        self._cursor = self._connection.cursor()
        sql_to_save_statuses = "INSERT INTO task_statuses (id, status) VALUES (%s, %s)"
        try:
            self._cursor.executemany(sql_to_save_statuses, [
                                        (1, self.STATUS_NEW_TASK),
                                        (2, self.STATUS_COMPLETED_TASK)
                                        ])
            self._connection.commit()
        except pymysql.err.IntegrityError:  # Если уже записано
            pass

    def add_task(self):
        sql_to_insert_task = f"""
            INSERT INTO tasks (parent_id, user_token, task_type)
            VALUES (Null, Null, 1)
            """
        self._cursor.execute(sql_to_insert_task)
        self._connection.commit()

    def mark_task_completed(self, t_id):
        sql_mark_task_completed = f"""
            UPDATE tasks SET task_type=2 WHERE id={t_id}
        """
        self._cursor.execute(sql_mark_task_completed)

        sql_get_sub_task = f"""
            SELECT id FROM tasks WHERE parent_id={t_id}
        """
        self._cursor.execute(sql_get_sub_task)
        sub_task_id = self._cursor.fetchall()
        if sub_task_id:
            self.mark_task_completed(sub_task_id[0]['id'])

        self._connection.commit()

    def assign_task_to_user(self, t_id, u_name):
        sql_add_user_id_in_tasks = f"""
            UPDATE tasks SET user_token=(SELECT id FROM users WHERE login='{u_name}') 
            WHERE id={t_id}
        """
        self._cursor.execute(sql_add_user_id_in_tasks)

        sql_get_sub_task = f"""
                    SELECT id FROM tasks WHERE parent_id={t_id}
                """
        self._cursor.execute(sql_get_sub_task)
        sub_task_id = self._cursor.fetchall()
        if sub_task_id:
            self.assign_task_to_user(sub_task_id[0]['id'], u_name)

        self._connection.commit()

    def get_task_status(self, t_id):
        sql_to_get_status = f"""
            SELECT status FROM task_statuses 
            WHERE id=(SELECT task_type FROM tasks WHERE id={t_id})
        """
        self._cursor.execute(sql_to_get_status)
        response = self._cursor.fetchall()
        print(response)
        return response

    def get_tasks_list(self):
        sql_get_tasks_list = """
            SELECT tasks.id, users.login FROM users RIGHT JOIN tasks ON tasks.user_token=users.id;
        """
        self._cursor.execute(sql_get_tasks_list)
        response = self._cursor.fetchall()
        tasks_list = [(table_tuple['id'], table_tuple['login']) for table_tuple in response]
        return tasks_list

    def add_sub_task(self, parent_task, child_task):
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
        sql_to_delete = "ALTER TABLE tasks AUTO_INCREMENT=0"
        self._cursor.execute(sql_to_delete)
        self._connection.commit()

    def create_user(self, u_name):
        sql_to_create_user = f"""
            INSERT INTO users (login)
            VALUES ('{u_name}')
        """
        self._cursor.execute(sql_to_create_user)
        self._connection.commit()

    def __del__(self):
        self._connection.close()

if __name__ == '__main__':
    t_tracker = TackTracker('testDB', 'localhost', 'test_user', 'password')
    t_tracker._clear_the_base()
    t_tracker.add_task()
    t_tracker.add_task()
    t_tracker.add_task()
    t_tracker.add_task()
    t_tracker.add_sub_task(1, 2)
    t_tracker.add_sub_task(2, 3)
    t_tracker.add_sub_task(3, 4)
    t_tracker.mark_task_completed(1)
    t_tracker.create_user('Lion')
    t_tracker.assign_task_to_user(1, 'Lion')
    print(t_tracker.get_tasks_list())

