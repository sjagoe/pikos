def get_model_for_profile(profile):
    if not hasattr(get_model_for_profile, "_pikos_model_cache"):
        from pikos.live.models.memory_model import MemoryModel
        cache = {
            "memory": MemoryModel,
            }
        get_model_for_profile._pikos_model_cache = cache
    return get_model_for_profile._pikos_model_cache.get(profile.lower())


def get_view_for_profile(profile):
    if not hasattr(get_view_for_profile, "_pikos_model_cache"):
        from pikos.live.ui.memory_view import MemoryView
        cache = {
            "memory": MemoryView,
            }
        get_view_for_profile._pikos_view_cache = cache
    return get_view_for_profile._pikos_view_cache.get(profile.lower())
