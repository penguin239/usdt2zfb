from django.utils.deprecation import MiddlewareMixin
from django.shortcuts import redirect


class checkLogin(MiddlewareMixin):
    def process_request(self, request):
        path = request.path_info
        not_check_list = [
            'login', '/login', '/login/',
            'logout', '/logout', '/logout'
        ]
        if path in not_check_list:
            return None

        user_info = request.session.get('cookie')
        if not user_info:
            return redirect('/login/')

    def process_response(self, request, response):
        return response
