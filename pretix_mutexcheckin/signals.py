from django.dispatch import receiver
from django.urls import resolve, reverse
from django.utils.translation import ugettext_lazy as _
from pretix.base.signals import checkin_created
from pretix.control.signals import nav_event_settings
import json
from pretix.base.models.checkin import Checkin
from pretix.base.signals import event_copy_data

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

@receiver(signal=event_copy_data, dispatch_uid="pages_copy_data")
def event_copy_data_receiver(sender, other, checkin_list_map=None, **kwargs):
    if checkin_list_map:
        mutex_checkins_old = json.loads(other.settings.get("mutex_checkin_lists", "[]"))
        mutex_checkins_new = list(filter(None, (checkin_list_map.get(x) for x in mutex_checkins_old)))
        mutex_checkins_new_pk = [x.pk for x in mutex_checkins_new]
        sender.settings.set("mutex_checkin_lists", json.dumps(mutex_checkins_new_pk))
