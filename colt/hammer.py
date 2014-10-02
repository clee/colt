#!/usr/bin/env python
# vim: set fileencoding=utf-8

try:
	from urllib.parse import urlparse
except ImportError:
	from urlparse import urlparse

import logging
import requests

from .utils import dictmerge


LOG = logging.getLogger(__name__)

class Hammer(object):
	def __init__(self, host):
		self.hostname = host['name']
		self.hostport = host['port']
		self.use_ssl = False
		self.cookies = []
		self.lastpath = None
		self.responses = {}
		self.response_code = -1
		self.rpm = 0
		self.session = requests.Session()

	def setSSL(self, should_use_ssl):
		self.use_ssl = should_use_ssl

	def log_status(self, status, path, new_location):
		if LOG.getEffectiveLevel() > logging.INFO:
			return

		def good():
			LOG.info("\x1B[034;1m(✓) {0}\x1B[0m response from {1}".format(status, path))

		def redir():
			LOG.info("\x1B[037;1m(→) {0}\x1B[0m redirect from {1} to {2}".format(status, path, new_location))

		def bad():
			LOG.info("\x1B[031;1m(✘) {0}\x1B[0m response from {1}".format(status, path))

		codes = {}
		for code in (200, 201, 202, 203, 204, 205, 206, 207):
			codes[code] = good
		for code in (301, 302, 303, 307):
			codes[code] = redir
		try:
			codes[status]()
		except:
			bad()

	def setRPM(self, rpm):
		self.rpm = rpm

	def request(self, method, url, body):
		response_body = ''
		u = urlparse(url)
		if self.use_ssl:
			default_scheme = 'https'
		else:
			default_scheme = 'http'
		scheme = u.scheme or default_scheme
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
			headers['Referer'] = "{0}://{1}:{2}{3}".format(scheme, self.hostname, self.hostport, self.lastpath)

		full_url = '{0}://{1}:{2}{3}'.format(scheme, hostname, port, path)
		self.session.headers.update(headers)

		if method == 'GET':
			response = self.session.request(method, full_url, params=body, allow_redirects=False)
		else:
			response = self.session.request(method, full_url, data=body, allow_redirects=False)

		self.lastpath = path

		self.status_code = response.status_code
		self.log_status(self.status_code, path, response.headers.get('location') or None)

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

