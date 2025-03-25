from collections import namedtuple
import time

ApiParams = namedtuple('ApiParams', [
    'url',
    'method',    # for reference
    'headers',
    'params',
    'data'
])

def javascript_now():
    return int(time.time() * 1000)

class API:

    login_transfer_key = b'u2oh6Vu^HWe4_AES'

    login = ApiParams(
        url = 'https://passport2.chaoxing.com/fanyalogin',
        method = 'POST',
        headers = lambda: {
            'Content-Type': 'application/x-www-form-urlencoded',
            'Referer': 'https://passport2.chaoxing.com/login?fid=&newversion=true&refer=https%3A%2F%2Fi.chaoxing.com',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:136.0) Gecko/20100101 Firefox/136.0'
        },
        params = lambda: '',
        data = lambda uname, password: {
            'fid':               '-1',
            'uname':             uname,
            'password':          password,
            'refer':             'https://i.chaoxing.com',
            't':                 'true',
            'forbidotherlogin':  '0',
            'validate':          '',
            'doubleFactorLogin': '0',
            'independentId':     '0',
            'independentNameId': '0'
        }
    )
    
    course_list = ApiParams(
        url = 'https://mooc1-1.chaoxing.com/visit/courselistdata',
        method = 'POST',
        headers = lambda cookie: {
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8;',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:136.0) Gecko/20100101 Firefox/136.0',
            'Cookie': cookie
        },
        params = lambda: '',
        data = lambda: {
            'courseType':       1,
            'courseFolderId':   0,
            'courseFolderSize': 0
        }
    )
    
    active_list = ApiParams(
        url = 'https://mobilelearn.chaoxing.com/v2/apis/active/student/activelist',
        method = 'GET',
        headers = lambda cookie: {
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8;',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:136.0) Gecko/20100101 Firefox/136.0',
            'Cookie': cookie
        },
        params = lambda courseId, classId: f'fid=0&courseId={courseId}&classId={classId}&_={javascript_now()}',
        data = None
    )
    
    sign_location = ApiParams(
        url = 'https://mobilelearn.chaoxing.com/pptSign/stuSignajax',
        method = 'GET',
        headers = lambda cookie: {
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8;',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:136.0) Gecko/20100101 Firefox/136.0',
            'Cookie': cookie
        },
        params = lambda name, address, activeId, uid, lon, lat, fid: f'name={name}&address={address}&activeId={activeId}&uid={uid}&clientip=&longitude={lon}&latitude={lat}&fid={fid}&appType=15&ifTiJiao=1',
        data = None
    )
    
    pre_sign = ApiParams(
        url = 'https://mobilelearn.chaoxing.com/newsign/preSign',
        method = 'GET',
        headers = lambda cookie: {
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8;',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:136.0) Gecko/20100101 Firefox/136.0',
            'Cookie': cookie
        },
        params = lambda courseId, classId, activeId, uid: f'courseId={courseId}&classId={classId}&activePrimaryId={activeId}&general=1&sys=1&ls=1&appType=15&tid=&uid={uid}&ut=s',
        data = None
    )
    
    pre_sign_analysis = ApiParams(
        url = 'https://mobilelearn.chaoxing.com/pptSign/analysis',
        method = 'GET',
        headers = lambda cookie: {
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8;',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:136.0) Gecko/20100101 Firefox/136.0',
            'Cookie': cookie
        },
        params = lambda activeId: f'vs=1&DB_STRATEGY=RANDOM&aid={activeId}',
        data = None
    )
    
    pre_sign_analysis2 = ApiParams(
        url = 'https://mobilelearn.chaoxing.com/pptSign/analysis2',
        method = 'GET',
        headers = lambda cookie: {
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8;',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:136.0) Gecko/20100101 Firefox/136.0',
            'Cookie': cookie
        },
        params = lambda code: f'DB_STRATEGY=RANDOM&code={code}',
        data = None
    )
