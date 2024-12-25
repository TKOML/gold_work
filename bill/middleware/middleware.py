from django.utils.deprecation import MiddlewareMixin
from django.shortcuts import redirect


class MiddleWare(MiddlewareMixin):
    def process_request(self, request):
        if request.path_info in ["/bill/login", "/bill/register"]:
            return
        info_dict = request.session.get("info")
        if info_dict:
            return
        return redirect('/bill/login')