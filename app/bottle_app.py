__author__ = 'idMolotov'

from bottle import default_app, route, run
from bottle import post
import bottle
import json, re
import urllib.request
import urllib.parse

# define Redmine access vars
redmine_admin_key = 'xxxxx'
redmine_url = 'http://www.redmine/'


@route('/')
def hello_world():
    return 'Hell low from Bottle!'


@route('/bitmine')
@post('/bitmine')
def bitmine():
    data = None


    if bottle.request.json:
        data = bottle.request.json
    elif bottle.request.forms.get('payload', None):
        data = json.loads(bottle.request.forms.get('payload'))

    if data:
        commits_list = data["commits"]

        for commit in commits_list:
            commit_message = commit['message']
            m = re.findall(r"\d{5,6}", commit_message)
            if len(m) > 0:
                task_id_detected = int(m[0])

                author = commit['author']
                utctimestamp = commit['utctimestamp']
                branch = commit['branch']
                
                file_num = str(len(commit['files']))

                # https://bitbucket.org/_company_/_project_/commits/_commit_id_
                commit_url = data["canon_url"] + data["repository"]["absolute_url"] + 'commits/' + commit['raw_node']

                redmine_comment_text = 'source code commit for this task ' \
                                       + '\n  URL: ' + urllib.request.quote(commit_url, safe=':/') \
                                       + '\n  Author: ' + author \
                                       + '    Time: ' + utctimestamp \
                                       + '\n  Branch: ' + branch \
                                       + '    Files: ' + file_num \
                                       + '\n  Message: ' + commit_message \
                                       + ''

                print(redmine_comment_text)
                print(json.dumps(redmine_comment_text))

                '''
                http://www.redmine/issues/_12345_
                PUT /issues/[id].json
                {
                  "issue": {
                    "subject": "Subject changed",
                    "notes": "The subject was changed"
                  }
                }
                X-Redmine-API-Key: redmine_admin_key
                '''

                put_url = redmine_url + '/issues/%s.json' % task_id_detected
                out_data = json.dumps({"issue": {"notes": redmine_comment_text}})
                out_data = out_data.encode('utf-8')

                request = urllib.request.Request(put_url, method='PUT')
                request.add_header("Content-Type", "application/json;charset=utf-8")
                request.add_header("X-Redmine-API-Key", redmine_admin_key)
                f = urllib.request.urlopen(request, out_data)
                print(f.read().decode('utf-8'))


    return 'bitmine - OK'


application = default_app()


if __name__ == "__main__":
    run(host='127.0.0.1', port=80, debug=True,reloader=True)
