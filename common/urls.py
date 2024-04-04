from django.urls import path
from .views import (
    ActiveAPIView, ActivePostAPIView, AllUsersAPIView, CreateCommentAPIView, CreateJobAPIView, CreateMessageAPIView, CreatePaymentAPIView, CreateProductAPIView,
    CreateProductCommentAPIView, EditProfileImageAPIView, GetUnreadNumberNotice, JobAPIView, MonthPaymentPIView, NotJobAPIView,
    NotPostAPIView, OneWeekPaymentPIView, PasswordResetConfirmView, PasswordResetView, PostAPIView, PostDetailAPIView, RegisterAPIView, LoginAPIView,
    SearchJobAPIView, SearchProductAPIView, SendVerificationToken, TwoWeeksPaymentPIView, UserAPIView, LogoutAPIView, EditProfileAPIView, 
    EditPasswordAPIView, VerificationToken, ViewCommentAPIView, ViewItemAPIView, ViewJobAPIView, ViewJobItemAPIView, 
    ViewMessageAPIView, MessageAPIView, ViewProductCommentAPIView, ViewpostAPIView
)

urlpatterns = [
    path('register', RegisterAPIView.as_view()),
    path('login', LoginAPIView.as_view()),
    path('user', UserAPIView.as_view()),
    path('logout', LogoutAPIView.as_view()),
    path('editprofile', EditProfileAPIView.as_view()),
    path('editphoto', EditProfileImageAPIView.as_view()),
    path('editpassword', EditPasswordAPIView.as_view()),
    path('users', AllUsersAPIView.as_view()),
    path('users/<str:pk>/', AllUsersAPIView.as_view()),
    # product
    path('product/create', CreateProductAPIView.as_view(), name='create-product'),
    path('product', PostAPIView.as_view()),
    path('product/<str:pk>/', PostAPIView.as_view()),
    # path('product/detail', PostDetailAPIView.as_view()),
    path('product/detail/<int:id>/', PostDetailAPIView.as_view()),
    path('search/create', SearchProductAPIView.as_view()),
    path('view/post/create', ViewpostAPIView.as_view()),
    path('view/post', ViewItemAPIView.as_view()),
    # job
    path('job/create', CreateJobAPIView.as_view(), name='create-job'),
    path('job', JobAPIView.as_view()),
    path('job/<str:pk>/', JobAPIView.as_view()),
    path('job/search/create', SearchJobAPIView.as_view()),
    path('view/job/create', ViewJobAPIView.as_view()),
    path('view/job', ViewJobItemAPIView.as_view()),
    # not login
    path('not/product', NotPostAPIView.as_view()),
    path('not/product/<str:pk>/', NotPostAPIView.as_view()),
    path('not/job', NotJobAPIView.as_view()),
    path('not/job/<str:pk>/', NotJobAPIView.as_view()),
    # phone verification
    path('sendtoken', SendVerificationToken.as_view()),
    path('verifytoken', VerificationToken.as_view()),

    path('forgetpassword', PasswordResetView.as_view(), name='password-reset'),
    path('reset-password/<int:user_id>/<str:token>/',
         PasswordResetConfirmView.as_view(), name='password-reset-confirm'),

    path('usercomment/create', CreateCommentAPIView.as_view()),
    path('usercomment', ViewCommentAPIView.as_view()),
    path('usercomment/<str:pk>/', ViewCommentAPIView.as_view()),

    path('productcomment/create', CreateProductCommentAPIView.as_view()),
    path('productcomment', ViewProductCommentAPIView.as_view()),
    path('productcomment/<str:pk>/', ViewProductCommentAPIView.as_view()),

    path('message/create', CreateMessageAPIView.as_view()),
    path('messages', ViewMessageAPIView.as_view()),
    path('messages/<str:pk>/', ViewMessageAPIView.as_view()),

    path('notice', GetUnreadNumberNotice.as_view()),
    path('notice/<str:pk>/', GetUnreadNumberNotice.as_view()),
    
    path('chat', MessageAPIView.as_view()),
    path('chat/<str:pk>/', MessageAPIView.as_view()),


    path('product/month', MonthPaymentPIView.as_view(), name='month-payment'),
    path('product/2weeks', TwoWeeksPaymentPIView.as_view(), name='2weeks-payment'),
    path('product/week', OneWeekPaymentPIView.as_view(), name='week-payment'),

    path('ad/active', ActiveAPIView.as_view(), name='active'),
    path('ad/createpayment', CreatePaymentAPIView.as_view(), name='CreatePayment'),

    path('ad/active/post', ActivePostAPIView.as_view(), name='active-post'),
]
