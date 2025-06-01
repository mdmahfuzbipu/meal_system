from functools import wraps
from django.core.exceptions import PermissionDenied


from functools import wraps
from django.core.exceptions import PermissionDenied


def role_required(check_func, role_name):
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if request.user.is_authenticated and check_func(request.user):
                return view_func(request, *args, **kwargs)
            raise PermissionDenied(f"Only {role_name}s can access this page.")

        return _wrapped_view

    return decorator


student_required = role_required(lambda user: user.is_student, "student")
manager_required = role_required(lambda user: user.is_manager, "manager")
admin_required = role_required(lambda user: user.is_admin, "admin")
