# -*- coding: utf-8 -*-
CONTRACTOR_ADDED = u'1'
CONTRACTOR_REMOVED = u'2'
CONFIRM_NEW_EMPLOYEE = u'3'
RECOMMENDATION_ASKED = u'4'
INVOICE_VERIFICATION_PASSED = u'5'
DEPOSIT_TRANSACTION = u'6'
INVOICE_ROTTEN = u'7'
INVITATION = u'8'
FEEDBACK_SENT = u'9'
UNREAD_DIALOGS = u'10'
VERIFICATION_PERIODIC = u'11'
PASSWORD_RECOVERY = u'12'

def create_action_id(*args):
    """
    Create id for deferred notification action
    for new notification
    for remove notification
    """
    return u'-'.join([unicode(arg) for arg in args])

def get_action_name(action=u''):
    """
    Return human view action name of notification to admin
    """
    result=u''
    if len(action):
        action = action.split('-')[0]
        if action == CONTRACTOR_ADDED:
            result=u'Добавление контрагента'
        elif action == CONTRACTOR_REMOVED:
            result=u'Удаление контрагента'
        elif action == CONFIRM_NEW_EMPLOYEE:
            result=u'Подтверждение сотрудника'
        elif action == RECOMMENDATION_ASKED:
            result=u'Запрос рекомендации'
    else:
        result=u'Не определено'
    return result
