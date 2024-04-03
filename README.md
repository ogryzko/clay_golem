# Clay golem
### Introduction
The simplest possible web interface for remote control
and automation of work with experimental stands of 
the O-125 laboratory. It can be launched both in the 
cloud and on a local machine, for example Raspberry Pi.
It does not have any protection during data transfer
or authorization mechanisms, so it is assumed that 
you are running the server STRICTLY on a laboratory 
VPN network. Tested only on Linux.

#### How it works
The central element of the entire system is the redis 
database, which stores all the current data about the 
state of the experimental setup, as well as data about 
the current state of the backend processes.

The frontend is implemented using the Flask framework, the bootstrap
library and the gunicorn wsgi server. gunicorn manages
the flask server processes, which draws a web page 
using bootstrap primitives. The frontend is completely
stateless, it simply renders the control interface and
the state of the devices using data from the database.
Due to this, you can run as many flask processes as you
like in parallel.

The backend is implemented using the
redis-queue framework. When a user clicks on a button
on a web page, the javascript creates a request to the
server, the server processes it and creates a task in
the redis-queue. The server itself does not have any 
access to the hardware; it only creates tasks and waits
for them to be completed. Redis-queue workers perform
tasks from the queue and directly interact with the 
equipment. They are handled through 
systemd services, and can work without web-page launched.

#### Frontend
We are using AJAX polling from user browser to server 
to get updates from db without manual reloading web-page.
It is old method but very simple. May be in future we will
migrate to web-sockets technology.
All js scripts stored in flaskr/templates folder. They are very simple

#### Backend


### Installation
1. install python3, pip, venv;  install redis
2. sudo mkdir /opt/clay
3. sudo chown -R <your_user>:<your_user> /opt/clay
4. clone project from github to /opt/clay so it will be in /opt/clay/clay_golem
5. create new venv inside /opt/clay/clay_golem and activate it
6. install requirements via pip -r
7. create or copy config.py file with hardware configuration
8. manually create systemd services for 
   1. web-server with gunicorn wsgi
   2. rq-scheduler
   3. rq-workers (via template)
9. allow selected app port in firewall if there is such

### Configuration
All hardware configuration, database, all app paths, 
network addresses stores in default flask config in same format
#### Logic of hardware handling
#### Logic of creating and handling rq tasks
#### Config file 

### How to start
All console commands related to app can be run with flask click wrapper to store 
unified config file and app context in all operations related to app
1. go to app folder
2. run ```flask --app flaskr init-db``` to create or clean existing db
3. run ```flask --app flaskr start-tasks``` to create rq-tasks corresponded to config
4. run ```flask --app flaskr start-workers``` 
5. run ```flask --app flaskr start-app``` 

### How to stop
1. go to app folder
2. run ```flask --app flaskr clear-queue``` to remove 
jobs of all types from rq queue
3. run ```flask --app flaskr kill-all-workers``` to stop all workers from systemd
4. run ```flask --app flaskr stop-app```

### Uninstall
1. manually remove systemd services
2. manually remove app directory
3. manually remove venv
