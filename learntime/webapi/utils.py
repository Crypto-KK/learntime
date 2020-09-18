def jwt_response_payload_handler(token, user=None, request=None, role=None):
    return {
        'uid': user.uid,
        'name': user.name,
        'grade': user.grade,
        'academy': user.academy,
        'clazz': user.clazz,
        'credit': user.credit,
        'sxdd_credit': user.sxdd_credit,
        'cxcy_credit': user.cxcy_credit,
        'fl_credit': user.fl_credit,
        'wt_credit': user.wt_credit,
        'xl_credit': user.xl_credit,
        'token': token,
    }
