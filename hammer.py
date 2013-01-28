#!/usr/bin/env python
# vim: set fileencoding=utf-8

import urllib
from urlparse import urlparse
import requests
import logging

LOG = logging.getLogger(__name__)

def dictmerge(dst, src):
	for key, value in src.items():
		if not key in dst:
			dst[key] = value
			continue
		if value.__class__ is list:
			dst[key].extend(src[key])
		else:
			dst[key] = dictmerge(dst[key], src[key])
	return dst

class Hammer(object):
	def __init__(self, host):
		self.hostname = host['name']
		self.hostport = host['port']
		self.cookies = []
		self.lastpath = None
		self.responses = {}
		self.response_code = -1
		self.rpm = 0
		self.session = requests.Session()

	def setRPM(self, rpm):
		self.rpm = rpm

	def request(self, method, url, body):
		response_body = ''
		u = urlparse(url)
		scheme = u.scheme or 'http'
		hostname = u.hostname or self.hostname
		port = u.port or self.hostport
		path = u.path
		headers = {
			'User-Agent': 'colt 0.5',
			'Host': '{0}:{1}'.format(hostname, port),
			'Accept-Encoding': 'gzip'
		}
		if method == 'POST':
			headers['Content-Type'] = 'application/x-www-form-urlencoded'
		if self.lastpath:
			headers['Referer'] = "http://{0}:{1}{2}".format(self.hostname, self.hostport, self.lastpath)

		full_url = '{0}://{1}:{2}{3}'.format(scheme, hostname, port, path)
		self.session.headers.update(headers)
		if method == 'GET':
			response = self.session.request(method, full_url, params=body, allow_redirects=False)
		else:
			response = self.session.request(method, full_url, data=body, allow_redirects=False)

		self.lastpath = path
		self.status_code = response.status_code
		def good():
			LOG.info(u"\x1B[034;1m(✓) {0}\x1B[0m response from {1}".format(self.status_code, path))
		def redir():
			LOG.info(u"\x1B[037;1m(→) {0}\x1B[0m redirect from {1} to {2}".format(self.status_code, path, response.headers['location']))
		def bad():
			LOG.info(u"\x1B[031;1m(✘) {0}\x1B[0m response from {1}".format(self.status_code, path))
		codes = {}
		for code in xrange(200, 207):
			codes[code] = good
		for code in (301, 302, 303, 307):
			codes[code] = redir
		try:
			codes[self.status_code]()
		except:
			bad()

		elapsed = int(response.elapsed.total_seconds() * 1000)
		responses = {path: { method: { self.status_code: [elapsed]}}}
		self.responses = dictmerge(self.responses, responses)

		if self.status_code in (301, 302, 303, 307) and 'location' in response.headers:
			self.get(response.headers['location'], {})

	def get(self, url, params={}):
		self.request('GET', url, params)

	def post(self, url, params={}):
		self.request('POST', url, params)

	def put(self, url, params={}):
		self.request('PUT', url, params)

	def delete(self, url, params={}):
		self.request('DELETE', url, params)

	def get_shared_email(self):
		self.get('/shared/email/')

	def post_shared_email(self, params):
		self.post('/shared/email/', params)

	def get_shared_domain(self):
		self.get('/shared/domain/')

	def post_shared_domain(self, params):
		self.post('/shared/domain/', params)

	def get_shared_plan(self):
		self.get('/shared/plan/')

	def post_shared_plan(self, params):
		self.post('/shared/plan/', params)

	def get_shared_billing(self):
		self.get('/shared/billing/')

	def post_shared_billing(self, params):
		self.post('/shared/billing/', params)

