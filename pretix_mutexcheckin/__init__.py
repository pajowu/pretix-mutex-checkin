from django.utils.translation import ugettext_lazy
try:
    from pretix.base.plugins import PluginConfig
except ImportError:
    raise RuntimeError("Please use pretix 2.7 or above to run this plugin!")


class PluginApp(PluginConfig):
    name = 'pretix_mutexcheckin'
    verbose_name = 'Pretix Mutex Checkin'

    class PretixPluginMeta:
        name = ugettext_lazy('Pretix Mutex Checkin')
        author = 'Karl Engelhardt'
        description = ugettext_lazy('Select checkin-lists where a checkin to one of them will check customers out of the other ones.')
        visible = True
        version = '1.0.0'
        compatibility = "pretix>=3.6.0"

    def ready(self):
        from . import signals  # NOQA


default_app_config = 'pretix_mutexcheckin.PluginApp'
