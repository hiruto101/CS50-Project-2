from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("accounts/login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("new_list", views.new_list, name="new_list"),
    path("my_list", views.my_list, name="my_list"),
    path("mywatchlist", views.mywatchlist, name="mywatchlist"),
    path("placeBid/<int:id>", views.placeBid, name="placeBid"),
     path("listing/<int:id>", views.view_list, name="view_list"),
    path("removewatchlist/<int:id>", views.removewatchlist, name="removewatchlist"),
    path("addwatchlist/<int:id>", views.addwatchlist, name="addwatchlist")
]
