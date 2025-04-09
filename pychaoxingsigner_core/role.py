from Crypto.Cipher import AES
from Crypto.Util.Padding import pad
from http.cookies import SimpleCookie
import requests, base64, json, os,time

from .logger import logger, new_logging_levels
from .configs.api import *
from .configs.params import *
from .datatypes import *


def javascript_now():
    return int(time.time() * 1000)


class Cookie:
    
    cookie_dir = os.path.join('.', 'cookies')
    
    def __init__(self, cookie_str: str, username: str, do_cache: bool = True):
        self.cookie_str = cookie_str
        self.cookie = SimpleCookie(self.cookie_str)
        self.username = username
        if do_cache:
            if not os.path.exists(self.cookie_dir):
                os.makedirs(self.cookie_dir)
            self.path = os.path.join(self.cookie_dir, 'cookie_' + base64.urlsafe_b64encode(self.username.encode('utf-8')).decode())
            if os.path.exists(self.path):
                if input('User "%s" already exists. Overwrite? [y/N] ' % self.username).strip().lower() != 'y':
                    return
            with open(self.path, 'w', encoding = 'utf-8') as f:
                f.write(self.cookie_str)
    
    def __getitem__(self, *args, **kwargs):
        return self.cookie.__getitem__(*args, **kwargs)
    
    def __str__(self):
        return 'Cookie %s owned by user %s' % (repr(self.cookie_str), repr(self.username))
    
    def __repr__(self):
        return self.__str__()

    @classmethod
    def load_user(cls, username: str):
        path = os.path.join(cls.cookie_dir, 'cookie_' + base64.urlsafe_b64encode(username.encode('utf-8')).decode())
        if not os.path.exists(path):
            return None
        with open(path, 'r', encoding = 'utf-8') as f:
            return cls(f.read(), username, do_cache = False)
    
    @classmethod
    def load_file(cls, path: str, username: str):
        if not os.path.exists(path):
            return None
        with open(path, 'r', encoding = 'utf-8') as f:
            return cls(f.read(), username, do_cache = False)


class NotAuthorizedException(Exception):
    pass


class Role:
    def _enc(self, data: bytes):
        cipher = AES.new(key = API.login_transfer_key, mode = AES.MODE_CBC, iv = API.login_transfer_key)
        ct = cipher.encrypt(pad(data, 16, style = 'pkcs7'))
        ct = base64.b64encode(ct)
        return ct
    
    def __init__(self, phone: str, pwd: str, cookie: [Cookie, None] = None):
        self.phone = phone
        self.pwd = pwd
        self.name = None
        self.last_response = None
        if cookie is None:
            self.cookie = Cookie.load_user(phone)
            if self.cookie is not None:
                logger.info('Using cached cookie for "%s".', self.phone)
        else:
            self.cookie = cookie
    
    def is_logged_in(self):
        return self.cookie is not None
    
    def check_is_logged_in(self, action):
        if not self.is_logged_in():
            logger.critical(f"{action}: You need to log in to perform this action.")
            raise NotAuthorizedException(f"{action}: You need to log in to perform this action.")
    
    def login(self):
        uname = self._enc(self.phone.encode('utf-8'))
        password = self._enc(self.pwd.encode('utf-8'))
        res = requests.post(
            url = API.login.url,
            data = API.login.data(uname, password),
            headers = API.login.headers()
        )
        self.last_response = res.text
        if res.status_code != 200:
            logger.error('login: Failed with status code %d.', res.status_code)
            return False
        try:
            data = json.loads(res.text)
            self.last_response = data
        except json.decoder.JSONDecodeError:
            logger.error('login: JSON decode error: %s', res.text)
            return False
        if 'status' not in data:
            logger.error('login: Malformed response: %s', res.text)
            return False
        elif not data['status']:
            logger.error('login: %s', data['msg2'] if 'msg2' in data else res.text)
            return False
        else:
            logger.info('login: Welcome, %s.', self.phone)
            cookie_str = res.headers['Set-Cookie'].replace('HttpOnly, ', '')
            cookie_dict = SimpleCookie(cookie_str)
            if '_uid' not in cookie_dict or \
               '_d'   not in cookie_dict or \
               'UID'  not in cookie_dict or \
               'uf'   not in cookie_dict or \
               'fid'  not in cookie_dict or \
               'vc2'  not in cookie_dict or \
               'vc3'  not in cookie_dict:
                logger.warn('login: A probably malformed cookie detected.')
            else:
                cookie_str = '; '.join(f"{k}={v.value}" for k, v in cookie_dict.items()) + ';'
            self.cookie = Cookie(cookie_str, self.phone)
        return True
    
    def get_courses(self):
        self.check_is_logged_in('get_courses')
        res = requests.post(
            url = API.course_list.url,
            data = API.course_list.data(),
            headers = API.course_list.headers(self.cookie.cookie_str)
        )
        self.last_response = res.text
        if res.status_code != 200:
            logger.error('get_courses: Failed with status code %d.', res.status_code)
            return []
        html = res.text
        token = 'id="course_'
        l = len(token)
        i = html.find(token)
        course_list = []
        if i == -1:
            logger.warn('get_courses: No courses found by token search.')
        else:
            while i >= 0:
                i1 = html.find('_', i + l)
                i2 = html.find('"', i + l)
                if i1 == -1 or i2 == -1 or i1 >= i2 - 1 or i + l == i1:
                    logger.error("get_courses: Malformed courseId or classId.")
                    return []
                courseId, classId = html[i+l: i1], html[i1+1: i2]
                course_list.append(Course(classId = classId, courseId = courseId))
                i = html.find(token, i + l)
        return course_list
    
    def iter_active(self, courses):
        self.check_is_logged_in('iter_active')
        for course in courses:
            res = requests.get(
                url = API.active_list.url,
                params = API.active_list.params(course.courseId, course.classId),
                headers = API.active_list.headers(self.cookie.cookie_str)
            )
            self.last_response = res.text
            if res.status_code != 200:
                logger.error('iter_active: %s failed with status code %d.', course, res.status_code)
                continue
            try:
                data = json.loads(res.text)
                self.last_response = data
            except json.decoder.JSONDecodeError:
                logger.error('iter_active: %s JSON decode error: %s', course, res.text)
                continue
            try:
                activeList = data['data']['activeList']
                if len(activeList) > 0 and \
                   activeList[0]['status'] == 1:
                    if javascript_now() - activeList[0]['startTime'] < IGNORE_ACTIVE_THRESHOLD:
                        logger.info("Active event: %s", activeList[0]['nameOne'])
                        activeId = activeList[0]['id']
                        yield course, activeId
            except (KeyError, TypeError):
                logger.error('%s Malformed response: %s', course, data)
                continue
    
    def pre_sign(self, course, activeId):
        self.check_is_logged_in('pre_sign')
        res = requests.get(
            url = API.pre_sign.url,
            params = API.pre_sign.params(course.courseId, course.classId, activeId, self.cookie['_uid'].value),
            headers = API.pre_sign.headers(self.cookie.cookie_str)
        )
        if res.status_code != 200:
            logger.error('pre_sign: Failed with status code %d.', res.status_code)
            return
        logger.log(new_logging_levels.SUCCESS, "pre_sign: Done.")
        
        res = requests.get(
            url = API.pre_sign_analysis.url,
            params = API.pre_sign_analysis.params(activeId),
            headers = API.pre_sign_analysis.headers(self.cookie.cookie_str)
        )
        self.last_response = res.text
        if res.status_code != 200:
            logger.warn('pre_sign: Analysis failed with status code %d.', res.status_code)
            return
        token1 = "code='+'"
        l1 = len(token1)
        token2 = "'"
        i = res.text.find(token1)
        j = res.text.find(token2, i+l1)
        if i == -1 or j == -1 or j == i+l1:
            return
        code = res.text[i+l1:j]
        
        res = requests.get(
            url = API.pre_sign_analysis2.url,
            params = API.pre_sign_analysis2.params(code),
            headers = API.pre_sign_analysis.headers(self.cookie.cookie_str)
        )
        self.last_response = res.text
        if res.status_code != 200:
            logger.warn('pre_sign: Analysis2 failed with status code %d.', res.status_code)
            return
        logger.info('pre_sign: Analysis2 returned %s', res.text)
    
    def sign_location(self, course, activeId, address, lon, lat, name = None):
        self.check_is_logged_in('sign_location')
        if name is None:
            name = self.name
        if name is None:
            logger.critical("sign_location: Name must be specified.")
            raise ValueError("sign_location: Name must be specified.")
        self.pre_sign(course, activeId)
        res = requests.get(
            url = API.sign_location.url,
            params = API.sign_location.params(name, address, activeId, self.cookie['_uid'].value, lon, lat, self.cookie['fid'].value),
            headers = API.sign_location.headers(self.cookie.cookie_str)
        )
        self.last_response = res.text
        if res.status_code != 200:
            logger.error('sign_location: Failed with status code %d.', res.status_code)
            return
        if res.text == 'success':
            logger.log(new_logging_levels.SUCCESS, 'sign_location: success')
        else:
            logger.error('sign_location: %s', res.text)

    def __str__(self):
        return 'User %s, %s' % (self.phone, 'logged in' if self.is_logged_in() else 'not logged in')
    
    def __repr__(self):
        return self.__str__()
