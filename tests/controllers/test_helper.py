from expects import *
from expects.matchers import Matcher
from unittest import TestCase

class be_successful(Matcher):
    def __init__(self):
        pass

    def _match(self, request):
        if request.status_code >= 200 and request.status_code <= 299:
            return True, ["Request was successful"]
        else:
            return False, ["Status code outside of 2xx range"]

be_successful = be_successful()

class have_in_body(Matcher):
    def __init__(self, content):
        self.content = content

    def _match(self, request):
        body = request.get_data(as_text=True)
        if self.content in body:
            return True, ["'{}' in '{}'".format(self.content, body)]
        else:
            return False, ["'{}' not in '{}'".format(self.content, body)]
