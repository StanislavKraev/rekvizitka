class StateChangeException(Exception):
    pass

def make_fsm(initial=None, field_name='_fsm_field'):
    def _set_state(cls, new_state):
        field = getattr(cls, field_name)
        if new_state == field:
            return
        method = cls._fsm_dir.get((field, new_state))
        if not method:
            raise StateChangeException("Incorrect transition: %s -> %s" % (field, new_state))
        setattr(cls, field_name, new_state)
        method(cls)

    def _change_state(cls, new_state, *args, **kwargs):
        field = getattr(cls, field_name)
        if new_state == field:
            return
        method = cls._fsm_dir.get((field, new_state))
        if not method:
            raise StateChangeException("Incorrect transition: %s -> %s" % (field, new_state))
        setattr(cls, field_name, new_state)
        try:
            method(cls, *args, **kwargs)
        except Exception, ex:
            setattr(cls, field_name, field)
            raise ex

    def _get_state(cls):
        return getattr(cls, field_name)

    def inner_wrapper(cls):
        fsm_state = property(_get_state, _set_state)
        setattr(cls, 'fsm_state', fsm_state)
        setattr(cls, 'change_fsm_state', _change_state)
        setattr(cls, field_name, initial)

        fsm_dir = {}
        setattr(cls, '_fsm_dir', fsm_dir)

        for member in dir(cls):
            member_obj = getattr(cls, member)
            if hasattr(member_obj, '__call__') and hasattr(member_obj, '_fsm_method'):
                transition = getattr(member_obj, '_fsm_method')
                fsm_dir[transition] = member_obj

        return cls

    return inner_wrapper

def transition(source='', target=''):
    def inner_wrapper(func):
        if not hasattr(func, '_fsm_method'):
            setattr(func, '_fsm_method', (source, target))
        return func
    return inner_wrapper
