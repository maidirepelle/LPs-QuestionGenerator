import os
import random
import re
from typing import Dict, List
try:
    from hashlib import md5
except ImportError:
    from md5 import md5

import tornado.httpserver
import tornado.ioloop
import tornado.web
from tornado.escape import xhtml_unescape
from tornado.options import define, options

define("port", default=5000, type=int)

questions_file = os.path.join(os.path.dirname(__file__), 'LPsQuestions.txt')
questions: Dict[str, str] = {}

with open(questions_file, 'r', encoding='utf-8') as questions_input:
    for line in questions_input.readlines():
        questions[md5(line.encode('utf-8')).hexdigest()] = line

def fill_line(question):
    return question

class MainHandler(tornado.web.RequestHandler):
    def get(self, question_hash=None):
        if not question_hash:
            question_hash = random.choice(list(questions.keys()))
        elif question_hash not in questions:
            raise tornado.web.HTTPError(404)

        question=questions[question_hash]
        real_question_groups = re.search(r"#([\D\d]+)#(.+)", question)

        leadership_principle=real_question_groups.group(1)
        real_question=real_question_groups.group(2)
        
        question = fill_line(real_question)
        self.output_question(question, leadership_principle,question_hash)

    def output_question(self, question, leadership_principle,question_hash):
        self.set_header('X-question-Hash', question_hash)
        self.render('index.html', question=question, leadership_principle=leadership_principle,question_hash=question_hash)

settings = {}

application = tornado.web.Application([
    (r'/', MainHandler),
    (r'/([a-z0-9]+)', MainHandler),
], **settings)

if __name__ == '__main__':
    tornado.options.parse_command_line()
    http_server = tornado.httpserver.HTTPServer(application)
    http_server.listen(os.environ.get("PORT", 5000))
    tornado.ioloop.IOLoop.instance().start()