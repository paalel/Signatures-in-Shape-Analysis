#!/usr/bin/python
from .db_helpers import set_up
import os, sys

def check_animation_id(id1, id2):
    connection, cursor = set_up()
    if id1 is None or id2 is None:
        raise("No animation id given in check_animation_id")

    cursor.execute("""
            SELECT count(*) FROM similarity
            WHERE (animation_id1 = ? AND animation_id2 = ?);
        """, (id1, id2))

    return int(cursor.fetchone()[0]) > 0

def insert_similarity(animation_id1, animation_id2, distance, dp_distance, size1, size2):
    connection, cursor = set_up()
    if check_animation_id(animation_id1, animation_id2):
        cursor.execute("""
            UPDATE similarity
            SET dp_distance=?
            WHERE
            animation_id1=? and animation_id2=?;
            """, (dp_distance, animation_id1, animation_id2)
        )
    else:
        cursor.execute("""
            INSERT INTO
            similarity(animation_id1, animation_id2,
            distance, dp_distance, size1, size2)
            VALUES (?, ?, ?, ?, ?, ?);
            """, (animation_id1, animation_id2, distance, dp_distance, size1, size2)
        )

    connection.commit()
    cursor.execute("SELECT count(*) FROM similarity;")
    return int(cursor.fetchone()[0])


def insert_signature_distance(animation_id1, animation_id2, signature_distance):
    connection, cursor = set_up()
    cursor.execute("""
        UPDATE similarity
        SET signature_distance=?
        WHERE
        animation_id1=? and animation_id2=?;
        """, (signature_distance, animation_id1, animation_id2)
    )
    connection.commit()
    cursor.execute("SELECT count(*) FROM similarity;")
    return int(cursor.fetchone()[0])
