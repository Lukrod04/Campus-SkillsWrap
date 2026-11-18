from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from .models import Review, Session, Skill


class SkillSwapTests(TestCase):
    def setUp(self):
        self.owner = User.objects.create_user('teacher', password='Example-password-472')
        self.learner = User.objects.create_user('learner', password='Example-password-472')
        self.skill = Skill.objects.create(owner=self.owner, title='Python basics', category='Coding', description='Learn together.')

    def test_search_title_category_and_empty_results(self):
        for query in ['PYTHON', 'coding', '  Python  ']:
            response = self.client.get('/', {'q': query})
            self.assertContains(response, 'Python basics')
        self.assertContains(self.client.get('/', {'q': 'guitar'}), 'No skills found')

    def test_pages_render(self):
        for url in ['/', '/register/', '/accounts/login/', reverse('skill_detail', args=[self.skill.pk])]:
            self.assertEqual(self.client.get(url).status_code, 200)
        self.client.force_login(self.owner)
        for url in ['/dashboard/', '/skills/new/', reverse('skill_edit', args=[self.skill.pk]), reverse('skill_delete', args=[self.skill.pk])]:
            self.assertEqual(self.client.get(url).status_code, 200)

    def test_ownership_and_post_only_actions(self):
        self.client.force_login(self.learner)
        self.assertEqual(self.client.post(reverse('skill_edit', args=[self.skill.pk]), {'title': 'Stolen'}).status_code, 404)
        self.assertEqual(self.client.post(reverse('skill_delete', args=[self.skill.pk])).status_code, 404)
        self.assertEqual(self.client.get(reverse('request_session', args=[self.skill.pk])).status_code, 405)
        self.client.logout()
        self.assertEqual(self.client.get('/skills/new/').status_code, 302)

    def test_session_review_workflow(self):
        detail = reverse('skill_detail', args=[self.skill.pk])
        self.client.force_login(self.learner)
        self.client.post(detail, {'rating': 5, 'comment': 'Premature'})
        self.assertFalse(Review.objects.exists())
        self.client.post(reverse('request_session', args=[self.skill.pk]))
        self.client.post(reverse('request_session', args=[self.skill.pk]))
        self.assertEqual(Session.objects.count(), 1)
        session = Session.objects.get()
        complete = reverse('complete_session', args=[session.pk])
        self.assertEqual(self.client.post(complete).status_code, 404)
        self.client.post(detail, {'rating': 5, 'comment': 'Still premature'})
        self.assertFalse(Review.objects.exists())
        self.client.force_login(self.owner)
        self.client.post(complete)
        self.client.post(detail, {'rating': 5, 'comment': 'Self review'})
        self.assertFalse(Review.objects.exists())
        self.client.force_login(self.learner)
        for rating in ['0', '6', 'abc']:
            self.assertEqual(self.client.post(detail, {'rating': rating, 'comment': 'Invalid'}).status_code, 200)
        self.assertFalse(Review.objects.exists())
        self.client.post(detail, {'rating': 5, 'comment': 'Great lesson'})
        self.client.post(detail, {'rating': 4, 'comment': 'Updated review'})
        self.assertEqual(Review.objects.count(), 1)
        self.assertEqual(Review.objects.get().rating, 4)
        self.assertContains(self.client.get('/'), '4.0 / 5')

    def test_create_and_delete(self):
        self.client.force_login(self.owner)
        self.client.post('/skills/new/', {'title': 'Guitar', 'category': 'Music', 'description': 'Learn chords'})
        skill = Skill.objects.get(title='Guitar')
        self.assertEqual(skill.owner, self.owner)
        self.client.post(reverse('skill_delete', args=[skill.pk]))
        self.assertFalse(Skill.objects.filter(pk=skill.pk).exists())

    def test_csrf_required(self):
        from django.test import Client
        client = Client(enforce_csrf_checks=True)
        client.force_login(self.learner)
        self.assertEqual(client.post(reverse('request_session', args=[self.skill.pk])).status_code, 403)

    def test_category_filter_combines_with_search(self):
        Skill.objects.create(owner=self.owner, title='Python art', category='Art', description='Sketching')
        response = self.client.get('/', {'q': 'Python', 'category': 'Coding'})
        self.assertContains(response, 'Python basics')
        self.assertNotContains(response, 'Python art')

    def test_meeting_details_and_confirmation(self):
        self.client.force_login(self.learner)
        self.client.post(reverse('request_session', args=[self.skill.pk]),
                         {'preferred_time': 'Friday 3pm Central', 'meeting_place': 'Campus library'})
        session = Session.objects.get()
        self.assertEqual(session.meeting_place, 'Campus library')
        confirm = reverse('confirm_session', args=[session.pk])
        self.assertEqual(self.client.post(confirm).status_code, 404)
        self.client.force_login(self.owner)
        self.assertEqual(self.client.get(confirm).status_code, 405)
        self.client.post(confirm)
        session.refresh_from_db()
        self.assertTrue(session.confirmed)
        self.assertFalse(session.completed)
        self.assertContains(self.client.get('/dashboard/'), 'Campus library')
        self.client.force_login(self.learner)
        self.assertContains(self.client.get('/dashboard/'), 'Meeting confirmed')
