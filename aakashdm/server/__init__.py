from flask import Flask

from aakashdm import PROG
from aakashdm.server.routes import router

server = Flask(PROG, static_folder="server/static", template_folder="server/templates")
server.register_blueprint(router)
