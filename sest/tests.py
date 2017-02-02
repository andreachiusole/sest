from django.test import TestCase, Client
from django.utils import timezone
from django.conf import settings

from .models import *

import uuid
from postmarker.core import PostmarkClient

POSTMARK_API_TEST = "POSTMARK_API_TEST"

postmark_client_test = PostmarkClient(token=POSTMARK_API_TEST)


class UploadView(TestCase):

    def test_upload_successful(self):
        """Use a POST http (made with the Client class from the test module) to
        test the correct upload of data to a channel, using the view `upload'.
        """

        c = Client()

        channel_id = 1234

        u = User.objects.create(nick="test", registration_time=timezone.now())
        ch = Channel.objects.create(
            user=u, id=channel_id, last_update=timezone.now(), number_fields=2)
        channel_uuid = str(ch.write_key)

        d = {'field2': 45}
        response = c.post('/{}/upload/'.format(channel_id), d,
                          HTTP_X_WRITE_API_KEY=channel_uuid)

        self.assertEqual(ch.record_set.all()[0].field_set.count(), len(d))
        self.assertEqual(response.status_code, 200)

    def test_upload_exceeds_no_fields(self):
        """Use a POST http (made with the Client class from the test module) to
        check that we are not allowed to post more fields than the max number
        available.
        """

        c = Client()

        channel_id = 1234

        u = User.objects.create(nick="test", registration_time=timezone.now())
        ch = Channel.objects.create(
            user=u, id=channel_id, last_update=timezone.now(), number_fields=2)
        channel_uuid = str(ch.write_key)

        d = {'field{}'.format(i + 1): i +
             1 for i in range(Channel.MAX_NUMBER_FIELDS + 2)}
        response = c.post('/{}/upload/'.format(channel_id), d,
                          HTTP_X_WRITE_API_KEY=channel_uuid)

        self.assertEqual(response.status_code, 406)

    def test_upload_zero_no_fields(self):
        """Use a POST http (made with the Client class from the test module) to
        make sure that user has to publish at least one field.
        """

        c = Client()

        channel_id = 1234

        u = User.objects.create(nick="test", registration_time=timezone.now())
        ch = Channel.objects.create(
            user=u, id=channel_id, last_update=timezone.now(), number_fields=2)
        channel_uuid = str(ch.write_key)

        d = {}
        response = c.post('/{}/upload/'.format(channel_id), d,
                          HTTP_X_WRITE_API_KEY=channel_uuid)

        self.assertEqual(response.status_code, 406)

    def test_upload_wrong_write_API(self):
        """Use a POST http (made with the Client class from the test module) to
        make sure that the view exits with a 400 Bad Request code in case the
        write API key provided is not the same as the one of the channel.
        """

        c = Client()

        channel_id = 1234

        u = User.objects.create(nick="test", registration_time=timezone.now())
        Channel.objects.create(
            user=u, id=channel_id, last_update=timezone.now(), number_fields=2)
        channel_uuid = uuid.uuid4()

        d = {'field2': 45}
        response = c.post('/{}/upload/'.format(channel_id), d,
                          HTTP_X_WRITE_API_KEY=channel_uuid)

        self.assertEqual(response.status_code, 400)

    def test_upload_missing_write_API(self):
        """Use a POST http (made with the Client class from the test module) to
        make sure that the view exits with a 400 Bad Request code in case the
        write API key is provided.
        """

        c = Client()

        channel_id = 1234

        u = User.objects.create(nick="test", registration_time=timezone.now())
        Channel.objects.create(
            user=u, id=channel_id, last_update=timezone.now(), number_fields=2)
        # channel_uuid = uuid.uuid4()

        d = {'field2': 45}
        response = c.post('/{}/upload/'.format(channel_id), d)
        # HTTP_X_WRITE_API_KEY=channel_uuid)

        self.assertEqual(response.status_code, 400)

    def test_upload_wrong_HTTP_request(self):
        """Use a POST http (made with the Client class from the test module) to
        make sure that the view exits with a 400 Bad Request code in case the
        write API key is provided.
        """

        c = Client()

        channel_id = 1234

        u = User.objects.create(nick="test", registration_time=timezone.now())
        Channel.objects.create(
            user=u, id=channel_id, last_update=timezone.now(), number_fields=2)
        # channel_uuid = uuid.uuid4()

        d = {'field2': 45}
        response = c.get('/{}/upload/'.format(channel_id), d)
        # HTTP_X_WRITE_API_KEY=channel_uuid)

        self.assertEqual(response.status_code, 400)


def create_testclient_user_channel():
    client = Client()
    u = User.objects.create(nick="test",
                            registration_time=timezone.now())
    ch = Channel.objects.create(user=u,
                                last_update=timezone.now(),
                                number_fields=2
                                )
    return client, u, ch


class FieldEncoding(TestCase):

    def test_fields_correct(self):
        """Create a new record and test the number and values of fields saved.
        """

        c, u, ch = create_testclient_user_channel()

        ch_id = ch.id
        ch.fieldencoding_set.create(field_no=1, encoding="float")
        ch.fieldencoding_set.create(field_no=2, encoding="float")

        channel_uuid = str(ch.write_key)

        d = {'field2': 3.141592}
        c.post('/{}/upload/'.format(ch_id), d,
               HTTP_X_WRITE_API_KEY=channel_uuid)

        # r contains the record object just created.
        r = ch.record_set.all()[0]
        self.assertEqual(r.field_set.count(), len(d))

        self.assertEqual(r.field_set.all()[0].real_value, d['field2'])

    def test_field_encoding_no_operation_defined(self):
        """Create a new record, but set a wrong encoding in the channel.

        This should never happen, since the user should choose an encoding (
        boolean, int, float, etc) from a list with pre-defined objects.
        """

        c, u, ch = create_testclient_user_channel()

        ch_id = ch.id
        ch.fieldencoding_set.create(field_no=1, encoding="float")
        # Wrong encoding set here.
        ch.fieldencoding_set.create(field_no=2, encoding="asdf")

        channel_uuid = str(ch.write_key)

        d = {'field2': 3.141592}
        c.post('/{}/upload/'.format(ch_id), d,
               HTTP_X_WRITE_API_KEY=channel_uuid)

        # r contains the record object just created.
        r = ch.record_set.all()[0]

        with self.assertRaises(ValueError):
            r.field_set.all()[0].real_value

    def test_field_encoding_wrong_value_saved(self):
        """Create a new record with a wrong value.

        This should never happen, since the values should be checked for
        consistency right before saving them in the DB.
        """

        c, u, ch = create_testclient_user_channel()

        ch_id = ch.id
        ch.fieldencoding_set.create(field_no=1, encoding="float")
        ch.fieldencoding_set.create(field_no=2, encoding="float")

        channel_uuid = str(ch.write_key)

        d = {'field2': 'asdf'}
        c.post('/{}/upload/'.format(ch_id), d,
               HTTP_X_WRITE_API_KEY=channel_uuid)

        # r contains the record object just created.
        r = ch.record_set.all()[0]

        with self.assertRaises(ValueError):
            r.field_set.all()[0].real_value


class EmailSending(TestCase):

    def t_send_correct_email(self):
        c, u, ch = create_testclient_user_channel()
        ch.notification_email = settings.DEFAULT_FROM_EMAIL


class CheckAndReactTests(TestCase):

    def t_react_failing(self):
        c, u, ch = create_testclient_user_channel()
        ch.notification_email = settings.DEFAULT_FROM_EMAIL
        pass
