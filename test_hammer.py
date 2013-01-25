#!/usr/bin/env python
# vim: set fileencoding=utf-8

from hammer import Hammer, dictmerge
import json
import logging


def run():
	h = Hammer({'name': 'localhost', 'port': 8080})
	h.get_shared_email()
	token = h.session.cookies.get('ndn.signup_auth_token')
	params = {
		'csrf_token': token,
		'email': 'clee@x.org',
		'password': 'blexcutiscgradisco',
		'password_confirm': 'blexcutiscgradisco',
		'secret_question': 'In what city does your nearest sibling live?',
		'secret_answer': 'vancouver'
	}
	h.post_shared_email(params)
	params = {
		'csrf_token': token,
		'domain': '',
		'special_tld': '',
		'duration': '1',
		'action': 'skip'
	}
	h.post_shared_domain(params)
	params = {
		'csrf_token': token,
		'service_type_id': '225'
	}
	h.post_shared_plan(params)
	return h.responses

if __name__ == '__main__':
	logging.basicConfig(level=logging.INFO)
	responses = {}

	for i in xrange(10):
		responses = dictmerge(responses, run())
	open('r.json', 'w').write(json.dumps(responses))
