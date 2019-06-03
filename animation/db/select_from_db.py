#!/usr/bin/python
from .db_helpers import set_up
import os, sys

def get_subject(description = None, file_name = None, animation_file_name = None):
    connection, cursor = set_up()

    if file_name:
        cursor.execute("""
                SELECT file_name, file_path, description FROM subject WHERE
                file_name = ?;
            """, (file_name,))

        return cursor.fetchone()
    
    if animation_file_name:
        cursor.execute("""
                SELECT s.file_name, s.file_path, s.description FROM subject AS s
                INNER JOIN animation AS a ON s.subject_id = a.subject_id
                WHERE a.file_name = ?;
            """, (animation_file_name,))
        return cursor.fetchone()

    if description:
        cursor.execute("""
                SELECT file_name, file_path, description FROM subject WHERE
                WHERE LOWER(description) LIKE LOWER(?);
            """, ("%"+description+"%",))

        return cursor.fetchall()

    print("No query paramters given.")
    return None


def get_animation(animation_id = None, file_name = None, description = None, 
        subject_file_name = None, subject_fkey = None):
    connection, cursor = set_up()
    if animation_id:
        cursor.execute("""
                SELECT file_name, file_path, description FROM animation WHERE
                animation_id = ?;
            """, (animation_id,))
        return cursor.fetchone()

    if file_name:
        cursor.execute("""
                SELECT file_name, file_path, description FROM animation WHERE
                file_name = ?;
            """, (file_name,))
        return cursor.fetchone()

    if subject_file_name:
        cursor.execute("""
                SELECT a.file_name, a.file_path, a.description FROM animation
                a inner join subject s on a.subject_id = s.subject_id WHERE
                s.file_name = ?;
            """, (subject_file_name,))
        return cursor.fetchall()

    if description:
        cursor.execute("""
                SELECT file_name, file_path, description FROM animation 
                WHERE LOWER(description) LIKE LOWER(?);
            """, ("%"+description+"%",))
        return cursor.fetchall()

    if subject_fkey:
        cursor.execute("""
                SELECT animation_id FROM animation where subject_id = ?;
            """, (subject_fkey,))
        return cursor.fetchall()
    
    print("No query paramters given.")
    return None

def get_animation_id_set(description = None, subject_fkey = None, count = None):
    connection, cursor = set_up()
    if description:
        cursor.execute("""
                SELECT animation_id FROM animation 
                WHERE LOWER(description) LIKE LOWER(?);
            """, ("%"+description+"%",))

    elif subject_fkey:
        cursor.execute("""
                SELECT animation_id FROM animation
                where subject_id = ?;
            """, (subject_fkey,))
    else:
        cursor.execute("SELECT animation_id FROM animation;")

    if count:
        return cursor.fetchmany(count)
    return cursor.fetchall()
