function handler(event) {
  var request = event.request;
  var headers = request.headers;
  var uri = request.uri;

  // Add custom security headers
  headers['x-frame-options'] = { value: 'DENY' };
  headers['x-content-type-options'] = { value: 'nosniff' };
  headers['x-xss-protection'] = { value: '1; mode=block' };

  // Normalize URI
  if (uri.endsWith('/')) {
    request.uri = uri + 'index.html';
  } else if (!uri.includes('.')) {
    request.uri = uri + '/index.html';
  }

  return request;
}
