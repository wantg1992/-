import pymongo

conn = pymongo.MongoClient('localhost', 27017)
db = conn.Capf

users = db.users
users.remove()

notifications = db.notifications
notifications.remove()

applications = db.applications
applications.remove()

grades = db.grades
grades.remove()

disobediences = db.disobediences
disobediences.remove()

user_init={ "name":"WanTG",
            "id":"12345678",
            "password":"123",
            "priority":"5",
	    "team":"team_2",
	    "subTeam":"subTeam_2",
	    "class":"class_5",
            "email":"wan@qq.com",
            "phone":"13826412345",
        }
users.insert(user_init)

notification_init = {"title":"Safe_Meeting",
		     "type":"notice",
		     "name":"WanTG",
		     "date":"2015-6-1 3:00 pm",
                     "content":"bla..bla..bla.....",
                    }
notifications.insert(notification_init)

notification2_init = {"title":"Study_Communication",
		     "type":"task",
		     "name":"WanTG",
		     "date":"2015-5-1 3:00 pm",
                     "content":"bla..bla..bla.....",
                    }
notifications.insert(notification2_init)

application = { "title":"For a rest",
		"startTime":"2015-6-1",
		"endTime":"2015-6-2",
		"reason":"bla..bla...",
		"status":"allowed",
                "id":"12345678",
		"name":"WanTG",
            }
applications.insert(application)

grade = { "id":"12345678",
	  "name":"WanTG",
	  "run100":"8s",
	  "run3000":"12min50s",
	  "run5000":"21min30s",
	  "pullUp":"12",
	  "parallelBars":"20",
	  "sitUp":"60",
	  "pushUp":"80",
	  "date":"2015-6-1",
        }
grades.insert(grade)

disobedience = {"id":"12345678",
		"name":"WanTG",
		"reason":"do not wake up on time",
    		"date":"2015-6-1",
                }
disobediences.insert(disobedience)

