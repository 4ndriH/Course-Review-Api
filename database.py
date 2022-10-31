import sqlite3
import json
import pandas as pd
import time

path = '/usr/games/RubberDucky/DB/RubberDucky.db'

def getApiUser(username):
    cnx = sqlite3.connect(path)
    cursor = cnx.execute("SELECT * FROM ApiUsers WHERE Username=? AND Deactivated=0", (username,))
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

def getRatingReviews(CourseNumber):
    cnx = sqlite3.connect(path)
    cursor = cnx.execute("SELECT SUM(S1)/SUM(CASE WHEN S1 = 0 THEN 0 ELSE 1) as one, SUM(S2)/SUM(CASE WHEN S2 = 0 THEN 0 ELSE 1) as two, SUM(S3)/SUM(CASE WHEN S3 = 0 THEN 0 ELSE 1) as three, SUM(S4)/SUM(CASE WHEN S4 = 0 THEN 0 ELSE 1) as four, SUM(S5)/SUM(CASE WHEN S5 = 0 THEN 0 ELSE 1) as five, ((one + two + three + four + five) / (CASE WHEN one = 0 THEN 0 ELSE 1 + CASE WHEN two = 0 THEN 0 ELSE 1 + CASE WHEN three = 0 THEN 0 ELSE 1 + CASE WHEN four = 0 THEN 0 ELSE 1 + CASE WHEN five = 0 THEN 0 ELSE 1)) FROM CourseReviews WHERE CourseNumber=? AND Verified=1 ORDER BY Date DESC", (CourseNumber,))
    data = [dict((cursor.description[i][0], value) for i, value in enumerate(row)) for row in cursor.fetchall()]
    cnx.close()
    return json.dumps((r[0] if data else None) if False else data)

def getLatestReviews():
    cnx = sqlite3.connect(path)
    cursor = cnx.execute("SELECT CourseNumber FROM CourseReviews WHERE Verified= 1 GROUP BY CourseNumber HAVING MAX(Date) ORDER BY Date DESC limit 10")
    data = [dict((cursor.description[i][0], value) for i, value in enumerate(row)) for row in cursor.fetchall()]
    cnx.close()
    return json.dumps((r[0] if data else None) if False else data)

def getAllReviews():
    cnx = sqlite3.connect(path)
    cursor = cnx.execute("SELECT CourseNumber FROM CourseReviews WHERE Verified= 1 GROUP BY CourseNumber HAVING MAX(Date) ORDER BY Date")
    data = [dict((cursor.description[i][0], value) for i, value in enumerate(row)) for row in cursor.fetchall()]
    cnx.close()
    return json.dumps((r[0] if data else None) if False else data)

def getStatsReviews():
    cnx = sqlite3.connect(path)
    cursor = cnx.execute("SELECT COUNT(DISTINCT CourseNumber) AS percourse, COUNT(*) AS total FROM CourseReviews WHERE Verified=1")
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


def insertReview(course_id, nethz, review, s1, s2, s3, s4, s5):
    cnx = sqlite3.connect(path)
    cursor = cnx.execute("SELECT * FROM CourseReviews WHERE nethz=? AND CourseNumber=?", (nethz, course_id,))
    if len(cursor.fetchall()) == 0: 
        cursor = cnx.execute("INSERT INTO CourseReviews (nethz, CourseNumber, Review, Star1, Star2, Star3, Star4, Star5 Date) VALUES (?, ?, ?, ?, ?, ?, ?, ?)", (nethz, course_id, review, s1, s2, s3, s4, s5, int(time.time() * 1000),))
        cnx.commit()
        cnx.close()
        return "inserted"
    else:
        return "User already submitted a review for this course"


def updateReview(course_id, nethz, review, s1, s2, s3, s4, s5):
    cnx = sqlite3.connect(path)
    cursor = cnx.execute("UPDATE CourseReviews SET Review=?, Star1=?, Star2=?, Star3=?, Star4=?, Star5=?, Verified=0 WHERE CourseNumber=? AND nethz=?", (review, course_id, nethz, s1, s2, s3, s4, s5,))
    cnx.commit()
    rowsAffected = cursor.rowcount
    cnx.close()
    if rowsAffected < 1:
        return "fail"
    else:
        return "success"
