import mysql.connector
from mysql.connector import Error
from mysql.connector import pooling

def create_connection_pool(pool_name, pool_size, host_name, user_name, user_password, db_name):
    pool = None
    try:
        pool = mysql.connector.pooling.MySQLConnectionPool(
            pool_name = pool_name,
            pool_size = pool_size,
            host = host_name,
            user = user_name,
            password = user_password,
            database = db_name
        )
        print("Connection pool created successfully")
    except Error as err:
        print(f"Error: '{err}'")
    return pool


def get_connection(pool):
    try:
        return pool.get_connection()
    except Error as err:
        print(f"Error getting connection: '{err}'")
        return None


def execute_query(pool, query, params):
    connection = get_connection(pool)
    if connection:
        try:
            cursor = connection.cursor()
            cursor.execute(query, params)
            connection.commit()
        except Error as err:
            print(f"Error: '{err}'")
        finally:
            cursor.close()
            connection.close()


def create_username(pool, user_id, username, current_group_id=None):
    connection = get_connection(pool)
    if connection:
        try:
            cursor = connection.cursor()
            query = "INSERT INTO users (user_id, username, current_group_id) VALUES (%s, %s, %s)"
            cursor.execute(query, (user_id, username, current_group_id))
            connection.commit()
            print(f"Username '{username}' created.")
        except Error as err:
            print(f"Error: '{err}'")
        finally:
            cursor.close()
            connection.close()


def update_current_group(pool, user_id, new_group_id):
    connection = get_connection(pool)
    if connection:
        try:
            cursor = connection.cursor()
            query = "UPDATE users SET current_group_id = %s WHERE user_id = %s"
            cursor.execute(query, (new_group_id, user_id))
            connection.commit()
            print(f"User {user_id}'s current group updated to {new_group_id}.")
        except Error as err:
            print(f"Error: '{err}'")
        finally:
            cursor.close()
            connection.close()



def get_username(pool, user_id):
    connection = get_connection(pool)
    if connection:
        try:
            cursor = connection.cursor()
            query = "SELECT username FROM users WHERE user_id = %s"
            cursor.execute(query, (user_id,))
            result = cursor.fetchone()  # fetchone() returns a single record or None
            return result[0] if result else None
        except Error as err:
            print(f"Error: '{err}'")
            return None
        finally:
            cursor.close()
            connection.close()




def delete_user(pool, user_id):
    connection = get_connection(pool)
    if connection:
        try:
            cursor = connection.cursor()
            query = "DELETE FROM users WHERE id = %s"
            cursor.execute(query, (user_id,))
            connection.commit()
            print(f"User with id {user_id} deleted.")
        except Error as err:
            print(f"Error: '{err}'")
        finally:
            cursor.close()
            connection.close()


def create_group_name(pool, groupname):
    connection = get_connection(pool)
    if connection:
        try:
            cursor = connection.cursor()
            query = "INSERT INTO split_groups (groupname) VALUES (%s)"
            cursor.execute(query, (groupname,))
            connection.commit()
            group_id = cursor.lastrowid
            print(f"Group '{groupname}' created.")
            return group_id
        except Error as err:
            print(f"Error: '{err}'")
            return None
        finally:
            cursor.close()
            connection.close()


def add_user_to_group(pool, user_id, group_id):
    connection = get_connection(pool)
    if connection:
        try:
            cursor = connection.cursor()
            query = "INSERT INTO user_groups (user_id, group_id) VALUES (%s, %s)"
            cursor.execute(query, (user_id, group_id))
            connection.commit()
            print(f"User {user_id} added to group {group_id}.")
        except Error as err:
            print(f"Error: '{err}'")
        finally:
            cursor.close()
            connection.close()


def delete_group(pool, group_id):
    connection = get_connection(pool)
    if connection:
        try:
            cursor = connection.cursor()
            query = "DELETE FROM split_groups WHERE id = %s"
            cursor.execute(query, (group_id,))
            connection.commit()
            print(f"Group with id {group_id} deleted.")
        except Error as err:
            print(f"Error: '{err}'")
        finally:
            cursor.close()
            connection.close()



def add_transaction(pool, title, amount, created_by, created_to, group_id):
    connection = get_connection(pool)
    if connection:
        try:
            cursor = connection.cursor()
            query = "INSERT INTO transactions (title, amount, created_by, created_to, group_id, created_at) VALUES (%s, %s, %s, %s, %s, NOW())"
            cursor.execute(query, (title, amount, created_by, created_to, group_id))
            connection.commit()
            transaction_id = cursor.lastrowid
            print(f"Transaction '{title}' added.")
            return transaction_id
        except Error as err:
            print(f"Error: '{err}'")
            return None
        finally:
            cursor.close()
            connection.close()


def delete_transaction(pool, transaction_id):
    connection = get_connection(pool)
    if connection:
        try:
            cursor = connection.cursor()
            query = "DELETE FROM transactions WHERE id = %s"
            cursor.execute(query, (transaction_id,))
            connection.commit()
            return f"Transaction with id {transaction_id} deleted."
        except Error as err:
            print(f"Error: '{err}'")
            return None
        finally:
            cursor.close()
            connection.close()




def get_all_transactions_for_user(pool, user_id, group_id):
    connection = get_connection(pool)
    if connection:
        try:
            cursor = connection.cursor()
            query = """
            SELECT t.id, t.title, t.amount, u1.username AS created_by_username, u2.username AS created_to_username FROM transactions t
            JOIN users u1 ON t.created_by = u1.user_id
            LEFT JOIN users u2 ON t.created_to = u2.user_id
            WHERE (t.created_by = %s OR t.created_to = %s) AND t.group_id = %s
            ORDER BY t.created_at ASC
            """
            cursor.execute(query, (user_id, user_id, group_id,))
            result = cursor.fetchall()
            return result
        except Error as err:
            print(f"Error: '{err}'")
            return None
        finally:
            cursor.close()
            connection.close()

def get_all_transactions_in_group(pool,group_id):
    connection = get_connection(pool)
    if connection:
        try:
            cursor = connection.cursor()
            query = """
            SELECT t.*, u1.username AS created_by_username, u2.username AS created_to_username FROM transactions t
            JOIN users u1 ON t.created_by = u1.user_id
            LEFT JOIN users u2 ON t.created_to = u2.user_id
            WHERE t.group_id = %s
            """
            cursor.execute(query, (group_id,))
            result = cursor.fetchall()
            return result
        except Error as err:
            print(f"Error: '{err}'")
            return None
        finally:
            cursor.close()
            connection.close()



def get_group_id(pool, group_name):
    connection = get_connection(pool)
    if connection:
        try:
            cursor = connection.cursor()
            query = "SELECT * FROM split_groups WHERE groupname = %s"
            cursor.execute(query, (group_name,))
            result = cursor.fetchall()
            return result
        except Error as err:
            print(f"Error: '{err}'")
            return None
        finally:
            cursor.close()
            connection.close()


def get_current_group_name(pool, user_id):
    connection = get_connection(pool)
    if connection:
        try:
            cursor = connection.cursor()
            query = """
            SELECT sg.groupname
            FROM users u
            JOIN split_groups sg ON u.current_group_id = sg.id
            WHERE u.user_id = %s
            """
            cursor.execute(query, (user_id,))
            result = cursor.fetchone()
            return result[0] if result else None
        except Error as err:
            print(f"Error: '{err}'")
            return None
        finally:
            cursor.close()
            connection.close()



def get_user_current_group_id(pool, user_id):
    connection = get_connection(pool)
    if connection:
        try:
            cursor = connection.cursor()
            query = "SELECT users.current_group_id FROM users WHERE user_id= %s"
            cursor.execute(query, (user_id,))
            result = cursor.fetchall()
            return result[0][0] if result else None
        except Error as err:
            print(f"Error: '{err}'")
            return None
        finally:
            cursor.close()
            connection.close()

def get_users_groups(pool, user_id):
    connection = get_connection(pool)
    if connection:
        try:
            cursor = connection.cursor()
            query = "SELECT split_groups.* FROM split_groups JOIN user_groups ON user_groups.group_id = split_groups.id WHERE user_groups.user_id = %s"
            cursor.execute(query, (user_id,))
            result = cursor.fetchall()
            return result
        except Error as err:
            print(f"Error: '{err}'")
            return None
        finally:
            cursor.close()
            connection.close()


def get_users_in_group(pool, group_id):
    connection = get_connection(pool)
    if connection:
        try:
            cursor = connection.cursor()
            query = "SELECT users.* FROM users JOIN user_groups ON user_groups.user_id = users.id WHERE user_groups.group_id = %s"
            cursor.execute(query, (group_id,))
            result = cursor.fetchall()
            return result
        except Error as err:
            print(f"Error: '{err}'")
            return None
        finally:
            cursor.close()
            connection.close()


def get_groupmates(pool, user_id):
    connection = get_connection(pool)
    if connection:
        try:
            cursor = connection.cursor()
            query = """
            SELECT u.username
            FROM users u
            JOIN user_groups ug ON u.user_id = ug.user_id
            WHERE ug.group_id = (
                SELECT current_group_id
                FROM users
                WHERE user_id = %s
            ) AND u.user_id != %s;
            """
            cursor.execute(query, (user_id, user_id))
            result = cursor.fetchall()
            groupmates = [username[0] for username in result]
            return groupmates
        except Error as err:
            print(f"Error: '{err}'")
            return None
        finally:
            cursor.close()
            connection.close()



def get_user_id(pool, username):
    connection = get_connection(pool)
    if connection:
        try:
            cursor = connection.cursor()
            query = "SELECT users.user_id FROM users WHERE users.username = %s"
            cursor.execute(query, (username,))
            result = cursor.fetchall()
            return result[0][0] if result else None
        except Error as err:
            print(f"Error: '{err}'")
            return None
        finally:
            cursor.close()
            connection.close()
