from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    # Welcome
    path('', views.welcome, name='welcome'),

    # Restaurant
    path('restaurant/login/', views.restaurant_login, name='restaurant_login'),
    path('restaurant/signup/', views.restaurant_signup, name='restaurant_signup'),
    path('restaurant/dashboard/', views.restaurant_dashboard, name='restaurant_dashboard'),
    path('restaurant/logout/', views.restaurant_logout, name='restaurant_logout'),
    path('restaurant/meals/', views.meals_list, name='meals_list'),
    path('restaurant/meals/add/', views.meal_add, name='meal_add'),
    path('restaurant/meals/edit/<int:meal_id>/', views.meal_edit, name='meal_edit'),
    path('restaurant/meals/delete/<int:meal_id>/', views.meal_delete, name='meal_delete'),
    path('restaurant/profile/', views.restaurant_profile, name='restaurant_profile'),

    # Customer
    path('customer/signup/', views.customer_signup, name='customer_signup'),
    path('customer/login/', views.customer_login, name='customer_login'),
    path('customer/logout/', views.customer_logout, name='customer_logout'),
    path('customer/', views.customer_home, name='customer_home'),
    path('customer/restaurants/', views.customer_restaurants, name='customer_restaurants'),
    path('customer/meals/<int:rest_id>/', views.customer_meals, name='customer_meals'),
    path('customer/cart/add/<int:meal_id>/', views.cart_add, name='cart_add'),
    path('customer/cart/', views.cart_view, name='cart_view'),
    path('customer/quiz/', views.customer_quiz, name='customer_quiz'),
    path('customer/quiz/result/', views.customer_quiz_result, name='customer_quiz_result'),

    # RAG — Export Data
    path('rag/export/', views.rag_data_export, name='rag_export'),
    
    
    path("nutrition/chat/", views.nutrition_chat, name="nutrition_chat"),

  
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
