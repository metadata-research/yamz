from flask import redirect, url_for, flash, request
from flask_login import current_user
from flask_admin.contrib import sqla as flask_sqla
from flask_admin import expose
from flask_admin import AdminIndexView


class AdminModelView(flask_sqla.ModelView):
    def is_accessible(self):
        return current_user.is_authenticated and current_user.is_administrator

    def inaccessible_callback(self, name, **kwargs):
        # redirect to login page if user doesn't have access
        return redirect(url_for("login", next=request.url))


class AppAdminIndexView(AdminIndexView):
    def is_accessible(self):
        return current_user.is_authenticated and current_user.is_administrator

    def inaccessible_callback(self, name, **kwargs):
        # redirect to login page if user doesn't have access
        return redirect(url_for("auth.login", next=request.url))

    @expose("/")
    def index(self):
        if not current_user.is_authenticated and current_user.is_administrator:
            return redirect(url_for("auth.login"))
        return super(AppAdminIndexView, self).index()
