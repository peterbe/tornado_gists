import markdown
from dateutil.parser import parse as date_parse
import anyjson
from pprint import pprint
import datetime
import tornado.web
from utils.routes import route, route_redirect
#from utils.gist_api import get_gist
from apps.main.handlers import BaseHandler

@route(r'/add/', name="add_gist")
class AddGistHandler(BaseHandler):

    @tornado.web.asynchronous
    @tornado.web.authenticated
    def post(self):
        gist_id = int(self.get_argument('gist_id'))
        gist = self.db.Gist.one({'gist_id': gist_id})
        if gist:
            return self.redirect(self.reverse_url('view_gist', gist_id))
        http = tornado.httpclient.AsyncHTTPClient()
        url = "http://gist.github.com/api/v1/json/%s" % gist_id
        http.fetch(url, callback=lambda r:self.on_gist_found(gist_id, r))

    def on_gist_found(self, gist_id, response):
        print "RESPONSE.body"
        print repr(response.body)
        gist_json = anyjson.deserialize(response.body)
        gist_info = gist_json['gists'][0]
        pprint(gist_info)
        gist = self.db.Gist()
        gist.gist_id = gist_id
        gist.description = unicode(gist_info.get('description', u''))
        #gist.created_at = date_parse(gist_info['created_at'])
        gist.created_at = unicode(gist_info['created_at'])
        gist.files = [unicode(x) for x in gist_info['files']]
        gist.contents = []
        gist.public = gist_info['public']
        gist.owner = unicode(gist_info['owner'])
        gist.repo = unicode(gist_info['repo'])
        gist.user = self.get_current_user()
        gist.save()

        self.redirect(self.reverse_url('view_gist', gist.gist_id))
        #files = iter(gist.files)
        #self.fetch_files(gist, files)

    def fetch_files(self, gist, files_iterator, response=None):
        if response is not None:
            gist.contents.append(unicode(response.body))
            gist.save()

        try:
            filename = files_iterator.next()
            http = tornado.httpclient.AsyncHTTPClient()
            url = "http://gist.github.com/raw/%s/%s" % (gist.gist_id, filename) # filename needs to be url quoted??
            http.fetch(url, callback=lambda r:self.fetch_files(gist, files_iterator, r))

        except StopIteration:
            self.redirect(self.reverse_url('view_gist', gist.gist_id))


@route(r'/(\d+)/?', name="view_gist")
class GistHandler(BaseHandler):
    def find_gist(self, gist_id):
        try:
            return self.db.Gist.one({'gist_id': int(gist_id)})
        except (ValueError, AssertionError):
            raise tornado.web.HTTPError(404, "Gist not found")

    def get(self, gist_id):
        options = self.get_base_options()
        gist = self.find_gist(gist_id)
        options['gist'] = gist
        options['edit'] = False
        self.render("gist.html", **options)

@route(r'/(\d+)/edit/', name="edit_gist")
class EditGistHandler(GistHandler):

    @tornado.web.authenticated
    def get(self, gist_id):
        options = self.get_base_options()
        gist = self.find_gist(gist_id)
        if gist.user != options['user']:
            raise tornado.web.HTTPError(403, "Not your gist")
        options['gist'] = gist
        options['edit'] = True
        self.render("gist.html", **options)

    @tornado.web.authenticated
    def post(self, gist_id):
        options = self.get_base_options()
        gist = self.find_gist(gist_id)
        if gist.user != options['user']:
            raise tornado.web.HTTPError(403, "Not your gist")
        description = self.get_argument('description').strip()
        discussion = self.get_argument('discussion', u'')
        try:
            # test if the markdown plain text isn't broken
            markdown.markdown(discussion, safe_mode="escape")
        except Exception:
            raise
        gist.description = description
        gist.discussion = discussion
        gist.discussion_format = u'markdown'
        gist.update_date = datetime.datetime.now()
        gist.save()
        url = self.reverse_url('view_gist', gist.gist_id)
        self.redirect(url + '?edited=yay')


@route(r'/(\d+)/delete/?', name="delete_gist")
class GistHandler(GistHandler):

    @tornado.web.authenticated
    def get(self, gist_id):
        gist = self.find_gist(gist_id)
        if gist.user != self.get_current_user():
            raise tornado.web.HTTPError(403, "Not yours")
        gist.delete()
        self.redirect('/?gist=deleted')
