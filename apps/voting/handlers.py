from urllib import quote
from apps.gists.handlers import GistHandler
from utils.routes import route, route_redirect
from models import Vote

@route(r'/(\d+)/vote/up/', name="vote_up_gist")
class VoteupGistHandler(GistHandler):

    def post(self, gist_id):
        # used by $.post()
        user = self.get_current_user()
        if not user:
            self.write_json(dict(not_logged_in=True))
            return
        gist = self.find_gist(gist_id)
        vote = self.db.Vote.one({'user.$id': user._id,
                                 'gist.$id': gist._id,
                                 'comment': None})
        if not vote:
            vote = self.db.Vote()
            vote.user = user
            vote.gist = gist
        vote.points = 1
        vote.save()
        self.write_json(dict(points=vote.points))
