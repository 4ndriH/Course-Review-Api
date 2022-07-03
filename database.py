import sqlite3
import json
import pandas as pd
import time

path = ''

def getApiUser(username):
    temp_dict = {}
    cnx = sqlite3.connect(path)
    cursor = cnx.execute("SELECT * FROM ApiUsers WHERE Username=? AND Deactivated=0", ('luggas',))
    userList = [dict((cursor.description[i][0], value) for i, value in enumerate(row)) for row in cursor.fetchall()]
    cnx.close()
    if len(userList) == 0:
        return {'Username': '', 'PasswordHash': '', 'Deactivated': 1}
    else:
        return userList[0]


def getCourseReviews(CourseNumber):
    cnx = sqlite3.connect(path)
    cursor = cnx.execute("SELECT Review FROM CourseReviews WHERE CourseNumber=? AND Verified=1 ORDER BY Date DESC", (CourseNumber,))
    data = [dict((cursor.description[i][0], value) for i, value in enumerate(row)) for row in cursor.fetchall()]
    cnx.close()
    return json.dumps((r[0] if data else None) if False else data)

def getLatestReviews():
    cnx = sqlite3.connect(path)
    cursor = cnx.execute("SELECT DISTINCT CourseNumber FROM CourseReviews WHERE Verified=1 ORDER BY Date DESC limit 10")
    data = [dict((cursor.description[i][0], value) for i, value in enumerate(row)) for row in cursor.fetchall()]
    cnx.close()
    return json.dumps((r[0] if data else None) if False else data)

    
def getStatsReviews():
    cnx = sqlite3.connect(path)
    cursor = cnx.execute("SELECT COUNT(DISTINCT CourseNumber), COUNT(*) FROM CourseReviews WHERE Verified=1")
    data = [dict((cursor.description[i][0], value) for i, value in enumerate(row)) for row in cursor.fetchall()]
    cnx.close()
    return json.dumps((r[0] if data else None) if False else data)


def removeCourseReviews(CourseNumber, nethz):
    cnx = sqlite3.connect(path)
    cursor = cnx.execute("DELETE FROM CourseReviews WHERE CourseNumber=? AND nethz=?", (CourseNumber, nethz,))
    cnx.commit()
    rowsAffected = cursor.rowcount
    cnx.close()
    if rowsAffected < 1:
        return "fail"
    else:
        return "success"


def getReviewsFromUser(nethz):
    cnx = sqlite3.connect(path)
    cursor = cnx.execute("SELECT Review, CourseNumber, Verified FROM CourseReviews WHERE nethz=? ORDER BY Date DESC", (nethz,))
    result = cursor.fetchall()
    cnx.close()
    return result


def insertReview(course_id, nethz, review):
    cnx = sqlite3.connect(path)
    cursor = cnx.execute("SELECT * FROM CourseReviews WHERE nethz=? AND CourseNumber=?", (nethz, course_id,))
    if len(cursor.fetchall()) == 0: 
        cursor = cnx.execute("INSERT INTO CourseReviews (nethz, CourseNumber, Review, Date) VALUES (?, ?, ?, ?)", (nethz, course_id, review, int(time.time() * 1000),))
        cnx.commit()
        cnx.close()
        return "inserted"
    else:
        return "User already submitted a review for this course"


def updateReview(course_id, nethz, review):
    cnx = sqlite3.connect(path)
    cursor = cnx.execute("UPDATE CourseReviews SET Review=?, Verified=0 WHERE CourseNumber=? AND nethz=?", (review, course_id, nethz,))
    cnx.commit()
    rowsAffected = cursor.rowcount
    cnx.close()
    if rowsAffected < 1:
        return "fail"
    else:
        return "success"
