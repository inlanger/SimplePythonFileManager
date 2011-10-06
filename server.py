# -*- coding: utf-8 -*-
from bottle import *
import sys, os, time, md5

app = Bottle()
full_path = os.path.abspath(os.path.dirname(sys.argv[0]))
accounts = {"test": "test", "test2": "test2"}


# Some code from https://github.com/herrerae/mia
def get_file_type(filename):
    path = request.GET.get('path')
    if not path:
        path = '/'
    TEXT_TYPE = ['doc', 'docx', 'txt', 'rtf', 'odf', 'text', 'nfo']
    AUDIO_TYPE = ['aac', 'mp3', 'wav', 'wma', 'm4p', 'flac']
    IMAGE_TYPE = ['bmp', 'eps', 'gif', 'ico', 'jpg', 'jpeg', 'png', 'psd', 'psp', 'raw', 'tga', 'tif', 'tiff', 'svg']
    VIDEO_TYPE = ['mv4', 'bup', 'mkv', 'ifo', 'flv', 'vob', '3g2', 'bik', 'xvid', 'divx', 'wmv', 'avi', '3gp', 'mp4', 'mov', '3gpp', '3gp2', 'swf', 'mpg', 'mpeg']
    COMPRESS_TYPE = ['7z', 'dmg', 'rar', 'sit', 'zip', 'bzip', 'gz', 'tar', 'ace']
    EXEC_TYPE = ['exe', 'msi', 'mse']
    SCRIPT_TYPE = ['js', 'html', 'htm', 'xhtml', 'jsp', 'asp', 'aspx', 'php', 'xml', 'css', 'py', 'bat', 'sh', 'rb', 'java']

    if os.path.isdir(full_path + path + "/" + filename):
        return "folder"
    else:
        extension = os.path.splitext(filename)[1].replace('.','')
        if extension in TEXT_TYPE:
            type_file = 'text'
        elif extension in AUDIO_TYPE:
            type_file = 'audio'
        elif extension in IMAGE_TYPE:
            type_file = 'imagen'
        elif extension in VIDEO_TYPE:
            type_file = 'video'
        elif extension in COMPRESS_TYPE:
            type_file = 'compress'
        elif extension in EXEC_TYPE:
            type_file = 'exec'
        elif extension in SCRIPT_TYPE:
            type_file = 'script'
        elif extension == 'pdf':
            type_file = 'pdf'
        else:
            type_file = 'unknow'
        return type_file

# Some code from https://github.com/herrerae/mia
def date_file(path):
    tiempo = time.gmtime(os.path.getmtime(path))
    return time.strftime("%d.%m.%Y %H:%M:%S", tiempo)

# Some code from https://github.com/herrerae/mia
def convert_bytes(path):
    bytes = float(os.path.getsize(path))
    if bytes >= 1099511627776:
        terabytes = bytes / 1099511627776
        size = '%.2f Tb' % terabytes
    elif bytes >= 1073741824:
        gigabytes = bytes / 1073741824
        size = '%.2f Gb' % gigabytes
    elif bytes >= 1048576:
        megabytes = bytes / 1048576
        size = '%.2f Mb' % megabytes
    elif bytes >= 1024:
        kilobytes = bytes / 1024
        size = '%.2f Kb' % kilobytes
    else:
        size = '%.2f Byte' % bytes
    return size

@app.post('/login')
def login():
    login = request.forms.get('login')
    password = request.forms.get('password')
    if not login or not password:
        redirect("/?error=empty")
    if login in accounts:
        if accounts[login] == password:
            hash = md5.new()
            hash.update(password)
            response.set_cookie("login", login)
            response.set_cookie("password", hash.hexdigest())
            print "OK"
            redirect("/")
        else:
            print "Неправильный пароль!"
            redirect("/?error=badpass")
    else:
        print "Нет такого логина"
        redirect("/?error=badlogin")
    return ""

@app.route('/logout')
def logout():
    response.set_cookie("login", "")
    response.set_cookie("password", "")
    redirect("/")

@app.route('/img/:filename')
def img_static(filename):
    return static_file(filename, root=full_path+'/views/static/img/')

@app.route('/img/view')
def view_img_static():
    filename = request.GET.get('path')
    return static_file(filename, root=full_path)

@app.route('/img/icons/:filename')
def icons_static(filename):
    return static_file(filename, root=full_path+'/views/static/img/icons/')

@app.route('/img/fancybox/:filename')
def fancybox_static(filename):
    return static_file(filename, root=full_path+'/views/static/img/fancybox/')

@app.route('/js/:filename')
def js_static(filename):
    return static_file(filename, root=full_path+'/views/static/js/')

@app.route('/css/:filename')
def css_static(filename):
    return static_file(filename, root=full_path+'/views/static/css/')

@app.route('/')
@view('list')
def list():
    for header in response.headers:
        print header
    path = request.GET.get('path')
    if not path:
        path = '/'
    if path != '/':
        array = path.split("/")
        toplevel = path.replace("/" + array[path.count("/")], "")
        if not toplevel:
            toplevel  = '/'
    else:
        toplevel = False
    dirList = os.listdir(full_path + path)
    dirList.sort()
    output = []
    for item in dirList:
        if item == 'server.py' or item == 'bottle.py' or item == 'bottle.pyc' or item == '.folderinfo' or item == 'views':
            pass
        else:
            if not toplevel:
                filepath = path + item
            else:
                filepath = path + "/" + item
            output.append({"name": item, "path": filepath, "type": get_file_type(item), "date": date_file(full_path + filepath), "size": convert_bytes(full_path + filepath)})
    data = {"title": "Список файлов " + path, "full_path": full_path, "path": path, "list": dirList, "toplevel": toplevel, "output": output, "login": request.get_cookie("login"), "password": request.get_cookie("password"), "error": request.GET.get('error')}
    return dict(data=data)

@app.route('/download')
def download():
    filename = request.GET.get('path')
    return static_file(filename, root=full_path, download=filename)

debug(True)
run(app, host='localhost', port=8080, reloader=True)