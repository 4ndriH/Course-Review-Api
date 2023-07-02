import sqlite3
import json
import pandas as pd
import time

path = '/usr/games/CRAPI/CourseReview.db'

# -----------------------------------------------------------
# User verification
# -----------------------------------------------------------

def getApiUser(username):
    cnx = sqlite3.connect(path)
    cursor = cnx.execute("SELECT * FROM ApiUsers WHERE Username=? AND Deactivated=0", (username,))
    userList = [dict((cursor.description[i][0], value) for i, value in enumerate(row)) for row in cursor.fetchall()]
    cnx.close()
    if len(userList) == 0:
        return {'Username': '', 'PasswordHash': '', 'Deactivated': 1}
    else:
        return userList[0]


# -----------------------------------------------------------
# Get reviews and ratings of a course
# -----------------------------------------------------------

def getCourseReviews(course_id):
    cnx = sqlite3.connect(path)
    cursor = cnx.execute("SELECT Review, Semester FROM CourseReviews WHERE CourseNumber=? AND VerificationStatus=1 ORDER BY Date DESC", (course_id,))
    data = [dict((cursor.description[i][0], value) for i, value in enumerate(row)) for row in cursor.fetchall()]
    cnx.close()
    return json.dumps((r[0] if data else None) if False else data)


def getCourseRating(CourseNumber):
    cnx = sqlite3.connect(path)
    cursor = cnx.execute("SELECT AVG(Recommended), AVG(Interesting), AVG(Difficulty), AVG(Effort), AVG(Resources), Semester FROM CourseStarRatings WHERE CourseNumber=?", (CourseNumber,))
    data = [dict((cursor.description[i][0], value) for i, value in enumerate(row)) for row in cursor.fetchall()]
    cnx.close()
    return json.dumps((r[0] if data else None) if False else data)


# -----------------------------------------------------------
# Get CourseReview website statistics
# -----------------------------------------------------------

def getLatestReviews():
    cnx = sqlite3.connect(path)
    cursor = cnx.execute("SELECT c.CourseNumber, CourseName FROM (SELECT CourseNumber FROM CourseReviews WHERE VerificationStatus= 1 GROUP BY CourseNumber HAVING MAX(Date) ORDER BY Date DESC limit 10) cn INNER JOIN Courses c ON cn.CourseNumber = c.CourseNumber")
    data = [dict((cursor.description[i][0], value) for i, value in enumerate(row)) for row in cursor.fetchall()]
    cnx.close()
    return json.dumps((r[0] if data else None) if False else data)


def getPublishedReviewStats():
    cnx = sqlite3.connect(path)
    cursor = cnx.execute("SELECT COUNT(DISTINCT CourseNumber) AS percourse, COUNT(*) AS total FROM (SELECT CourseNumber, UniqueUserId FROM CourseReviews WHERE VerificationStatus = 1 UNION SELECT CourseNumber, UniqueUserId FROM CourseStarRatings)")
    data = [dict((cursor.description[i][0], value) for i, value in enumerate(row)) for row in cursor.fetchall()]
    cnx.close()
    return json.dumps((r[0] if data else None) if False else data)


def getAllCoursesWithReviews():
    cnx = sqlite3.connect(path)
    cursor = cnx.execute("SELECT c.CourseNumber, CourseName FROM (SELECT CourseNumber FROM CourseReviews WHERE VerificationStatus= 1 GROUP BY CourseNumber HAVING MAX(Date) ORDER BY Date DESC) cn INNER JOIN Courses c ON cn.CourseNumber = c.CourseNumber")
    data = [dict((cursor.description[i][0], value) for i, value in enumerate(row)) for row in cursor.fetchall()]
    cnx.close()
    return json.dumps((r[0] if data else None) if False else data)


# -----------------------------------------------------------
# Insert reviews or ratings of a course
# -----------------------------------------------------------

def insertReview(course_id, user_id, review):
    cnx = sqlite3.connect(path)
    cursor = cnx.execute("SELECT * FROM CourseReviews WHERE UniqueUserId=? AND CourseNumber=?", (user_id, course_id,))
    if len(cursor.fetchall()) == 0: 
        cursor = cnx.execute("INSERT INTO CourseReviews (UniqueUserId, CourseNumber, VerificationStatus, Date, Review) VALUES (?, ?, 0, ?, ?)", (user_id, course_id, review, int(time.time() * 1000),))
        cnx.commit()
        cnx.close()
        return "inserted"
    else:
        return "You already submitted a review for this course"


def insertRating(course_id, user_id, column, rating):
    cnx = sqlite3.connect(path)
    cursor = cnx.execute("SELECT * FROM CourseReviews WHERE UniqueUserId=? AND CourseNumber=? AND {0} IS NOT NULL".format(column), (user_id, course_id))
    if len(cursor.fetchall()) == 0: 
        cursor = cnx.execute("INSERT INTO CourseReviews (UniqueUserId, CourseNumber, {0}) VALUES (?, ?, ?, )".format(column), (user_id, course_id, rating,))
        cnx.commit()
        cnx.close()
        return "success"
    else:
        return updateRating(course_id, user_id, column, rating)


# -----------------------------------------------------------
# Update reviews, ratings or semester of a course
# -----------------------------------------------------------

def updateReview(course_id, user_id, review):
    cnx = sqlite3.connect(path)
    cursor = cnx.execute("UPDATE CourseReviews SET Review=?, VerificationStatus=0, Date=? WHERE CourseNumber=? AND UniqueUserId=?", (review, course_id, user_id, int(time.time() * 1000),))
    cnx.commit()
    rowsAffected = cursor.rowcount
    cnx.close()
    if rowsAffected < 1:
        return "fail"
    else:
        return "success"


def updateRating(course_id, user_id, column, rating):
    cnx = sqlite3.connect(path)
    cursor = cnx.execute("UPDATE CourseReviews SET {0}=? WHERE CourseNumber=? AND UniqueUserId=?".format(column), (rating, course_id, user_id,))
    cnx.commit()
    rowsAffected = cursor.rowcount
    cnx.close()
    if rowsAffected < 1:
        return "fail"
    else:
        return "success"
    

def updateSemester(course_id, user_id, semester):
    cnx = sqlite3.connect(path)
    cursor = cnx.execute("UPDATE CourseReviews SET Semester=?, WHERE CourseNumber=? AND UniqueUserId=?", (semester, course_id, user_id,))
    cnx.commit()
    rowsAffected = cursor.rowcount
    cnx.close()
    if rowsAffected < 1:
        return "fail"
    else:
        return "success"

# -----------------------------------------------------------
# Remove reviews or ratings of a course
# -----------------------------------------------------------

def removeCourseReview(course_id, user_id):
    cnx = sqlite3.connect(path)
    cursor = cnx.execute("UPDATE CourseReviews SET Review=NULL WHERE CourseNumber=? AND UniqueUserId=?", ("", course_id, user_id,))
    cnx.commit()
    rowsAffected = cursor.rowcount
    cnx.close()
    if rowsAffected < 1:
        return "fail"
    else:
        return "success"
    

def removeCourseRating(course_id, user_id, column):
    cnx = sqlite3.connect(path)
    cursor = cnx.execute("UPDATE CourseReviews SET {0}=NULL WHERE CourseNumber=? AND UniqueUserId=?".format(column), (course_id, user_id,))
    cnx.commit()
    rowsAffected = cursor.rowcount
    cnx.close()
    if rowsAffected < 1:
        return "fail"
    else:
        return "success"


# -----------------------------------------------------------
# Reviews and rating submitted by user
# -----------------------------------------------------------

def getReviewsFromUser(user_id):
    cnx = sqlite3.connect(path)
    cursor = cnx.execute("SELECT CourseNumber, Review, VerificationStatus, Semester FROM CourseReviews WHERE UniqueUserId=? ORDER BY Date DESC", (user_id,))
    result = cursor.fetchall()
    cnx.close()
    return result


def getStarRatingsFromUser(user_id):
    cnx = sqlite3.connect(path)
    cursor = cnx.execute("SELECT CourseNumber, Recommended, Interesting, Difficulty, Effort, Resources, Semester FROM CourseReviews WHERE UniqueUserId=?", (user_id,))
    result = cursor.fetchall()
    cnx.close()
    return result
