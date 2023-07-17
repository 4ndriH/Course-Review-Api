import requests
import json
import expectedResults as expRes
import sys

access_token = ''
url = 'https://rubberducky.vsos.ethz.ch:1855/'
rdd = '&RDD=@jmWveQtmf9a2v9JC-7fXCQj'
username = 'MT6o3ZRdHkzCm3FX'
password = 'xje@tuf6fge.wqh.QMA'
offset = 20
successCnt = 0
verificationURLs = ['https://rubberducky.vsos.ethz.ch:1855/course/00-010-00X?' + rdd, 'https://rubberducky.vsos.ethz.ch:1855/rating/00-020-00X?' + rdd]
sys.tracebacklimit = 0

# ----------------------------------------
# API request decorators
# ----------------------------------------

def apiGetRequest(test, weirdUrlExtension='', endpoint='', parameters=''):
    APIresponse = None  
    if endpoint == '':
        APIresponse = requests.get(url)
    else:
        APIresponse = requests.get(url + endpoint + weirdUrlExtension + "?" + parameters + rdd, headers={'Authorization': 'Bearer ' + access_token})
    test(APIresponse)


def apiPostRequest(test, endpoint='', parameters='', authData={}):
    APIresponse = requests.post(url + endpoint + "?" + parameters + rdd, data=authData, headers={'Authorization': 'Bearer ' + access_token})
    test(APIresponse)


def apiPostRequestRating(test, columnList, ratingList, endpoint='', parameters='', authData={}):
    APIresponse = ''
    for i in range(0, 5):
        APIresponse = requests.post(url + endpoint + "?" + parameters + 'rating_id=' + columnList[i] + '&rating=' + str(ratingList[i]) + rdd, data=authData, headers={'Authorization': 'Bearer ' + access_token})
        if APIresponse.status_code != 200:
            break
    test(APIresponse)


# ----------------------------------------
# Helper functions
# ----------------------------------------

def verifyResponse(statusCode, expectedResponse, actualResponse, throwException=False):
    if statusCode == 200 and actualResponse == expectedResponse:
        print('\u2705')
        global successCnt
        successCnt += 1
    else:
        print('\u274C' + '\t[Status code: ' + str(statusCode) + ' | Correct Response: ' + str(actualResponse == expectedResponse) + ']')
        if throwException:
            raise Exception('Crucial Functionality is missing!')


def getJson(apiR):
    return json.loads(json.loads(apiR.content.decode('utf-8')))


# ----------------------------------------
# Basic Functionality Tests
# ----------------------------------------

def connectionTest(apiR):
    print(f"{'Connection:' : <{offset}}", end='')
    verifyResponse(apiR.status_code, expRes.home, json.loads(apiR.content.decode('utf-8')), True)
    

def authenticationTest(apiR):
    print(f"{'Authentication:' : <{offset}}", end='')
    verifyResponse(apiR.status_code, {}, {}, True)
    global access_token
    access_token = json.loads(apiR.content.decode('utf-8'))['access_token']


# ----------------------------------------
# CR Home
# ----------------------------------------

def latestReviewsTest(apiR):
    print(f"{'Latest Reviews:' : <{offset}}", end='')
    verifyResponse(apiR.status_code, expRes.latestReviews, getJson(apiR))


def allReviewsTest(apiR):
    print(f"{'All Reviews:' : <{offset}}", end='')
    verifyResponse(apiR.status_code, expRes.allReviews, getJson(apiR))


def statsTest(apiR):
    print(f"{'Statistics:' : <{offset}}", end='')
    verifyResponse(apiR.status_code, expRes.stats, getJson(apiR))


# ----------------------------------------
# CR Course
# ----------------------------------------

def courseTest(apiR):
    print(f"{'Course:' : <{offset}}", end='')
    verifyResponse(apiR.status_code, expRes.course, getJson(apiR))


def ratingTest(apiR):
    print(f"{'Rating:' : <{offset}}", end='')
    verifyResponse(apiR.status_code, expRes.rating, getJson(apiR))


# ----------------------------------------
# CR User
# ----------------------------------------

def userStuffTest(apiR):
    print(f"{'User Stuff:' : <{offset}}", end='')
    verifyResponse(apiR.status_code, expRes.userStuff, getJson(apiR))


def insertReviewTest(apiR):
    print(f"{'Insert Review:' : <{offset}}", end='')
    verifyResponse(apiR.status_code, expRes.insertReview, getJson(requests.get(verificationURLs[0])))


def insertRatingTest(apiR):
    print(f"{'Insert Rating:' : <{offset}}", end='')
    verifyResponse(apiR.status_code, expRes.insertRating, getJson(requests.get(verificationURLs[1])))


def updateReviewTest(apiR):
    print(f"{'Update Review:' : <{offset}}", end='')
    verifyResponse(apiR.status_code, expRes.updateReview, getJson(requests.get(verificationURLs[0])))


def updateRatingTest(apiR):
    print(f"{'Update Rating:' : <{offset}}", end='')
    verifyResponse(apiR.status_code, expRes.updateRating, getJson(requests.get(verificationURLs[1])))


def insertSemesterTest(apiR):
    print(f"{'Insert Semester:' : <{offset}}", end='')
    verifyResponse(apiR.status_code, expRes.insertSemester, getJson(requests.get(verificationURLs[0])))


def removeSemesterTest(apiR):
    print(f"{'Remove Semester:' : <{offset}}", end='')
    verifyResponse(apiR.status_code, expRes.removeSemester, getJson(requests.get(verificationURLs[0])))


def removeReviewTest(apiR):
    print(f"{'Remove Review:' : <{offset}}", end='')
    verifyResponse(apiR.status_code, expRes.removeReview, getJson(requests.get(verificationURLs[0])))


def removeRatingTest(apiR):
    print(f"{'Remove Rating:' : <{offset}}", end='')
    verifyResponse(apiR.status_code, expRes.removeRating, getJson(requests.get(verificationURLs[1])))


# ----------------------------------------
# Running the tests
# ----------------------------------------

print("=== Testing API ===")
apiGetRequest(connectionTest)
apiPostRequest(authenticationTest, endpoint='token', authData={'username':username,'password':password})
apiGetRequest(latestReviewsTest, endpoint='latestReviews')
apiGetRequest(allReviewsTest, endpoint='allReviews')
apiGetRequest(statsTest, endpoint='stats')
apiGetRequest(courseTest, endpoint='course', weirdUrlExtension='/00-000-00X')
apiGetRequest(ratingTest, endpoint='rating', weirdUrlExtension='/00-000-00X')
apiGetRequest(userStuffTest, endpoint='userStuff', weirdUrlExtension='/dummy%40ethz.ch')
apiPostRequest(insertReviewTest, endpoint='insertReview', parameters='course_id=00-010-00X&user_id=labrat%40ethz.ch&review=beep%20boop')
apiPostRequestRating(insertRatingTest, ['Recommended', 'Interesting', 'Difficulty', 'Effort', 'Resources'], [1, 2, 3, 4, 5], endpoint='insertRating', parameters='course_id=00-020-00X&user_id=labrat%40ethz.ch&')
apiPostRequest(updateReviewTest, endpoint='insertReview', parameters='course_id=00-010-00X&user_id=labrat%40ethz.ch&review=updoot')
apiPostRequest(updateRatingTest, endpoint='insertRating', parameters='course_id=00-020-00X&user_id=labrat%40ethz.ch&rating_id=Recommended&rating=2')
apiPostRequest(insertSemesterTest, endpoint='updateSemester', parameters='course_id=00-010-00X&user_id=labrat%40ethz.ch&semester=FS99')
apiPostRequest(removeSemesterTest, endpoint='removeSemester', parameters='course_id=00-010-00X&user_id=labrat%40ethz.ch')
apiPostRequest(removeReviewTest, endpoint='removeReview', parameters='course_id=00-010-00X&user_id=labrat%40ethz.ch')
apiPostRequest(removeRatingTest, endpoint='removeRating', parameters='course_id=00-020-00X&user_id=labrat%40ethz.ch&rating_id=Recommended')

if successCnt < 16:
    raise Exception(str(successCnt) + '/16 tests passed!')
else:
    print("=== 16/16 tests passed! ===")