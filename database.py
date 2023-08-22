import sqlite3
import json
import pandas as pd
import time

paths = ['/usr/games/CRAPI/CourseReview.db', '/usr/games/CRAPI/CourseReview_test.db']

# -----------------------------------------------------------
# User verification
# -----------------------------------------------------------

def getApiUser(username):
    cnx = sqlite3.connect(paths[0])
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

def getCourseReviews(course_id, rdd_bool):
    cnx = sqlite3.connect(paths[int(rdd_bool)])
    cursor = cnx.execute("SELECT Review, Semester FROM CourseReviews WHERE CourseNumber=? AND VerificationStatus=1 ORDER BY Date DESC", (course_id,))
    data = [dict((cursor.description[i][0], value) for i, value in enumerate(row)) for row in cursor.fetchall()]
    cnx.close()
    return json.dumps((r[0] if data else None) if False else data)


def getCourseRating(CourseNumber, rdd_bool):
    cnx = sqlite3.connect(paths[int(rdd_bool)])
    cursor = cnx.execute("SELECT AVG(Recommended), AVG(Interesting), AVG(Difficulty), AVG(Effort), AVG(Resources) FROM CourseReviews WHERE CourseNumber=?", (CourseNumber,))
    data = [dict((cursor.description[i][0], value) for i, value in enumerate(row)) for row in cursor.fetchall()]
    cnx.close()
    return json.dumps((r[0] if data else None) if False else data)


# -----------------------------------------------------------
# Get CourseReview website statistics
# -----------------------------------------------------------

def getLatestReviews(rdd_bool):
    cnx = sqlite3.connect(paths[int(rdd_bool)])
    cursor = cnx.execute("SELECT c.CourseNumber, CourseName FROM (SELECT CourseNumber FROM CourseReviews WHERE VerificationStatus= 1 GROUP BY CourseNumber HAVING MAX(Date) ORDER BY Date DESC limit 10) cn INNER JOIN Courses c ON cn.CourseNumber = c.CourseNumber")
    data = [dict((cursor.description[i][0], value) for i, value in enumerate(row)) for row in cursor.fetchall()]
    cnx.close()
    return json.dumps((r[0] if data else None) if False else data)


def getPublishedReviewStats(rdd_bool):
    cnx = sqlite3.connect(paths[int(rdd_bool)])
    cursor = cnx.execute("SELECT COUNT(DISTINCT CourseNumber) AS percourse, COUNT(*) AS total FROM (SELECT * FROM CourseReviews WHERE (Review IS NOT NULL AND VerificationStatus=1 OR Recommended IS NOT NULL))")
    data = [dict((cursor.description[i][0], value) for i, value in enumerate(row)) for row in cursor.fetchall()]
    cnx.close()
    return json.dumps((r[0] if data else None) if False else data)


def getAllCoursesWithReviews(rdd_bool):
    cnx = sqlite3.connect(paths[int(rdd_bool)])
    cursor = cnx.execute("SELECT c.CourseNumber, CourseName FROM (SELECT CourseNumber FROM CourseReviews WHERE VerificationStatus= 1 GROUP BY CourseNumber ORDER BY Date DESC) cn INNER JOIN Courses c ON cn.CourseNumber = c.CourseNumber")
    data = [dict((cursor.description[i][0], value) for i, value in enumerate(row)) for row in cursor.fetchall()]
    cnx.close()
    return json.dumps((r[0] if data else None) if False else data)


# -----------------------------------------------------------
# Insert reviews or ratings of a course
# -----------------------------------------------------------

def insertReview(course_id, user_id, review, rdd_bool):
    cnx = sqlite3.connect(paths[int(rdd_bool)])
    cursor = cnx.execute("SELECT * FROM CourseReviews WHERE UniqueUserId=? AND CourseNumber=?", (user_id, course_id,))
    if len(cursor.fetchall()) == 0: 
        cursor = cnx.execute("INSERT INTO CourseReviews (UniqueUserId, CourseNumber, VerificationStatus, Date, Review) VALUES (?, ?, ?, ?, ?)", (user_id, course_id, int(rdd_bool),int(time.time() * 1000), review,))
        cnx.commit()
        cnx.close()
        return "inserted"
    else:
        cnx.close()
        return updateReview(course_id, user_id, review, rdd_bool)


def insertRating(course_id, user_id, column, rating, rdd_bool):
    cnx = sqlite3.connect(paths[int(rdd_bool)])
    cursor = cnx.execute("SELECT * FROM CourseReviews WHERE UniqueUserId=? AND CourseNumber=?", (user_id, course_id))
    if len(cursor.fetchall()) == 0: 
        cursor = cnx.execute("INSERT INTO CourseReviews (UniqueUserId, CourseNumber, {0}) VALUES (?, ?, ?)".format(column), (user_id, course_id, rating,))
        cnx.commit()
        cnx.close()
        return "success"
    else:
        cnx.close()
        return updateRating(course_id, user_id, column, rating, rdd_bool)


# -----------------------------------------------------------
# Update reviews, ratings or semester of a course
# -----------------------------------------------------------

def updateReview(course_id, user_id, review, rdd_bool):
    cnx = sqlite3.connect(paths[int(rdd_bool)])
    cursor = cnx.execute("UPDATE CourseReviews SET Review=?, VerificationStatus=?, Date=? WHERE CourseNumber=? AND UniqueUserId=?", (review, int(rdd_bool), int(time.time() * 1000), course_id, user_id,))
    cnx.commit()
    rowsAffected = cursor.rowcount
    cnx.close()
    if rowsAffected < 1:
        return "fail"
    else:
        return "success"


def updateRating(course_id, user_id, column, rating, rdd_bool):
    cnx = sqlite3.connect(paths[int(rdd_bool)])
    cursor = cnx.execute("UPDATE CourseReviews SET {0}=? WHERE CourseNumber=? AND UniqueUserId=?".format(column), (rating, course_id, user_id,))
    cnx.commit()
    rowsAffected = cursor.rowcount
    cnx.close()
    if rowsAffected < 1:
        return "fail"
    else:
        return "success"
    

def updateSemester(course_id, user_id, semester, rdd_bool):
    cnx = sqlite3.connect(paths[int(rdd_bool)])
    cursor = cnx.execute("UPDATE CourseReviews SET Semester=? WHERE CourseNumber=? AND UniqueUserId=?", (semester, course_id, user_id,))
    cnx.commit()
    rowsAffected = cursor.rowcount
    cnx.close()
    if rowsAffected < 1:
        return "fail"
    else:
        return "success"

# -----------------------------------------------------------
# Remove reviews ratings or semester of a course
# -----------------------------------------------------------

def removeCourseReview(course_id, user_id, rdd_bool):
    cnx = sqlite3.connect(paths[int(rdd_bool)])
    cursor = cnx.execute("UPDATE CourseReviews SET Review=NULL, VerificationStatus=NULL WHERE CourseNumber=? AND UniqueUserId=?", (course_id, user_id,))
    cnx.commit()
    rowsAffected = cursor.rowcount
    cnx.close()
    if rowsAffected < 1:
        return "fail"
    else:
        return "success"
    

def removeCourseRating(course_id, user_id, column, rdd_bool):
    cnx = sqlite3.connect(paths[int(rdd_bool)])
    cursor = cnx.execute("UPDATE CourseReviews SET {0}=NULL WHERE CourseNumber=? AND UniqueUserId=?".format(column), (course_id, user_id,))
    cnx.commit()
    rowsAffected = cursor.rowcount
    cnx.close()
    if rowsAffected < 1:
        return "fail"
    else:
        return "success"
    

def removeSemester(course_id, user_id, rdd_bool):
    cnx = sqlite3.connect(paths[int(rdd_bool)])
    cursor = cnx.execute("UPDATE CourseReviews SET Semester=NULL WHERE CourseNumber=? AND UniqueUserId=?", (course_id, user_id,))
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

def getThingsFromUser(user_id, rdd_bool):
    cnx = sqlite3.connect(paths[int(rdd_bool)])
    cursor = cnx.execute("SELECT CourseNumber, Review, VerificationStatus, Semester, Recommended, Interesting, Difficulty, Effort, Resources FROM CourseReviews WHERE UniqueUserId=? ORDER BY Date DESC", (user_id,))
    data = [dict((cursor.description[i][0], value) for i, value in enumerate(row)) for row in cursor.fetchall()]
    cnx.close()
    return json.dumps((r[0] if data else None) if False else data)
