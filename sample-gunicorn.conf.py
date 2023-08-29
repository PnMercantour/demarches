wsgi_app = "run:server"

# logging
accesslog = "log/access.log"
errorlog = "log/error.log"

# daemon = True
user = None
group = None

workers = 4
backlog = 64

# bind = "unix:apache2.sock"
bind = ["0.0.0.0:8050"]
