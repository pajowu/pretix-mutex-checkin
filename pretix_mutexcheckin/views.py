from django.urls import reverse
from pretix.control.views.event import EventSettingsFormView, EventSettingsViewMixin
from pretix.base.models.event import Event
from .forms import MutexCheckinSettingsForm

from pretix.presale.style import regenerate_css
from django.contrib import messages


class SettingsView(EventSettingsViewMixin, EventSettingsFormView):
    model = Event
    permission = "can_change_settings"
    form_class = MutexCheckinSettingsForm
    template_name = "pretix_mutexcheckin/settings.html"

    def get_success_url(self, **kwargs):
        return reverse(
            "plugins:pretix_mutexcheckin:settings",
            kwargs={
                "organizer": self.request.event.organizer.slug,
                "event": self.request.event.slug,
            },
        )
