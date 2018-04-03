#
# Credits:
# - Italo Nicola
# - Andre Almeida
#

#
# TODOs
#
# - Add more information to each data, example: which week it was from, a link to its description, etc
# - Improve front-end
# - Add position shifting information
#

import requests
import json
import os
import threading
from tabulate import tabulate
from operator import itemgetter
from flask import Flask, request, jsonify, make_response

global_problems_sorted = []
global_id_to_user = {}
global_team_id_to_user = {}
global_user_solved = {}

TIMER = 60 * 30

def initialize():
    global global_problems_sorted
    global global_id_to_user
    global global_user_solved
    global global_team_id_to_user
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
                    problem['accepted'] = []                    # list of unique people who were accepted by id
                    #problem['rejected'] = []                   # TODO: think about this
                    problems_data[problem['_id']] = problem
                for contestant in metadata['contestants']:
                    uname = contestant["id"]["local"]["username"]
                    if uname not in global_user_solved:
                        global_user_solved[uname] = []
                    global_id_to_user[contestant["id"]["_id"]] = uname
                    if "team" in contestant:
                        tid = contestant["team"]["_id"]
                        if tid not in global_team_id_to_user:
                            global_team_id_to_user[tid] = []
                        global_team_id_to_user[tid].append(uname)
                        
    #print(global_user_solved)
    #print(global_id_to_user)
                       
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
                        problems_data[parsed_res_data[1]]['accepted'].append(parsed_res_data[0]) # store user id
                        #print('Problem ' + parsed_res_data[1] + ' solved by ' + parsed_res_data[0]) # DEBUG
                        if parsed_res_data[0] not in global_id_to_user: # if it is a team, not a user
                            for u in global_team_id_to_user[parsed_res_data[0]]:
                                global_user_solved[u].append(parsed_res_data[1]) # map user to problem
                        else: # if it is a user, not a team
                            global_user_solved[global_id_to_user[parsed_res_data[0]]].append(parsed_res_data[1]) # map user to problem

    # sort data using number of accepted results as key
    problems = problems_data.values()
    problems = sorted(problems, key=lambda k: len(k['accepted']))

    position = 0;
    total_position = 0;
    len_accepted = -1;
    for p in problems:
        total_position += 1
        l = len(p['accepted'])
        if l != len_accepted:
            len_accepted = l
            position = total_position
        p['position'] = position 

    global_problems_sorted = problems

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
            problem['position'],
            problem['name'],
            len(problem['accepted']),
            memlimit,
            timelimit
        ])

    # and print it in a fancy table way :)
    table_header = ["Position", "Name", "# of Accepted", "Mem. limit", "Time limit"]
    print(tabulate(table_data, table_header))

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
    JOINED_CONTESTS_URL = "https://www.codepit.io/api/v1/contest/list/joined/0"

    # fetch all contests I've ever joined in this account
    print("Fetching contests...")
    joined_contests_req = session.get(JOINED_CONTESTS_URL)
    placar_ids = [c["_id"] for c in joined_contests_req.json()['contests']]

    print("Fetching problems...")
    for pid in placar_ids:
        req_get = session.get(SCORE_URL_TEMPLATE % pid)
        score_data = req_get.json()

        with open('resources/%s-metadata.json' % pid, 'w') as outfile:
            json.dump(score_data, outfile)

        results_get = session.get(RESULTS_URL_TEMPLATE % pid)
        results_data = results_get.json()

        with open('resources/%s-results.json' % pid, 'w') as outfile:
            json.dump(results_data, outfile)


def update_and_process():
    global TIMER
    fetch_contests_data()
    initialize()
    threading.Timer(TIMER, update_and_process).start() # call itself later


# WebServer
app = Flask(__name__)

@app.route('/all', methods = ['GET'])
def all():
    if request.method == 'GET':
        response = jsonify(global_problems_sorted)
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response

@app.route('/user/<uname>/solved', methods = ['GET'])
def user_solved(uname):
    if request.method == 'GET':
        response = jsonify(global_user_solved[uname])
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response

# TODO: uncomment this, but add some kind of safety against spammers
@app.route('/update', methods = ['PUT'])
def update():
    if request.method == 'PUT':
        #fetch_contests_data()
        #initialize()
        response = make_response()
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response


if __name__ == "__main__":
    update_and_process()
    app.run(host='0.0.0.0', port=5000, debug=False)

