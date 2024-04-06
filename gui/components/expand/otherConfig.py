from PyQt5.QtCore import QObject
from .expandTemplate import TemplateLayout
from ...util.common_methods import get_context_thread


class Layout(TemplateLayout):
    def __init__(self, parent=None, config=None):
        OtherConfig = QObject()
        configItems = [
            {
                'label': OtherConfig.tr('一键反和谐'),
                'type': 'button',
                'selection': self.fhx,
                'key': None
            },
            {
                'label': OtherConfig.tr('显示首页头图（下次启动时生效）'),
                'type': 'switch',
                'key': 'bannerVisibility'
            }
        ]

        super().__init__(parent=parent, configItems=configItems, config=config, context="OtherConfig")

    def fhx(self):
        get_context_thread(self).start_fhx()
