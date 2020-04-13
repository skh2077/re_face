from functions.dependency_imports import *

def refund_paidrecord(paidrecord,paid_type,origin_paid,refund_processor,refund_reason,refund_amount,receipt_id):
    if int(paidrecord.paid) < int(refund_amount):
        return 0
    if paid_type == 1: #crm
        return 1
    elif paid_type == 3: #kiosk
        if receipt_id:
            if receipt_id.paid_status ==20 and receipt_id.paid_path == 'kiosk':
                return 1    
        return 0
    elif paid_type == 5: #url
        bootpay = BootpayApi(BOOTPAY_APPLICATION_ID,BOOTPAY_PRIVATE_KEY)
        result = bootpay.get_access_token()
        if int(result.get('status')) == 200:
            cancel_result = bootpay.cancel(receipt_id.receipt_id,refund_amount,refund_processor.name,refund_reason)
            if int(cancel_result.get('status')) == 200:
                return 1

    return 0

def verify_paidrecord(receipt_id):  
    bootpay = BootpayApi(BOOTPAY_APPLICATION_ID,BOOTPAY_PRIVATE_KEY)
    result = bootpay.get_access_token()
    if int(result.get('status')) == 200:
        verify_result = bootpay.verify(origin_paid.receipt_id)
        if int(verify_result.get('status')) == 200:
            return verity_result['data']['receipt_url']


def gen_request_code(request, extra=None):
    request_code = random.choices(
        string.ascii_letters + string.digits, k=7)
    request['request_code'] = request_code
    request.update(extra)
    return request


def center_fran(request):
    name_list = ['center_code', 'franchise_code']
    result = {}
    if type(request) in [dict, QueryDict]:
        for name in name_list:
            if request.get(name):
                result[name] = request.get(name)
    else:
        for name in name_list:
            try:
                if request.__getattribute__(name):
                    result[name] = request.__getattribute__(
                        name).__getattribute__(name)
            except AttributeError:
                pass
    return result


def generate_key(length, url=False):
    randomurl = ''.join(random.choices(
        string.ascii_letters + string.digits, k=length))

    if url == True:
        baseurl = 'https://ref.autogym24.com/#'
        randomurl = baseurl+randomurl
    return randomurl


def Entry_check(membership, center_code):
    entry = False
    course_type = []
    try:
        iterator = iter(membership)
    except TypeError:
        membership = [membership]
    for memattr in membership:
        course = memattr.course_code
        if course.center_code == center_code or (course.franchise_code != None and
                                                 course.franchise_code == center_code.franchise_code):
            if memattr.remains > 0:
                entry = True
                if schedule_compare(course.schedule_code, datetime.now()):
                    entry = True
        course_type.append(course.course_type)
    if entry:
        return 1, course_type
    else:
        return 0, course_type


def gen_coord(raw_address):
    geocode_url = 'https://maps.googleapis.com/maps/api/geocode/json'
    address = ''
    initial = 0
    for spli in raw_address.split(' '):
        if initial != 0:
            address = address+','
        else:
            initial = initial + 1
        address = address+spli
    url = geocode_url+'?'+'address='+address+'&key='+GOOGLE_API_KEY
    result = requests.get(url)
    res = result.json()['results'][0]['geometry']['location']
    return {"latitude": float(res['lat']), "longitude": float(res['lng'])}


def schedule_compare(schedule, today):
    if schedule is not None:
        if today.weekday() in schedule.week_select:
            if schedule.start_time < today.time():
                if schedule.end_time > today.time():
                    return 1
    return 0


def range_compare(numeric_a, numeric_b):
    if not numeric_a.isempty and numeric_a.lower and numeric_a.upper:
        set_a = set(range(numeric_a.lower, numeric_a.upper))
    else:
        set_a = set()
    if not numeric_b.isempty and numeric_b.lower and numeric_b.upper:
        set_b = set(range(numeric_b.lower, numeric_b.upper))
    else:
        set_b = set()
    dif_ab = list(set_a-set_b)
    dif_ba = list(set_b-set_a)
    return dif_ab, dif_ba
