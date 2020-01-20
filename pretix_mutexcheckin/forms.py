from django import forms
from django.utils.translation import ugettext_lazy as _
from pretix.base.forms import SettingsForm
import json
from pretix.base.models.checkin import CheckinList


class MutexCheckinSettingsForm(SettingsForm):
    mutex_checkin_lists = forms.ModelMultipleChoiceField(
        queryset=None,
        label=_("Check-in lists"),
        widget=forms.CheckboxSelectMultiple(
            attrs={"class": "scrolling-multiple-choice"}
        ),
        initial=None,
    )

    def __init__(self, *args, **kwargs):
        event = kwargs.get("obj")
        super().__init__(*args, **kwargs)
        self.fields["mutex_checkin_lists"].queryset = event.checkin_lists.all()
        self.fields["mutex_checkin_lists"].initial = json.loads(
            self.initial.pop("mutex_checkin_lists", [])
        )

    def clean_mutex_checkin_lists(self, *args, **kwargs):
        return list(
            self.cleaned_data["mutex_checkin_lists"].values_list("pk", flat=True)
        )
