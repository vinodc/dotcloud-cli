import urllib2
import httplib
import socket
import json
import sys
import os

from .auth import BasicAuth, OAuth2Auth
from .response import *
from .errors import RESTAPIError, AuthenticationNotConfigured
from ..packages.ssl_match_hostname import match_hostname

try:
    import ssl
except ImportError:
    pass

class RESTClient(object):
    def __init__(self, endpoint='https://rest.dotcloud.com/1', debug=False):
        self.endpoint = endpoint
        self.authenticator = None
        self.trace_id = None
        self.trace = None
        self.debug = debug

        if 'ssl' in sys.modules:
            urllib2.install_opener(urllib2.build_opener(VerifiedHTTPSHandler()))

    def build_url(self, path):
        if path.startswith('/'):
            return self.endpoint + path
        else:
            return path

    def get(self, path):
        url = self.build_url(path)
        req = urllib2.Request(url)
        return self.request(req)

    def post(self, path, payload={}):
        url = self.build_url(path)
        data = json.dumps(payload)
        req = urllib2.Request(url, data, {'Content-Type': 'application/json'})
        return self.request(req)

    def put(self, path, payload={}):
        url = self.build_url(path)
        data = json.dumps(payload)
        req = urllib2.Request(url, data, {'Content-Type': 'application/json'})
        req.get_method = lambda: 'PUT'
        return self.request(req)

    def delete(self, path):
        url = self.build_url(path)
        req = urllib2.Request(url)
        req.get_method = lambda: 'DELETE'
        return self.request(req)

    def patch(self, path, payload={}):
        url = self.build_url(path)
        data = json.dumps(payload)
        req = urllib2.Request(url, data, {'Content-Type': 'application/json'})
        req.get_method = lambda: 'PATCH'
        return self.request(req)

    def request(self, req):
        if not self.authenticator:
            raise AuthenticationNotConfigured
        self.authenticator.authenticate(req)
        req.add_header('Accept', 'application/json')
        if self.trace_id:
            req.add_header('X-DotCloud-TraceID', self.trace_id)
        if self.debug:
            print >>sys.stderr, '### {method} {url} data=|{data}|'.format(
                method  = req.get_method(),
                url     = req.get_full_url(),
                data    = req.get_data()
            )

        ssl_verification_retry = True
        while ssl_verification_retry:
            ssl_verification_retry = False
            try:
                res = urllib2.urlopen(req)
                if res and self.debug:
                    print >>sys.stderr, '### {code}'.format(code=res.code)
                self.trace_id = res.headers.get('X-DotCloud-TraceID')
                if self.trace:
                    self.trace(self.trace_id)
                return self.make_response(res)
            except urllib2.HTTPError, e:
                if e.code == 401 and self.authenticator.retriable:
                    if self.authenticator.prepare_retry():
                        return self.request(req)
                return self.make_response(e)
            except urllib2.URLError, e:
                import pdb; pdb.set_trace()
                if 'ssl' in sys.modules and isinstance(e.reason, ssl.SSLError):
                    if self.debug:
                        print >> sys.stderr, '### %s' % e.reason.strerror
                    urllib2.install_opener(urllib2.build_opener(urllib2.HTTPSHandler()))
                    ssl_verification_retry = True
                else:
                    raise

    def make_response(self, res):
        if res.headers['Content-Type'] == 'application/json':
            data = json.loads(res.read())
        elif res.code == 204:
            return None
        else:
            raise RESTAPIError(code=500,
                               desc='Unsupported Media type: {0}'.format(res.headers['Content-Type']))
        if res.code >= 400:
            raise RESTAPIError(code=res.code, desc=data['error']['description'])
        return BaseResponse.create(res=res, data=data)

class VerifiedHTTPSConnection(httplib.HTTPSConnection):
    def __init__(self, *args, **kwargs):
        self.ca_certs = get_data_file_path('ca_certs.pem')
        httplib.HTTPSConnection.__init__(self, *args, **kwargs)

    def connect(self):
        sock = socket.create_connection((self.host, self.port),
                                        self.timeout)
        if self._tunnel_host:
            self.sock = sock
            self._tunnel()

        self.sock = ssl.wrap_socket(sock, self.key_file, self.cert_file,
                                    cert_reqs=ssl.CERT_REQUIRED,
                                    ca_certs=self.ca_certs)

        if self.ca_certs:
            match_hostname(self.sock.getpeercert(), self.host)

class VerifiedHTTPSHandler(urllib2.HTTPSHandler):
    def __init__(self, verified_http_class=VerifiedHTTPSConnection):
        self.verified_http_class = verified_http_class
        urllib2.HTTPSHandler.__init__(self)

    def https_open(self, req):
        return self.do_open(self.verified_http_class, req)

def get_data_file_path(file_path):
    path = os.path.join('data', *(file_path.split('/')))
    d = os.path.dirname(sys.modules[__package__].__file__)
    return os.path.join(d, path)
