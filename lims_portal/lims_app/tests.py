from unittest.mock import patch

from django.core.cache import cache
from django.test import RequestFactory, TestCase
from django.urls import reverse

from .models import scholarList
from .views import send_private_message


class PrivateMessageCooldownTests(TestCase):
    def setUp(self):
        cache.clear()
        self.factory = RequestFactory()

    @patch('lims_app.views.send_mail')
    def test_private_message_blocks_back_to_back_sends_to_same_student(self, mocked_send_mail):
        request_data = {
            'sender_name': 'Tester',
            'sender_email': 'tester@example.com',
            'message': 'Hi there',
            'targetScholar': 'Tesla',
        }

        first_request = self.factory.post('/send-private-message/', data=request_data)
        first_response = send_private_message(first_request)

        second_request = self.factory.post('/send-private-message/', data=request_data)
        second_response = send_private_message(second_request)

        self.assertEqual(first_response.status_code, 200)
        self.assertEqual(second_response.status_code, 429)
        self.assertEqual(mocked_send_mail.call_count, 1)


class ScholarDetailPageTests(TestCase):
    def test_detail_page_renders_shareable_scholar_modal(self):
        scholar = scholarList.objects.create(
            name='Ada Lovelace',
            description='First programmer vibes',
            section='Tesla',
            graduation_year=2026,
        )

        response = self.client.get(reverse('scholar_detail', args=[scholar.pk]))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Copy Link')
        self.assertContains(response, 'Public Comment')
        self.assertContains(response, 'Private Message')
        self.assertContains(response, scholar.name)
