import threading
from subprocess import call

import codecs
import os, json

from werkzeug.contrib.fixers import ProxyFix
from flask import Flask, request, redirect, url_for, render_template, flash
from flask_dance.contrib.github import make_github_blueprint, github

# create our application
from centillion_search import Search


"""
The Centillion

The centillion is a search engine that indexes the following:
    - Folder of Markdown documents
    - Github issues
    - Google Drive folder

You provide:
    - Github API key via env var
    - Google Drive API key via file
"""


class UpdateIndexTask(object):
    def __init__(self, gh_access_token, diff_index=False):
        self.diff_index = diff_index
        thread = threading.Thread(target=self.run, args=())
        self.gh_access_token = gh_access_token
        thread.daemon = True
        thread.start()

    def run(self):
        search = Search(app.config["INDEX_DIR"])

        if(self.diff_index):
            raise Exception("diff index not implemented")

        from get_centillion_config import get_centillion_config
        config = get_centillion_config('config_centillion.json')

        search.update_index_issues(self.gh_access_token,config)
        search.update_index_markdown(self.gh_access_token,config)
        search.update_index_gdocs(config)



app = Flask(__name__)
app.wsgi_app = ProxyFix(app.wsgi_app)

# Load default config and override config from an environment variable
app.config.from_pyfile("config_flask.py")

#github_bp = make_github_blueprint()
github_bp = make_github_blueprint(
                        client_id = os.environ.get('GITHUB_OAUTH_CLIENT_ID'),
                        client_secret = os.environ.get('GITHUB_OAUTH_CLIENT_SECRET'),
                        scope='read:org')

app.register_blueprint(github_bp, url_prefix="/login")

contents404 = "<html><body><h1>Status: Error 404 Page Not Found</h1></body></html>"
contents403 = "<html><body><h1>Status: Error 403 Access Denied</h1></body></html>"
contents200 = "<html><body><h1>Status: OK 200</h1></body></html>"


##############################
# Flask routes

@app.route('/')
def index():

    if not github.authorized:
        return redirect(url_for("github.login"))

    else:

        username = github.get("/user").json()['login']

        resp = github.get("/user/orgs")
        if resp.ok:

            # If they are in team copper, redirect to search.
            # Otherwise, hit em with a 403
            all_orgs = resp.json()
            for org in all_orgs:
                if org['login']=='dcppc':
                    copper_team_id = '2700235'
                    mresp = github.get('/teams/%s/members/%s'%(copper_team_id,username))
                    if mresp.status_code==204:

                        # --------------------
                        # Business as usual
                        return redirect(url_for("search", query="", fields=""))

            return contents403

        return contents404

### @app.route('/')
### def index():
###     return redirect(url_for("search", query="", fields=""))

@app.route('/search')
def search():

    if not github.authorized:
        return redirect(url_for("github.login"))

    username = github.get("/user").json()['login']

    resp = github.get("/user/orgs")
    if resp.ok:

        all_orgs = resp.json()
        for org in all_orgs:
            if org['login']=='dcppc':

                copper_team_id = '2700235'

                mresp = github.get('/teams/%s/members/%s'%(copper_team_id,username))
                if mresp.status_code==204:

                    # --------------------
                    # Business as usual
                    query = request.args['query']
                    fields = request.args.get('fields')
                    if fields == 'None':
                        fields = None

                    search = Search(app.config["INDEX_DIR"])
                    if not query:
                        parsed_query = ""
                        result = []

                    else:
                        parsed_query, result = search.search(query.split(), fields=[fields])

                    totals = search.get_document_total_count()

                    return render_template('search.html', 
                                           entries=result, 
                                           query=query, 
                                           parsed_query=parsed_query, 
                                           fields=fields, 
                                           totals=totals)

    return contents403


@app.route('/update_index')
def update_index():

    if not github.authorized:
        return redirect(url_for("github.login"))

    username = github.get("/user").json()['login']

    resp = github.get("/user/orgs")
    if resp.ok:

        all_orgs = resp.json()
        for org in all_orgs:
            if org['login']=='dcppc':

                copper_team_id = '2700235'

                mresp = github.get('/teams/%s/members/%s'%(copper_team_id,username))
                if mresp.status_code==204:

                    #gh_oauth_token = github.token['access_token']
                    gh_access_token = app.config['GITHUB_TOKEN']

                    # --------------------
                    # Business as usual
                    UpdateIndexTask(gh_access_token, 
                                    diff_index=False)
                    flash("Rebuilding index, check console output")
                    return render_template("controlpanel.html", 
                                           totals={})

    return contents403



@app.route('/control_panel')
def control_panel():

    if not github.authorized:
        return redirect(url_for("github.login"))

    username = github.get("/user").json()['login']

    resp = github.get("/user/orgs")
    if resp.ok:

        all_orgs = resp.json()
        for org in all_orgs:
            if org['login']=='dcppc':

                copper_team_id = '2700235'

                mresp = github.get('/teams/%s/members/%s'%(copper_team_id,username))
                if mresp.status_code==204:

                    return render_template("controlpanel.html", 
                                           totals={})

    return contents403


@app.errorhandler(404)
def oops(e):
    return contents404

if __name__ == '__main__':
    # if running local instance, set to true
    os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = 'true'
    app.run(host="0.0.0.0",port=5000)

