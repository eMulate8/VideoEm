import logging
import json

logger = logging.getLogger('django')


class RequestLoggingMiddleware:
    """
    Middleware to log detailed information about incoming requests and responses.
    Logs request method, path, IP, headers, and body (for POST/PUT requests).
    Also logs the response status code.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):

        request_log = {
            'method': request.method,
            'path': request.get_full_path(),
            'ip': request.META.get('REMOTE_ADDR', ''),
            'headers': {key: value for key, value in request.META.items() if key.startswith('HTTP_')},
        }

        if request.method in ['POST', 'PUT']:
            try:

                if request.content_type == 'application/json':
                    request_body = json.loads(request.body.decode('utf-8'))

                    sensitive_fields = ['password', 'token', 'authorization']

                    if isinstance(request_body, dict):
                        for field in sensitive_fields:
                            if field in request_body:
                                request_body[field] = '***REDACTED***'

                    request_log['body'] = request_body
                else:
                    request_log['body'] = request.body[:200]
            except Exception as e:
                request_log['body'] = f'Error parsing body: {str(e)}'

        response = self.get_response(request)

        response_log = {
            'status_code': response.status_code,
            'path': request.get_full_path(),
        }

        if hasattr(response, 'content'):
            response_log['body'] = response.content[:200]

        logger.info(f"Response Log: {response.status_code} for {request.get_full_path()}")

        return response