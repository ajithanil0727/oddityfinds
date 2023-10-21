from django.urls import path
from . import views
from django.contrib.auth.views import LogoutView, PasswordResetView, PasswordResetDoneView, PasswordResetConfirmView, PasswordResetCompleteView


urlpatterns = [
    path('', views.home, name= 'home'),
    path('user_view', views.user_view, name= 'user_view'),
    path('signup', views.signup, name= 'signup'),
    path('adminlogin', views.adminlogin, name= 'adminlogin'),
    path('usermanage', views.usermanage, name= 'usermanage'),
    path('productmanage', views.productmanage, name= 'productmanage'),
    path('signout', LogoutView.as_view(next_page='home'), name= 'signout'),
    # path('adduser',views.adduser, name= 'adduser'),
    path('edituser/<int:id>/',views.edituser, name= 'edituser'),
    path('editproduct/<int:id>/',views.editproduct, name= 'editproduct'),
    path('deleteuser/<int:id>/',views.deleteuser, name = 'deleteuser'),
    path('addproduct', views.addproduct, name= 'addproduct'),
    path('singleproduct/<int:id>/', views.singleproduct, name= 'singleproduct'),
    path('addcategory', views.addcategory, name= 'addcategory'),
    path('addcoupon', views.addcoupon, name= 'addcoupon'),
    path('editcategory/<int:id>/', views.editcategory, name= 'editcategory'),
    path('deleteproduct/<int:id>/', views.deleteproduct, name= 'deleteproduct'),
    path('deletecategory/<int:id>/', views.deletecategory, name= 'deletecategory'),
    path('dashboard', views.dashboard, name= 'dashboard'),
    path('categorymanage', views.categorymanage, name= 'categorymanage'),
    path('couponmanage', views.couponmanage, name= 'couponmanage'),
    path('editoffer/<int:id>/', views.editoffer, name= 'editoffer'),
    path('userprofile/<int:id>/', views.userprofile, name= 'userprofile'),
    path('filterby/<int:id>/', views.filterby, name= 'filterby'),
    path('addtocart/<int:id>/' , views.addtocart, name= 'addtocart'),
    path('cart', views.cart, name= 'cart'),
    path('removefromcart/<int:id>/', views.removefromcart, name= 'removefromcart'), 
    path('addaddress', views.addaddress, name= 'addaddress'),
    path('viewaddress', views.viewaddress, name= 'viewaddress'),
    path('editaddress/<int:id>/', views.editaddress, name= 'editaddress'),
    path('deleteaddress/<int:id>/', views.deleteaddress, name= 'deleteaddress'),
    path('buy/<int:id>/', views.buy, name= 'buy'),
    # path('verify_otp', views.verify_otp, name= 'verify_otp'),
    path('minsortview', views.minsortview, name= 'minsortview'),
    path('maxsortview', views.maxsortview, name= 'maxsortview'),
    path('addquantity/<int:id>/', views.addquantity, name= 'addquantity'),
    path('minusquantity/<int:id>/', views.minusquantity, name= 'minusquantity'),
    path('ordersucess/<int:id>/', views.ordersucess, name= 'ordersucess'),
    path('ordermanage',views.ordermanage, name= 'ordermanage'),
    path('myorder',views.myorder, name= 'myorder'),
    path('cancelorder/<int:id>/', views.cancelorder, name= 'cancelorder'),
    path('changepassword/<int:id>/' ,views.changepassword, name= 'changepassword'),
    path('stockmanage', views.stockmanage, name= 'stockmanage'),
    path('mark_order_delivered/<int:id>/', views.mark_order_delivered, name= 'mark_order_delivered'),
    path('returnorder/<int:id>/', views.returnorder, name= 'returnorder'),
    path('wallet', views.wallet, name= 'wallet'),
    path('addoffer', views.addoffer, name= 'addoffer'),
    path('offermanage', views.offermanage, name= 'offermanage'),
    path('adminorderitemdetail/<int:id>/', views.adminorderitemdetail, name= 'adminorderitemdetail'),
    path('coupons', views.coupons, name= 'coupons'),
    path('vieworderitem/<int:id>/', views.vieworderitem, name= 'vieworderitem'),
    path('deletecoupon/<int:id>/', views.deletecoupon, name= 'deletecoupon'),
    path('deleteoffer/<int:id>/', views.deleteoffer, name= 'deleteoffer'),
    path('reset_password' , PasswordResetView.as_view(), name= 'reset_password'),
    path('reset_password_sent' , PasswordResetDoneView.as_view(), name= 'password_reset_done'),
    path('reset/<uidb64>/<token>/' , PasswordResetConfirmView.as_view(), name= 'password_reset_confirm'),
    path('reset_password_complete' , PasswordResetCompleteView.as_view(), name= 'password_reset_complete'),
]