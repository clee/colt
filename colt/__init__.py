#!/usr/bin/env python

"""
colt HTTP load generation utility
=================================

colt is a load generator built on top of
requests <http://python-requests.org>.

Here's an example of how to use it:

    >>> import colt
    >>> h = colt.Hammer({'name': 'httpbin.org', 'port': 80})
    >>> for i in range(5): 
    ...     h.get("/redirect/3")
    >>> h.responses
    {'/redirect/1': {'GET': {302: [269, 257, 320, 256, 260]}}, '/get': {'GET': {200: [253, 252, 252, 273, 279]}}, '/redirect/3': {'GET': {302: [551, 259, 290, 255, 291]}}, '/redirect/2': {'GET': {302: [311, 271, 285, 258, 267]}}}

The dictionary returned at the end contains the response times (in
milliseconds) of each URL that was fetched during the session, grouped
by URL, request method, and status code.

:copyright: (c) 2013 by Chris Lee <clee@mg8.org>
:license: MIT, see LICENSE for more details
"""

__title__ = 'colt'
__version__ = '0.5.0'
__build__ = 0x000500
__author__ = 'Chris Lee <clee@mg8.org>'
__license__ = 'MIT'
__copyright__ = 'Copyright 2012 Chris Lee <clee@mg8.org>'

from . import utils
from hammer import Hammer
