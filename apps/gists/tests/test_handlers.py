import json
from apps.main.tests.test_handlers import HandlersTestCase
class GistsHandlersTestCase(HandlersTestCase):


    def test_commenting_on_gist(self):
        assert not self.db.Comment.find().count()
        peter = self.db.User()
        peter.login = u'peterbe'
        peter.email = u''
        peter.company = u''
        peter.name = u'Peter'
        peter.save()

        gist1 = self.db.Gist()
        gist1.user = peter
        gist1.gist_id = 1234
        gist1.created_at = u'yesterday'
        gist1.files = [u'foo.py']
        gist1.description = u'Testing the Atom feed'
        gist1.discussion = u"""Full `markdown` description:
        function foo():
            return bar

[peterbe](http://www.peterbe.com)
        """
        gist1.save()

        comment_url = self.reverse_url('comments', 1234)
        response = self.client.get(comment_url)
        assert response.code == 200
        struct = json.loads(response.body)
        self.assertEqual(struct, {'comments':[]})

        post_data = {
          'comment':'I love `cheese`!',
          'file': 'foo.py',
        }
        response = self.client.post(comment_url, post_data)
        self.assertEqual(response.code, 403)

        self.client.login('peterbe')

        response = self.client.post(comment_url, post_data)
        self.assertEqual(response.code, 302)
        self.assertTrue(response.headers['Location'].startswith(
          self.reverse_url('view_gist', 1234)))

        assert self.db.Comment.find().count()
        comment = self.db.Comment.one()
        self.assertEqual(comment.user.login, 'peterbe')
        self.assertEqual(comment.comment, post_data['comment'])
        self.assertEqual(comment.file, post_data['file'])

        response = self.client.get(comment_url)
        assert response.code == 200
        struct = json.loads(response.body)
        self.assertEqual(len(struct['comments']), 1)
        first = struct['comments'][0]

        self.assertTrue(first.get('ago'))
        self.assertTrue('<code>cheese</code>' in first['comment'])
        self.assertTrue(first.get('user'))
        self.assertTrue(first.get('id'))

    def test_preview_markdown(self):
        url = self.reverse_url('preview_markdown')
        post_data = {'text':
            "Test\nfoo `and` <script>alert('xsss')</script>"}
        response = self.client.post(url, post_data)
        assert response.code == 200
        struct = json.loads(response.body)
        assert struct['html']
        self.assertTrue('<code>and</code>' in struct['html'])
        self.assertTrue(
          "&lt;script&gt;alert('xsss')&lt;/script&gt;" \
           in struct['html'])
