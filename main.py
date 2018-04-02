#
# Credits:
# - Italo Nicola
# - Andre Almeida
#

#
# TODOs
#
# - Fetch new contests automagically
# - Update data periodically
# - Add more information to each data, example: which week it was from, a link to its description, etc
# - Improve front-end
# - Add position shifting information
#

import requests
import json
import os
from tabulate import tabulate
from operator import itemgetter
from flask import Flask, request, jsonify

global_problems_sorted = []

def initialize():
    global global_problems_sorted
    problems_data = {}

    files = []
    for (dirpath, dirnames, filenames) in os.walk('./resources'):
        files.extend(filenames)
        break

    # first process metadata, since we need to know which problems can be solved before parsin the results
    for f in files:
        if '-metadata' in f:
            with open('./resources/' + f) as data_from_file:
                metadata = json.load(data_from_file)
                for problem in metadata['problems']:
                    problem['accepted'] = []                    # list of unique people who were accepted
                    #problem['rejected'] = []                   # TODO: think about this
                    problems_data[problem['_id']] = problem
                       
    # then process the results now that we have all the problems mapped
    for f in files:
        if '-results' in f:
            with open('./resources/' + f) as data_from_file:
                results_data = json.load(data_from_file)
                for result in results_data['accepted']:
                    parsed_res_data = result.split(',')
                    if parsed_res_data[1] not in problems_data:
                        # TODO; log error, this shouldn't happen
                        continue
                    if parsed_res_data[0] not in problems_data[parsed_res_data[1]]['accepted']:
                        problems_data[parsed_res_data[1]]['accepted'].append(parsed_res_data[0])
                        #print('Problem ' + parsed_res_data[1] + ' solved by ' + parsed_res_data[0]) # DEBUG

    # sort data using number of accepted results as key
    problems = problems_data.values()
    problems = sorted(problems, key=lambda k: len(k['accepted']))

    global_problems_sorted = problems
    print('DEBUG')

    """
    # we now filter some data from the response
    table_data = []
    for problem in problems:
        memlimit = ""
        timelimit = ""
        if "memorylimit" in problem:
            memlimit = problem['memorylimit']
        if "timelimit" in problem:
            timelimit = problem['timelimit']
        table_data.append([
            problem['_id'],
            problem['name'],
            len(problem['accepted']),
            memlimit,
            timelimit
        ])

    # and print it in a fancy table way :)
    table_header = ["ID", "Name", "# of Accepted", "Mem. limit", "Time limit"]
    print(tabulate(table_data, table_header))
    """

def fetch_contests_data():
    CODEPIT_LOGIN_URL = "https://www.codepit.io/api/v1/user/login"
    CREDENTIALS_FILE = "credentials.txt"

    # getting our credentials from the secret file
    print("Getting our credentials...")
    with open(CREDENTIALS_FILE, "r") as cred_file:
        credentials = cred_file.read().strip().split(";")

    # preparing and sending our POST to Login
    print("Logging on Codepit...")
    post_data = {
        "email": credentials[0],
        "password": credentials[1]
    }

    # we open a session to keep the login cookies
    session = requests.session()

    req_post = session.post(url=CODEPIT_LOGIN_URL, data=post_data)
    if "error" in req_post.text:
        print("Login failed :(")
        exit(1)
    print("Login done!")

    SCORE_URL_TEMPLATE = "https://www.codepit.io/api/v1/contest/%s/metadata"
    RESULTS_URL_TEMPLATE = "https://www.codepit.io/api/v1/contest/%s/events/0"

    # TODO: move this to a configuration file (maybe fetch programatically for all problems I've entered?)
    placar_ids = ['5ab156d701a96e001940764f', '5aa6e07d80cd12006c997f4f', '5a9e754dbebc010018a6a353', '5a9800d8636fa800962e51e7', '5abddfc6636fa800962e6a86']

    print("Fetching contests data...")
    for pid in placar_ids:
        req_get = session.get(SCORE_URL_TEMPLATE % pid)
        score_data = req_get.json()

        with open('resources/%s-metadata.json' % pid, 'w') as outfile:
            json.dump(score_data, outfile)

        results_get = session.get(RESULTS_URL_TEMPLATE % pid)
        results_data = results_get.json()

        with open('resources/%s-results.json' % pid, 'w') as outfile:
            json.dump(results_data, outfile)


# WebServer
app = Flask(__name__)

@app.route('/all', methods = ['GET'])
def result():
    if request.method == 'GET':
        response = jsonify(global_problems_sorted)
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response


if __name__ == "__main__":
    #fetch_contests_data()
    #print('a')
    initialize()
    #print('b')
    app.run(host = '0.0.0.0', debug = True)

