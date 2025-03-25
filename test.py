from pychaoxingsigner_core import *

if __name__ == '__main__':
    phone = 'this_is_your_phone_number!!!!!!!!!!'
    pwd = 'this_is_your_password!!!!!!!!'
    name = '哈基米'

    # getit urself :)
    # https://api.map.baidu.com/lbsapi/getpoint/index.html
    addr = '给我干哪来了这还是国内吗'
    lonlat = '-21.613143,64.184654'

    role = Role(phone, pwd)
    if not role.is_logged_in(): role.login()
    courses = role.get_courses()
    #print(courses)
    for course, activeId in role.iter_active(courses):
        #print(activeId)
        role.sign_location(
            course,
            activeId,
            addr,
            *(lonlat.split(',')),
            name
        )
        #break
