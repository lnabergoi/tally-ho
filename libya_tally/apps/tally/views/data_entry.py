from django.shortcuts import get_object_or_404, redirect
from django.views.generic import FormView

from libya_tally.apps.tally import forms
from libya_tally.apps.tally.models.result_form import ResultForm
from libya_tally.libs.permissions import groups
from libya_tally.libs.views import mixins
from libya_tally.libs.views.form_state import form_in_data_entry_state


class CenterDetailsView(mixins.GroupRequiredMixin,
                        mixins.ReverseSuccessURLMixin,
                        FormView):
    form_class = forms.DataEntryCenterDetailsForm
    group_required = groups.DATA_ENTRY_CLERK
    template_name = "tally/center_details.html"
    success_url = 'data-entry-check-center-details'

    def post(self, *args, **kwargs):
        form_class = self.get_form_class()
        form = self.get_form(form_class)

        if form.is_valid():
            return redirect(self.success_url)
        else:
            return self.form_invalid(form)


class CheckCenterDetailView(mixins.GroupRequiredMixin,
                            mixins.ReverseSuccessURLMixin,
                            FormView):
    form_class = forms.IntakeBarcodeForm
    group_required = groups.DATA_ENTRY_CLERK
    template_name = "tally/check_center_details.html"
    success_url = "result-entry"

    def get(self, *args, **kwargs):
        pk = self.request.session.get('result_form')
        result_form = get_object_or_404(ResultForm, pk=pk)
        form_in_data_entry_state(result_form)

        return self.render_to_response(
            self.get_context_data(result_form=result_form))


class EnterResultsView(mixins.GroupRequiredMixin,
                       mixins.ReverseSuccessURLMixin,
                       FormView):
    form_class = forms.IntakeBarcodeForm
    group_required = groups.DATA_ENTRY_CLERK
    template_name = "tally/check_center_details.html"
    success_url = "data-entry-clerk"

    def get(self, *args, **kwargs):
        pk = self.request.session.get('result_form')
        result_form = get_object_or_404(ResultForm, pk=pk)
        form_in_data_entry_state(result_form)
        pk = self.request.session.get('result_form')
        result_form = get_object_or_404(ResultForm, pk=pk)
        form_in_data_entry_state(result_form)

        return self.render_to_response(
            self.get_context_data(result_form=result_form))
