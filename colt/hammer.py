#!/usr/bin/env python
# vim: set fileencoding=utf-8

try:
	from urllib.parse import urlparse
except ImportError:
	from urlparse import urlparse

import logging
import requests
import sys

from .utils import dictmerge


LOG = logging.getLogger(__name__)

class BadResponse(Exception):
	pass

class Hammer(object):
	def __init__(self, host):
		self.hostname = host['name']
		self.hostport = host['port']
		self.use_ssl = False
		self.verify_ssl = True
		self.cookies = []
		self.lastpath = None
		self.responses = {}
		self.status_code = -1
		self.rpm = 0
		self.follow_redirects = True
		self.session = requests.Session()

	def setSSL(self, should_use_ssl):
		self.use_ssl = should_use_ssl

	def setVerifySSL(self, verify):
		self.verify_ssl = verify

	def setFollowRedirects(self, should_follow):
		self.follow_redirects = should_follow

	def log_status(self, status, path, new_location):
		if LOG.getEffectiveLevel() > logging.INFO:
			return

		if hasattr(sys.stdout, 'isatty') and sys.stdout.isatty():
			goodfmt = "\x1B[034;1m(✓) {0}\x1B[0m response from {1}"
			redirfmt = "\x1B[037;1m(→) {0}\x1B[0m redirect from {1} to {2}"
			badfmt = "\x1B[031;1m(✘) {0}\x1B[0m response from {1}"
		else:
			goodfmt = "(✓) {0} response from {1}"
			redirfmt = "(→) {0} redirect from {1} to {2}"
			badfmt = "(✘) {0} response from {1}"

		def good():
			LOG.info(goodfmt.format(status, path))

		def redir():
			LOG.info(redirfmt.format(status, path, new_location))

		def bad():
			LOG.error(badfmt.format(status, path))
			raise BadResponse

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
			response = self.session.request(method, full_url, params=body, allow_redirects=False, verify=self.verify_ssl)
		else:
			response = self.session.request(method, full_url, data=body, allow_redirects=False, verify=self.verify_ssl)

		self.lastpath = path

		self.status_code = response.status_code
		self.log_status(self.status_code, path, response.headers.get('location') or None)

		elapsed = int(response.elapsed.total_seconds() * 1000)
		responses = {path: { method: { self.status_code: [elapsed]}}}
		self.responses = dictmerge(self.responses, responses)

		if self.follow_redirects and \
		   self.status_code in (301, 302, 303, 307) and \
		   'location' in response.headers:
			return self.get(response.headers['location'], {})
		return response

	def get(self, url, params={}):
		return self.request('GET', url, params)

	def post(self, url, params={}):
		return self.request('POST', url, params)

	def put(self, url, params={}):
		return self.request('PUT', url, params)

	def delete(self, url, params={}):
		return self.request('DELETE', url, params)

