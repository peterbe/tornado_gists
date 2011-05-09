from pymongo import ASCENDING, DESCENDING
from urllib import quote
from apps.main.handlers import BaseHandler
from apps.gists.handlers import GistBaseHandler
from utils.routes import route, route_redirect
from models import Vote

@route(r'/(\d+)/vote/toggle/$', name="vote_toggle_gist")
class VoteupGistHandler(GistBaseHandler):

    def post(self, gist_id):
        # used by $.post()
        user = self.get_current_user()
        if not user:
            self.write_json(dict(not_logged_in=True))
            return
        gist = self.find_gist(gist_id)
        search = {'user.$id': user._id,
                  'gist.$id': gist._id,
                  'comment': None}
        vote = self.db.Vote.one(search)
        if not vote:
            vote = self.db.Vote()
            vote.user = user
            vote.gist = gist
            vote.points = 1
            vote.save()
            points_diff = 1
        else:
            vote.delete()
            points_diff = -1

        # always return the total
        del search['user.$id']
        points = sum([x['points'] for x in
                      self.db.Vote.collection.find(search)])
        # to be able to do quick aggregates, on summed votes,
        # copy this number over to the gist now
        gist_points = self.db.GistPoints.one({'gist.$id': gist._id})
        if not gist_points:
            gist_points = self.db.GistPoints()
            gist_points.gist = gist
        gist_points.points = points
        gist_points.save()

        user_points = self.db.UserPoints.one({'user.$id': gist.user._id})
        if not user_points:
            user_points = self.db.UserPoints()
            user_points.user = gist.user
            user_points.points = 0
        user_points.points += points_diff
        user_points.save()

        self.write_json(dict(points=points))


@route(r'/most/loved/', name="most_loved")
class MostLovedHandler(BaseHandler):
    def get(self):
        options = self.get_base_options()
        options['page_title'] = "Most loved"
        options['gist_points'] = (self.db.GistPoints
          .find({'points': {'$gt': 0}})
          .sort('points', DESCENDING).limit(20))
        options['user_points'] = (self.db.UserPoints
          .find({'points': {'$gt': 0}})
          .sort('points', DESCENDING).limit(20))

        self.render("voting/most_loved.html", **options)

@route(r'/most/loved/(\w+)', name="most_loved_user")
class MostLovedUserHandler(BaseHandler):

    def get(self, login):
        user = self.db.User.one({'login':login})
        if not user:
            raise tornado.web.HTTPError(404, "No user by that login")

        user_points = self.db.UserPoints.one({'user.$id': user._id})
        if not user_points:
            self.write("Sorry, no points at all for %s yet" % user.login)
            return
        options = self.get_base_options()
        options['user_points'] = user_points
        gist_ids = [x['_id'] for x in self.db.Gist.collection.find({'user.$id': user._id})]
        options['gist_points'] = (self.db.GistPoints
          .find({'points': {'$gt': 0},
                 'gist.$id': {'$in': gist_ids}})
          .sort('points', DESCENDING).limit(20))
        options['no_total_gists'] = self.db.Gist.find({'user.$id': user._id}).count()

        self.render('voting/most_loved_user.html', **options)
