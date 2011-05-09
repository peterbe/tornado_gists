import json
from apps.main.tests.test_handlers import HandlersTestCaseBase

class VotingHandlersTestCase(HandlersTestCaseBase):

    def test_toggle_vote(self):
        peter = self.db.User()
        peter.login = u'peterbe'
        peter.email = u''
        peter.company = u''
        peter.name = u'Peter'
        peter.save()

        ernst = self.db.User()
        ernst.login = u'ernst'
        ernst.email = u''
        ernst.company = u''
        ernst.name = u'Ernst'
        ernst.save()

        gist = self.db.Gist()
        gist.user = ernst
        gist.gist_id = 1234
        gist.created_at = u'yesterday'
        gist.files = [u'foo.py']
        gist.description = u'Testing the Atom feed'
        gist.discussion = u"""Full `markdown` description:
        function foo():
            return bar
        """
        gist.save()

        url = self.reverse_url('vote_toggle_gist', gist.gist_id)
        response = self.client.get(url)
        self.assertEqual(response.code, 405)
        response = self.client.post(url, {})
        self.assertEqual(response.code, 200)
        self.assertTrue('not_logged_in' in response.body)

        self.client.login('peterbe')
        response = self.client.post(url, {})
        self.assertEqual(response.code, 200)
        struct = json.loads(response.body)
        self.assertEqual(struct, {'points': 1})

        vote = self.db.Vote.one()
        assert vote
        self.assertEqual(vote.gist._id, gist._id)
        self.assertEqual(vote.user._id, peter._id)

        gist_points = self.db.GistPoints.one({'gist.$id': gist._id})
        self.assertEqual(gist_points.points, 1)

        assert not self.db.UserPoints.one({'user.$id': peter._id})

        user_points = self.db.UserPoints.one({'user.$id': ernst._id})
        assert user_points
        self.assertEqual(user_points.points, 1)

        # change your mind
        response = self.client.post(url, {})
        self.assertEqual(response.code, 200)
        struct = json.loads(response.body)
        self.assertEqual(struct, {'points': 0})

        gist_points = self.db.GistPoints.one({'gist.$id': gist._id})
        self.assertEqual(gist_points.points, 0)

        assert not self.db.UserPoints.one({'user.$id': peter._id})

        user_points = self.db.UserPoints.one({'user.$id': ernst._id})
        assert user_points
        self.assertEqual(user_points.points, 0)

        # change your mind again
        response = self.client.post(url, {})
        self.assertEqual(response.code, 200)
        struct = json.loads(response.body)
        self.assertEqual(struct, {'points': 1})

        gist_points = self.db.GistPoints.one()

        # log in as the author of the gist and upvote your own
        import apps.main.tests.mock_data
        apps.main.tests.mock_data.MOCK_GITHUB_USERS['ernst'] = {
          'name': 'Ernst Hemingway',
          'login': 'ernst',
        }
        self.client.login('ernst')
        assert 'Hemingway' in self.client.get('/').body

        response = self.client.post(url, {})
        self.assertEqual(response.code, 200)
        struct = json.loads(response.body)
        self.assertEqual(struct, {'points': 2})

    def test_most_loved(self):
        peter = self.db.User()
        peter.login = u'peterbe'
        peter.email = u''
        peter.company = u''
        peter.name = u'Peter'
        peter.save()

        ernst = self.db.User()
        ernst.login = u'ernst'
        ernst.email = u''
        ernst.company = u''
        ernst.name = u'Ernst'
        ernst.save()

        gist = self.db.Gist()
        gist.user = peter
        gist.gist_id = 111
        gist.created_at = u'yesterday'
        gist.files = [u'foo.py']
        gist.description = u'Testing the Atom feed'
        gist.discussion = u"""Full `markdown` description:
        function foo():
            return bar
        """
        gist.save()

        gist2 = self.db.Gist()
        gist2.user = ernst
        gist2.gist_id = 2222
        gist2.created_at = u'yesterday'
        gist2.files = [u'foo.py']
        gist2.description = u'Foo 2'
        gist2.discussion = u"Stuff"
        gist2.save()

        # suppose both people voted for gist2
        vote = self.db.Vote()
        vote.user = peter
        vote.gist = gist2
        vote.points = 1
        vote.save()
        vote = self.db.Vote()
        vote.user = ernst
        vote.gist = gist2
        vote.points = 1
        vote.save()


        gp = self.db.GistPoints()
        gp.gist = gist2
        gp.points = 2
        gp.save()

        up = self.db.UserPoints()
        up.user = ernst
        up.points = 2
        up.save()

        url = self.reverse_url('most_loved')
        response = self.client.get(url)
        self.assertEqual(response.code, 200)
        self.assertTrue(gist2.description in response.body)
        self.assertTrue('>2<' in response.body)

        self.assertTrue(gist.description not in response.body)

        ernst_url = self.reverse_url('most_loved_user', ernst.login)
        self.assertTrue(ernst_url in response.body)

        # and now a vote for gist1
        vote = self.db.Vote()
        vote.user = ernst
        vote.gist = gist
        vote.points = 1
        vote.save()

        gp = self.db.GistPoints()
        gp.gist = gist
        gp.points = 1
        gp.save()

        up = self.db.UserPoints()
        up.user = peter
        up.points = 1
        up.save()

        response = self.client.get(url)
        self.assertEqual(response.code, 200)
        self.assertTrue(gist.description in response.body)
        self.assertTrue('>1<' in response.body)

        response = self.client.get(ernst_url)
        self.assertEqual(response.code, 200)
        self.assertTrue('2 points' in response.body)
