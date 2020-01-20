from django.dispatch import receiver
from django.urls import resolve, reverse
from django.utils.translation import ugettext_lazy as _
from pretix.base.signals import checkin_created
from pretix.control.signals import nav_event_settings
import json
from pretix.base.models.checkin import Checkin

@receiver(nav_event_settings, dispatch_uid="mutex_checkin_settings")
def mutexcheckin_settings(sender, request, **kwargs):
    url = resolve(request.path_info)
    return [
        {
            "label": _("Pretix Mutex Checkin"),
            "url": reverse(
                "plugins:pretix_mutexcheckin:settings",
                kwargs={
                    "event": request.event.slug,
                    "organizer": request.organizer.slug,
                },
            ),
            "active": url.namespace == "plugins:pretix_mutexcheckin"
            and url.url_name == "settings",
        }
    ]


@receiver(checkin_created, dispatch_uid="mutex_checkin_checkin_created")
def mutex_checkin_checkin_created(sender, checkin, **kwargs):
    mutex_checkins = json.loads(sender.settings.get("mutex_checkin_lists", "[]"))
    if checkin.list.pk in mutex_checkins:
        checkins_to_delete = Checkin.objects.filter(list__in=mutex_checkins).filter(position=checkin.position).exclude(list=checkin.list)
        for chk in checkins_to_delete:
            chk.delete()
            chk.position.order.log_action('pretix.event.checkin.reverted', data={
                'position': chk.position.id,
                'positionid': chk.position.positionid,
                'list': chk.list.pk,
                'web': False
            })
            chk.position.order.touch()
