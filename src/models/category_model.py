# category_model.py
# Model: only talks to the database

from src.models.db_connection import get_db_connection


def get_connection():
    # get_db_connection() returns None when it cannot connect,
    # so raise an error here and let the controller show the message
    conn = get_db_connection()
    if conn is None:
        raise Exception("Cannot connect to the database.")
    return conn

# sort options (fixed list so the user cannot put SQL in ORDER BY)
SORT_OPTIONS = {
    "name_asc": "c.full_name ASC, c.contact_id ASC",
    "name_desc": "c.full_name DESC, c.contact_id DESC",
    "newest": "c.created_at DESC, c.contact_id DESC",
    "oldest": "c.created_at ASC, c.contact_id ASC",
}


def get_groups(user_id):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(
        "SELECT group_id, group_name FROM contact_groups "
        "WHERE user_id = %s ORDER BY group_name",
        (user_id,),
    )
    groups = cursor.fetchall()
    cursor.close()
    conn.close()
    return groups


def group_name_exists(user_id, name, exclude_id=0):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT group_id FROM contact_groups "
        "WHERE user_id = %s AND group_name = %s AND group_id <> %s",
        (user_id, name, exclude_id),
    )
    found = cursor.fetchone() is not None
    cursor.close()
    conn.close()
    return found


def create_group(user_id, name):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO contact_groups (user_id, group_name) VALUES (%s, %s)",
            (user_id, name),
        )
        conn.commit()
        return cursor.lastrowid
    except Exception:
        conn.rollback()
        raise
    finally:
        cursor.close()
        conn.close()


def rename_group(user_id, group_id, new_name):
    # returns 0 if the group is not found
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "UPDATE contact_groups SET group_name = %s "
            "WHERE group_id = %s AND user_id = %s",
            (new_name, group_id, user_id),
        )
        count = cursor.rowcount
        if count == 0:
            # rowcount can be 0 when the name is not changed, so check again
            cursor.execute(
                "SELECT group_id FROM contact_groups WHERE group_id = %s AND user_id = %s",
                (group_id, user_id),
            )
            if cursor.fetchone() is not None:
                count = 1
        conn.commit()
        return count
    except Exception:
        conn.rollback()
        raise
    finally:
        cursor.close()
        conn.close()


def delete_group(user_id, group_id):
    # the links in contact_group_members are deleted by ON DELETE CASCADE
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "DELETE FROM contact_groups WHERE group_id = %s AND user_id = %s",
            (group_id, user_id),
        )
        conn.commit()
        return cursor.rowcount
    except Exception:
        conn.rollback()
        raise
    finally:
        cursor.close()
        conn.close()


def get_groups_of_contact(user_id, contact_id):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(
        "SELECT g.group_id, g.group_name "
        "FROM contact_group_members m "
        "JOIN contact_groups g ON g.group_id = m.group_id "
        "JOIN contacts c ON c.contact_id = m.contact_id "
        "WHERE m.contact_id = %s AND g.user_id = %s AND c.user_id = %s "
        "ORDER BY g.group_name",
        (contact_id, user_id, user_id),
    )
    groups = cursor.fetchall()
    cursor.close()
    conn.close()
    return groups


def assign_contact_to_groups(user_id, contact_id, group_ids):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        # the contact must belong to this user
        cursor.execute(
            "SELECT contact_id FROM contacts WHERE contact_id = %s AND user_id = %s",
            (contact_id, user_id),
        )
        if cursor.fetchone() is None:
            raise ValueError("Contact not found.")

        for group_id in group_ids:
            # the group must belong to this user too
            cursor.execute(
                "SELECT group_id FROM contact_groups WHERE group_id = %s AND user_id = %s",
                (group_id, user_id),
            )
            if cursor.fetchone() is None:
                raise ValueError("Group not found.")
            # INSERT IGNORE: if the contact is already in the group, skip it
            cursor.execute(
                "INSERT IGNORE INTO contact_group_members (contact_id, group_id) "
                "VALUES (%s, %s)",
                (contact_id, group_id),
            )
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        cursor.close()
        conn.close()


def remove_contact_from_group(user_id, contact_id, group_id):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "DELETE m FROM contact_group_members m "
            "JOIN contacts c ON c.contact_id = m.contact_id "
            "JOIN contact_groups g ON g.group_id = m.group_id "
            "WHERE m.contact_id = %s AND m.group_id = %s "
            "AND c.user_id = %s AND g.user_id = %s",
            (contact_id, group_id, user_id, user_id),
        )
        conn.commit()
        return cursor.rowcount
    except Exception:
        conn.rollback()
        raise
    finally:
        cursor.close()
        conn.close()


def search_contacts(user_id, keyword="", group_id=None, sort_key="name_asc",
                    limit=20, offset=0):
    order_by = SORT_OPTIONS.get(sort_key, SORT_OPTIONS["name_asc"])
    params = []

    sql = (
        "SELECT c.contact_id, c.full_name, c.phone_number, c.email, "
        "(SELECT GROUP_CONCAT(g.group_name ORDER BY g.group_name SEPARATOR ', ') "
        " FROM contact_group_members m2 "
        " JOIN contact_groups g ON g.group_id = m2.group_id "
        " WHERE m2.contact_id = c.contact_id) AS group_names "
        "FROM contacts c "
    )
    if group_id is not None:
        sql += "JOIN contact_group_members m ON m.contact_id = c.contact_id AND m.group_id = %s "
        params.append(group_id)

    sql += "WHERE c.user_id = %s "
    params.append(user_id)

    keyword = (keyword or "").strip()
    if keyword != "":
        # escape \ % _ so they are searched as normal characters
        keyword = keyword.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")
        like = "%" + keyword + "%"
        sql += "AND (c.full_name LIKE %s OR c.phone_number LIKE %s) "
        params.append(like)
        params.append(like)

    sql += "ORDER BY " + order_by + " LIMIT %s OFFSET %s"
    params.append(limit)
    params.append(offset)

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(sql, tuple(params))
    contacts = cursor.fetchall()
    cursor.close()
    conn.close()
    return contacts
