import app.utils as utils
from expects import *
from unittest import TestCase
from werkzeug.datastructures import MultiDict


class TestUtils(TestCase):
    def test_form_to_dict(self):
        form = MultiDict([
            ('foo', 'bar'), ('foo', 'baz'), ('bar[sub]', 'bit'),
        ])

        d_form = utils.form_to_dict(form)
        expect(d_form["foo"]).to(equal(["bar", "baz"]))
        expect(d_form["bar"]).to(equal({"sub": "bit"}))
