import logging
import time


from django.utils import timezone

class APILogMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # logger = logging.getLogger('django')
        # logger.debug(f"API Request - Method: {request.method}, Path: {request.path}, Body: {request.body}")
        #
        # response = self.get_response(request)

        timestamp = timezone.now()
        # Record the start time
        start_time = time.time()

        method = request.method
        path = request.path
        remote_addr = request.META.get('REMOTE_ADDR', '')
        user_agent = request.META.get('HTTP_USER_AGENT', '')

        log_msg = f"API Request - Timestamp: {timestamp}, Method: {method}, Path: {path},Body: {request.body}, Remote Addr: {remote_addr}, User Agent: {user_agent}"
        logger = logging.getLogger('api_calls')
        logger.info(log_msg)

        response = self.get_response(request)
        # Record the end time
        end_time = time.time()

        # Calculate the execution time
        execution_time = end_time - start_time

        # Add the execution time to the response headers (optional)
        response["X-Execution-Time"] = str(execution_time)

        # Print the execution time to the console (or log it)
        print(f"API Execution Time: {execution_time} seconds")

        return response