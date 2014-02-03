from django.core.exceptions import PermissionDenied
from django.contrib.auth.models import AnonymousUser
from django.test import RequestFactory

from libya_tally.apps.tally.views import data_entry_clerk as views
from libya_tally.libs.permissions import groups
from libya_tally.libs.tests.test_base import create_result_form, TestBase
from libya_tally.apps.tally.models.center import Center
from libya_tally.apps.tally.models.station import Station
from libya_tally.apps.tally.models.sub_constituency import SubConstituency
from libya_tally.libs.models.enums.center_type import CenterType
from libya_tally.libs.models.enums.form_state import FormState
from libya_tally.libs.models.enums.gender import Gender


def center_data(code1, code2=None, station_number=1):
    if not code2:
        code2 = code1

    return {'center_number': code1,
            'center_number_copy': code2,
            'station_number': station_number,
            'station_number_copy': station_number}


def create_center(code):
    return Center.objects.get_or_create(
        code=code,
        mahalla='1',
        name='1',
        office='1',
        region='1',
        village='1',
        center_type=CenterType.GENERAL)[0]


def create_station(center):
    sc, _ = SubConstituency.objects.get_or_create(code=1,
                                                  component_ballot=False,
                                                  field_office='1')

    return Station.objects.get_or_create(
        center=center,
        sub_constituency=sc,
        gender=Gender.MALE,
        station_number=1)


class TestDataEntryClerk(TestBase):
    def setUp(self):
        self.factory = RequestFactory()
        self._create_permission_groups()

    def _common_view_tests(self, view):
        request = self.factory.get('/')
        request.user = AnonymousUser()
        with self.assertRaises(PermissionDenied):
            view(request)
        self._create_and_login_user()
        request.user = self.user
        with self.assertRaises(PermissionDenied):
            view(request)
        self._add_user_to_group(self.user, groups.DATA_ENTRY_CLERK)
        response = view(request)
        response.render()
        self.assertIn('/accounts/logout/', response.content)
        return response

    def test_center_detail_view(self):
        response = self._common_view_tests(views.CenterDetailsView.as_view())
        self.assertContains(response, 'Double Enter Center Details')
        self.assertIn('<form id="result_form"', response.content)

    def test_center_detail_center_number_length(self):
        self._create_and_login_user()
        self._add_user_to_group(self.user, groups.DATA_ENTRY_CLERK)
        view = views.CenterDetailsView.as_view()
        data = {'center_number': '1223', 'center_number': '1223'}
        request = self.factory.post('/', data=data)
        request.user = self.user
        response = view(request)
        self.assertContains(response,
                            u'Ensure this value has at least 5 characters')

    def test_center_detail_center_not_equal(self):
        self._create_and_login_user()
        self._add_user_to_group(self.user, groups.DATA_ENTRY_CLERK)
        view = views.CenterDetailsView.as_view()
        data = center_data('12345', '12346')
        request = self.factory.post('/', data=data)
        request.user = self.user
        response = view(request)
        self.assertContains(response, 'Center Numbers do not match')

    def test_center_detail_does_not_exist(self):
        self._create_and_login_user()
        self._add_user_to_group(self.user, groups.DATA_ENTRY_CLERK)
        view = views.CenterDetailsView.as_view()
        data = center_data('12345')
        request = self.factory.post('/', data=data)
        request.user = self.user
        response = view(request)
        self.assertContains(response, 'Center Number does not exist')

    def test_center_detail_no_station(self):
        code = '12345'
        create_center(code)
        self._create_and_login_user()
        self._add_user_to_group(self.user, groups.DATA_ENTRY_CLERK)
        view = views.CenterDetailsView.as_view()
        data = center_data(code)
        request = self.factory.post('/', data=data)
        request.user = self.user
        request.session = {}
        response = view(request)
        self.assertContains(response, 'Invalid Station Number for this Center')

    def test_center_detail_redirects_to_check_center_details(self):
        code = '12345'
        station_number = 1
        center = create_center(code)
        create_station(center)
        create_result_form(form_state=FormState.DATA_ENTRY_1,
                           center=center,
                           station_number=station_number)
        self._create_and_login_user()
        self._add_user_to_group(self.user, groups.DATA_ENTRY_CLERK)
        view = views.CenterDetailsView.as_view()
        data = center_data(code, station_number=station_number)
        request = self.factory.post('/', data=data)
        request.user = self.user
        request.session = {}
        response = view(request)
        self.assertEqual(response.status_code, 302)
        self.assertIn('data-entry/check-center-details',
                      response['location'])

    def test_enter_results_has_candidates(self):
        code = '12345'
        center = create_center(code)
        create_station(center)
        result_form = create_result_form(form_state=FormState.DATA_ENTRY_1)
        self._create_and_login_user()
        self._add_user_to_group(self.user, groups.DATA_ENTRY_CLERK)
        view = views.EnterResultsView.as_view()
        data = center_data(code)
        request = self.factory.get('/', data=data)
        request.user = self.user
        request.session = {'result_form': result_form.pk}
        response = view(request)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Data Entry')