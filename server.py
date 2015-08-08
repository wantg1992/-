import tornado.web
import tornado.ioloop
import tornado.httpserver
import tornado.options
import os.path
import pymongo

from tornado.options import define, options
define('port', default=8000, help="run on the given port", type=int)

class Application(tornado.web.Application):
    def __init__(self):
        handlers = [
            (r'/', LoginHandler),
            (r'/register', RegisterHandler),
            (r'/index', IndexHandler),
            (r'/members', MembersHandler),
            (r'/notification', NotificationHandler),
            (r'/application', ApplicationHandler),
            (r'/task', TaskHandler),
            (r'/query', QueryHandler),
            (r'/logout', LogoutHandler),
            (r'/user/(\w+)', UserHandler),
            (r'/noticeEdit', NoticeEditHandler),
        ]
        settings = dict(
            template_path=os.path.join(os.path.dirname(__file__), "templates"),
            static_path=os.path.join(os.path.dirname(__file__), "static"),
            ui_modules={'Notification':NotificationModule,
                        'Grade':GradeModule,
                        'Disobedience':DisobedienceModule,
                        },
        )
        conn = pymongo.MongoClient("localhost", 27017)
        self.db = conn['Capf']
        tornado.web.Application.__init__(self, handlers, **settings)

class LoginHandler(tornado.web.RequestHandler):
    def get(self):
        self.render(
            "login.html",
        )
    def post(self):
        coll = self.application.db.users
        id = self.get_argument('id',None)
        password = self.get_argument('password', None)
        user = coll.find_one({'id':id, 'password': password})
        if user:
            self.set_cookie('userName', user['name'])
            self.redirect('/index')
        else:
            self.redirect('/')
            
class LogoutHandler(tornado.web.RequestHandler):
    def get(self):
        self.redirect("/")
        
class UserHandler(tornado.web.RequestHandler):
    def get(self, userName):
        users = self.application.db.users
        user = users.find_one({"name":userName})
        self.render(
            "user.html", cookiesName=userName,personal=user,
        )
class RegisterHandler(tornado.web.RequestHandler):
    def get(self):
        self.render(
            "register.html",
        )
    def post(self):
        user_fields = ['id','name', 'password','priority',\
                       'team','subTeam','class','email','phone']
        coll = self.application.db.users
        user = dict()
        for key in user_fields:
            user[key] = self.get_argument(key, None)
        find_user = coll.find_one({"id":user['id']})
        if find_user:
            self.redirect('/register')
        else:
            coll.insert(user)
            self.set_cookie('userName', user['name'])
            self.redirect("/")

class IndexHandler(tornado.web.RequestHandler):
    def get(self):
        name=self.get_cookie('userName')
        if name == None:
            self.redirect('/')
            self.render('login.html')
        coll = self.application.db.notifications
        notifications=coll.find()
        self.render(
            "index.html",
            cookiesName=name,
            notifications = notifications.sort("date",pymongo.DESCENDING),
        )

class MembersHandler(tornado.web.RequestHandler):
    def get(self):
        name=self.get_cookie('userName')
        coll = self.application.db.users
        members = coll.find()
        self.render('members.html', cookiesName=name, members=members)

class NotificationHandler(tornado.web.RequestHandler):
    def get(self):
        name=self.get_cookie('userName')
        coll = self.application.db.notifications
        notifications = coll.find()
        self.render('notification.html',
                    cookiesName=name,
                    notifications=notifications)
        
class NotificationModule(tornado.web.UIModule):
    def render(self, notification):
        return self.render_string('modules/notificationModule.html',
                                  notification=notification)

class ApplicationHandler(tornado.web.RequestHandler):
    def get(self):
        name=self.get_cookie('userName')
        self.render("application.html",cookiesName=name)
    def post(self):
        name=self.get_cookie('userName')
        application_fields = ['title','startTime', 'endTime','name','id','reason',]
        coll = self.application.db.applications
        application = dict()
        for key in application_fields:
            application[key] = self.get_argument(key, None)
        application['status'] = "Undeal"
        coll.insert(application)
        self.set_cookie('userName', name)
        self.redirect("/index")
        
class NoticeEditHandler(tornado.web.RequestHandler):
    def get(self):
        name=self.get_cookie('userName')
        self.render("noticeEdit.html",cookiesName=name)
    def post(self):
        name=self.get_cookie('userName')
        notice_fields = ['title','type', 'name','date','content',]
        coll = self.application.db.notifications
        notice = dict()
        for key in notice_fields:
            notice[key] = self.get_argument(key, None)
        coll.insert(notice)
        self.set_cookie('userName', name)
        self.redirect("/index")
        
class TaskHandler(tornado.web.RequestHandler):
     def get(self):
         name=self.get_cookie('userName')
         coll = self.application.db.notifications
         notifications = coll.find({"type":"task"})
         self.render('task.html',
                     cookiesName=name,
                     notifications=notifications.sort("date",pymongo.DESCENDING),)
         
class QueryHandler(tornado.web.RequestHandler):
    def get(self):
        name=self.get_cookie('userName')
        personal = dict()
        grades = []
        disobediences = []
        personal['queryFlag'] = 'false'
        self.render("query.html",
                    cookiesName=name,
                    personal=personal,
                    grades=grades,
                    disobediences=disobediences,)
    def post(self):
        name=self.get_cookie('userName')
        id = self.get_argument("id", None)
        personalFlag = self.get_argument("personal", None)
        disobedienceFlag = self.get_argument("disobediences", None)
        gradeFlag = self.get_argument("grades",None)
        
        users = self.application.db.users
        grades = self.application.db.grades
        disobediences = self.application.db.disobediences
        
        personal = dict()
        grade = []
        disobedience = []
        personal['queryFlag'] = 'false'
        
        user = users.find_one({"name":name})
        if user['id'] == id:
            if personalFlag != 'false':
                personal = user
                personal['queryFlag'] = "true"
            if gradeFlag != 'false':
                grades = grades.find({"id":id})
            if disobedienceFlag != 'false':
                disobediences = disobediences.find({"id":id})
            self.render("query.html",
                        cookiesName=name,
                        personal=personal,
                        grades=grades,
                        disobediences=disobediences,)
        elif user['priority'] >= 3:
            if personalFlag != 'false':
                personal = users.find_one({"id":id})
                personal['queryFlag'] = "true"
            if gradeFlag != 'false':
                grades = grades.find({"id":id})
            if disobedienceFlag != 'false':
                disobediences = disobediences.find({"id":id})
            self.render("query.html",
                        cookiesName=name,
                        personal=personal,
                        grades=grades,
                        disobediences=disobediences,)

class GradeModule(tornado.web.UIModule):
    def render(self, grade):
        return self.render_string('modules/gradeModule.html',
                                  grade=grade)
    
class DisobedienceModule(tornado.web.UIModule):
    def render(self, disobedience):
        return self.render_string('modules/disobedienceModule.html',
                                  disobedience=disobedience)
    
if __name__=="__main__":
    tornado.options.parse_command_line()
    http_server = tornado.httpserver.HTTPServer(Application())
    http_server.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()

        
