import time
import logging
import json
import urllib2
import xqueue_util as util
import settings
import urlparse
import project_urls
import requests
import boto3
import auth

import traceback



log = logging.getLogger(__name__)

QUEUE_NAME = auth.XQUEUE_INTERFACE['queue_name']
LAMBDA_URL = project_urls.LAMBDA_URL

def each_cycle():
    print('\n[*]Logging in to xqueue: ' + QUEUE_NAME)
    try:
        session = util.xqueue_login()
    except Exception as ex:
        print('Error: Unable to log into XQueue:', ex)
        return
    success_length, queue_length = get_queue_length(QUEUE_NAME, session)
    print('Get queue successfully: ' + str(success_length) + ', number of queues: ' + str(queue_length))
    if success_length and queue_length > 0:
        success_get, queue_item = get_from_queue(QUEUE_NAME, session)
        # print(queue_item)
        success_parse, content = util.parse_xobject(queue_item, QUEUE_NAME)
        if success_get and success_parse:
            try:
                correct, score, comment = grade(content)
            except Exception as ex:
                print(ex)
                traceback.print_exc()
                correct, score, comment =  False, 0, '<p>SERVER UNEXPECTED ERROR</p>'
            print('correct: ', correct,'score: ', score, 'comment: ', comment)
            content_header = json.loads(content['xqueue_header'])
            content_body = json.loads(content['xqueue_body'])
            xqueue_header, xqueue_body = util.create_xqueue_header_and_body(content_header['submission_id'], content_header['submission_key'], correct, score, comment, 'reference_dummy_grader')
            (success, msg) = util.post_results_to_xqueue(session, json.dumps(xqueue_header), json.dumps(xqueue_body),)
            if success:
                print("successfully posted result back to xqueue")
                print(msg)



def grade(content):
    body = json.loads(content['xqueue_body'])
    student_info = json.loads(body.get('student_info', '{}'))
    email = student_info.get('student_email', '')
    files = json.loads(content['xqueue_files'])
    grader_payload = json.loads(body.get('grader_payload', '{}'))
    question = grader_payload.get('question', '')


    score = 0
    count = 0
    comment = ''
    lambda_client = boto3.client('lambda', region_name='us-east-1')
    for (filename, fileurl) in files.iteritems():
        try:
            result = lambda_client.invoke(
                FunctionName=LAMBDA_URL,
                InvocationType='RequestResponse',
                LogType = 'None',
                Payload = json.dumps({ "file" : fileurl, "question" : question, "info": student_info})
            )
        except Exception as ex:
            comment += '<p><emph>File: ' + filename + ': error</emph></p>'
            comment += '<p>Comment: Grading Error</p>'
            count += 1
            print('Grading error:',ex)
            continue

        response = json.loads(result['Payload'].read())
        if response['correct']:
            comment += '<p>File: ' + filename + ': correct</p>'
            comment += '<p>Comment: ' + "<br />".join(response['comment'].split("\n")) + '</p>'
        else: 
            comment += '<p><emph>File: ' + filename + ': error</emph></p>'
            comment += '<p>Comment: ' + "<br />".join(response['comment'].split("\n")) + '</p>'
        if not score:
            score = response['score']
        else:
            score += response['score']
        count += 1
    score = score / count
    if score > 0:
        success = True
    else: 
        success = False
    return success, score, comment


    # auth = AWSRequestsAuth(aws_access_key= KEY,
    #                 aws_secret_access_key= SEC,
    #                 aws_host= settings.IAM['aws_host'],
    #                 aws_region= settings.IAM['aws_region'],
    #                 aws_service= settings.IAM['aws_service'])

    # score = None
    # count = 0
    # comment = ''
    # for (filename, fileurl) in files.iteritems():
    #     r = requests.post(url = LAMBDA_URL, data = json.dumps({ "file" : fileurl, "question" : question}), auth=auth)
    #     # r = requests.post(url = LAMBDA_URL, data = json.dumps({ "file" : fileurl}))
    #     response = r.json()
    #     print(response)
    #     if response['correct']:
    #         comment += '<p>File: ' + filename + ': correct</p>'
    #         comment += '<p>Comment: ' + "<br />".join(response['comment'].split("\n")) + '</p>'
    #     else: 
    #         comment += '<p><emph>File: ' + filename + ': error</emph></p>'
    #         comment += '<p>Comment: ' + "<br />".join(response['comment'].split("\n")) + '</p>'
            
    #     if not score:
    #         score = response['score']
    #     else:
    #         score += response['score']
    #     count += 1

    #     r.close()
    # score /= count
    # if score > 0:
    #     success = True
    # else: 
    #     success = False
    # return success, score, comment


def get_from_queue(queue_name,xqueue_session):
    """
    Get a single submission from xqueue
    """
    try:
        success, response = util._http_get(xqueue_session,
                                           urlparse.urljoin(auth.XQUEUE_INTERFACE['url'], project_urls.XqueueURLs.get_submission),
                                           {'queue_name': queue_name})
    except Exception as err:
        return False, "Error getting response: {0}".format(err)
    
    return success, response



def get_queue_length(queue_name,xqueue_session):
    """
    Returns the length of the queue
    """
    try:
        success, response = util._http_get(xqueue_session,
                                           urlparse.urljoin(auth.XQUEUE_INTERFACE['url'], project_urls.XqueueURLs.get_queuelen),
                                           {'queue_name': queue_name})
        
        if not success:
            return False,"Invalid return code in reply"
    
    except Exception as e:
        log.critical("Unable to get queue length: {0}".format(e))
        return False, "Unable to get queue length."
    
    return True, response

try:
    logging.basicConfig()
    while True:
        each_cycle()
        time.sleep(2)
except KeyboardInterrupt:
    print('^C received, shutting down')
