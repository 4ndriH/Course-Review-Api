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
    cursor = cnx.execute("SELECT Review FROM CourseReviews WHERE CourseNumber=? AND VerificationStatus=1 ORDER BY Date DESC", (course_id,))
    data = [dict((cursor.description[i][0], value) for i, value in enumerate(row)) for row in cursor.fetchall()]
    cnx.close()
    return json.dumps((r[0] if data else None) if False else data)


def getCourseRating(CourseNumber):
    cnx = sqlite3.connect(path)
    cursor = cnx.execute("SELECT AVG(Recommended), AVG(Interesting), AVG(Difficulty), AVG(Effort), AVG(Resources), FROM CourseRatings WHERE CourseNumber=?", (CourseNumber,))
    data = [dict((cursor.description[i][0], value) for i, value in enumerate(row)) for row in cursor.fetchall()]
    cnx.close()
    return json.dumps((r[0] if data else None) if False else data)


# -----------------------------------------------------------
# Get CourseReview website statistics
# -----------------------------------------------------------

def getLatestReviews():
    cnx = sqlite3.connect(path)
    cursor = cnx.execute("SELECT CourseNumber FROM CourseReviews WHERE VerificationStatus= 1 GROUP BY CourseNumber HAVING MAX(Date) ORDER BY Date DESC limit 10")
    data = [dict((cursor.description[i][0], value) for i, value in enumerate(row)) for row in cursor.fetchall()]
    cnx.close()
    return json.dumps((r[0] if data else None) if False else data)


def getPublishedReviewStats():
    cnx = sqlite3.connect(path)
    cursor = cnx.execute("SELECT COUNT(DISTINCT CourseNumber) AS percourse, COUNT(*) AS total FROM CourseReviews WHERE VerificationStatus=1")
    data = [dict((cursor.description[i][0], value) for i, value in enumerate(row)) for row in cursor.fetchall()]
    cnx.close()
    return json.dumps((r[0] if data else None) if False else data)


def getAllCoursesWithReviews():
    cnx = sqlite3.connect(path)
    cursor = cnx.execute("SELECT CourseNumber FROM CourseReviews WHERE VerificationStatus=1 GROUP BY CourseNumber HAVING MAX(Date) ORDER BY Date")
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
        cursor = cnx.execute("INSERT INTO CourseReviews (UniqueUserId, CourseNumber, Review, Date) VALUES (?, ?, ?, ?)", (user_id, course_id, review, int(time.time() * 1000),))
        cnx.commit()
        cnx.close()
        return "inserted"
    else:
        return "You already submitted a review for this course"


def insertRating(course_id, user_id, column, rating):
    cnx = sqlite3.connect(path)
    cursor = cnx.execute("SELECT * FROM CourseStarRatings WHERE UniqueUserId=? AND CourseNumber=?", (user_id, course_id,))
    if len(cursor.fetchall()) == 0: 
        cursor = cnx.execute("INSERT INTO CourseStarRatings (UniqueUserId, CourseNumber, (%s)) VALUES (?, ?, ?)" % (column), (user_id, course_id, rating,))
        cnx.commit()
        cnx.close()
        return "success"
    else:
        return updateRating(course_id, user_id, column, rating)


# -----------------------------------------------------------
# Update reviews or ratings of a course
# -----------------------------------------------------------

def updateReview(course_id, user_id, review):
    cnx = sqlite3.connect(path)
    cursor = cnx.execute("UPDATE CourseReviews SET Review=?, VerificationStatus=0 WHERE CourseNumber=? AND UniqueUserId=?", (review, course_id, user_id,))
    cnx.commit()
    rowsAffected = cursor.rowcount
    cnx.close()
    if rowsAffected < 1:
        return "fail"
    else:
        return "success"


def updateRating(course_id, user_id, column, rating):
    cnx = sqlite3.connect(path)
    cursor = cnx.execute("UPDATE CourseStarRatings SET (%s)=? WHERE CourseNumber=? AND UniqueUserId=?" % (column), (rating, CourseNumber, user_id,))
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
    cursor = cnx.execute("DELETE FROM CourseReviews WHERE CourseNumber=? AND UniqueUserId=?", (course_id, user_id,))
    cnx.commit()
    rowsAffected = cursor.rowcount
    cnx.close()
    if rowsAffected < 1:
        return "fail"
    else:
        return "success"
    

def removeCourseRating(course_id, user_id, column):
    cnx = sqlite3.connect(path)
    cursor = cnx.execute("UPDATE CourseStarRatings SET (%s)=NULL WHERE CourseNumber=? AND UniqueUserId=?" % (column), (course_id, user_id,))
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
    cursor = cnx.execute("SELECT CourseNumber, Review, Verified FROM CourseReviews WHERE UniqueUserId=? ORDER BY Date DESC", (user_id,))
    result = cursor.fetchall()
    cnx.close()
    return result


def getStarRatingsFromUser(user_id):
    cnx = sqlite3.connect(path)
    cursor = cnx.execute("SELECT CourseNumber, Recommended, Interesting, Difficulty, Effort, Resources FROM CourseStarRatings WHERE UniqueUserId=? ORDER BY Date DESC", (user_id,))
    result = cursor.fetchall()
    cnx.close()
    return result