from pikos.live.models.base_model import BaseModel


class MemoryModel(BaseModel):

    def _TRANSFORMS_default(self):
        return {
            'RSS': 1./(1024**2),
            'VMS': 1./(1024**2),
            }

    def _UNITS_default(self):
        return {
            'RSS': 'MB',
            'VMS': 'MB',
            }
