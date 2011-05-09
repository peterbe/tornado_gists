import markdown
from dateutil.parser import parse as date_parse
import anyjson
from pprint import pprint
import datetime
import tornado.web
from utils.routes import route, route_redirect
from utils.timesince import smartertimesince
from utils import gravatar_html
from apps.main.handlers import BaseHandler


@route(r'/add/$', name="add_gist")
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
        gist_struct = anyjson.deserialize(response.body)
        #pprint(gist_struct)
        try:
            gist_info = gist_struct['gists'][0]
        except KeyError:
            # TODO: redirect to a warning page
            # gist is not found
            url = self.reverse_url("gist_not_found")
            url += '?gist_id=%s' % gist_id
            self.redirect(url)

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

        self.redirect(self.reverse_url('edit_gist', gist.gist_id))
        #files = iter(gist.files)
        #self.fetch_files(gist, files)

    def fetch_files(self, gist, files_iterator, response=None): # pragma: no cover
        # don't think we need this any more
        # Might be good one day for full text indexing search or something
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

@route(r'/notfound/$', name="gist_not_found")
class GistNotFoundHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        options = self.get_base_options()
        options['gist_id'] = self.get_argument('gist_id', None)
        self.render("gist_not_found.html", **options)

class GistBaseHandler(BaseHandler):

    def find_gist(self, gist_id):
        try:
            gist = self.db.Gist.one({'gist_id': int(gist_id)})
            assert gist
            return gist
        except (ValueError, AssertionError):
            raise tornado.web.HTTPError(404, "Gist not found")

@route(r'/(\d+)/$', name="view_gist")
class GistHandler(GistBaseHandler):

    def get(self, gist_id):
        options = self.get_base_options()
        gist = self.find_gist(gist_id)
        assert gist.gist_id == int(gist_id)
        options['gist'] = gist
        options['edit'] = False
        _vote_search = {'gist.$id':gist._id, 'comment':None}
        gist_points = self.db.GistPoints.one({'gist.$id': gist._id})
        if gist_points:
            options['vote_points'] = gist_points.points
        else:
            options['vote_points'] = 0

        options['has_voted_up'] = False
        if options['user']:
            _user_vote_search = dict(_vote_search)
            _user_vote_search['user.$id'] = options['user']._id
            options['has_voted_up'] = bool(
              self.db.Vote.collection.one(_user_vote_search))
        self.render("gist.html", **options)

@route(r'/(\d+)/edit/$', name="edit_gist")
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

        # fix 404 error if no description be posted
        # use gist_id as default description
        description = self.get_argument('description', u'GIST-%s' % gist_id).strip()
        discussion = self.get_argument('discussion', u'')
        tags = self.get_argument('tags', u'')
        tags = [x.strip() for x in tags.split(',') if x.strip()]

        try:
            # test if the markdown plain text isn't broken
            markdown.markdown(discussion, safe_mode="escape")
        except Exception:
            raise
        gist.description = description
        gist.discussion = discussion
        gist.discussion_format = u'markdown'
        gist.tags = tags
        gist.update_date = datetime.datetime.now()
        gist.save()
        url = self.reverse_url('view_gist', gist.gist_id)
        self.redirect(url)


@route(r'/(\d+)/delete/$', name="delete_gist")
class DeleteGistHandler(GistHandler):

    @tornado.web.authenticated
    def get(self, gist_id):
        gist = self.find_gist(gist_id)
        if gist.user != self.get_current_user():
            raise tornado.web.HTTPError(403, "Not yours")

        # delete all comments of this gist
        for comment in self.db.Comment.find({'gist.$id': gist._id}):
            comment.delete()

        gist.delete()
        self.redirect('/?gist=deleted')


@route(r'/preview_markdown$', name="preview_markdown")
class PreviewMarkdownHandler(BaseHandler):
    def check_xsrf_cookie(self):
        pass

    def post(self):
        text = self.get_argument('text')
        html = markdown.markdown(text, safe_mode="escape")
        self.write_json(dict(html=html))

@route(r'/tags.json$', name="autocomplete_tags")
class AutocompleteTags(BaseHandler):
    def check_xsrf_cookie(self):
        pass

    def get(self):
        search = self.get_argument('q', None)
        all_tags = set()
        all_tags_lower = set()
        search = {'tags': {'$ne': []}}
        for gist in self.db.Gist.collection.find(search):
            for tag in gist['tags']:
                if tag.lower() not in all_tags_lower:
                    all_tags.add(tag)
                    all_tags_lower.add(tag.lower())
        all_tags = list(all_tags)
        all_tags.sort(lambda x,y:cmp(x.lower(), y.lower()))
        self.write_json(dict(tags=all_tags))

@route(r'/(\d+)/comments', name="comments")
class CommentsHandler(GistHandler):

    def get(self, gist_id):
        #sg = ShowGravatar(self)
        gist = self.find_gist(gist_id)
        comments = []
        now = datetime.datetime.now()
        for comment in self.db.Comment.find({'gist.$id': gist._id}).sort('add_date', 1):
            #pprint(dict(comment.user))
            comment_dict = dict(
              comment=markdown.markdown(comment.comment, safe_mode='escape'),
              ago=smartertimesince(comment.add_date, now),
              file=comment.file,
              id=str(comment._id),
              user=dict(name=comment.user.name,
                        login=comment.user.login,
                        )
            )
            if comment.user.gravatar_id:
                comment_dict['user']['gravatar_html'] = \
                  gravatar_html(self.is_secure(), comment.user.gravatar_id, width_and_height=20)
            #pprint(comment_dict)
            comments.append(comment_dict)

        self.write_json(dict(comments=comments))

    @tornado.web.authenticated
    def post(self, gist_id):
        options = self.get_base_options()
        gist = self.find_gist(gist_id)
        comment = self.get_argument('comment')
        file_ = self.get_argument('file')

        # check that the comment hasn't already been posted,
        # for example by double-clicking the submit button
        search = {'user.$id': options['user']._id,
                  'gist.$id': gist._id}
        for c in self.db.Comment.find(search):
            if c.comment == comment:
                break
        else:
            c = self.db.Comment()
            c.user = options['user']
            c.gist = gist
            c.comment = comment
            c.comment_format = u'markdown'
            c.file = file_
            c.save()

        url = self.reverse_url('view_gist', gist.gist_id)
        anchor = gist.files.index(file_) + 1
        self.redirect(url + "#comments-%s" % anchor)
