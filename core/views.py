from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib import messages
from django.contrib.auth.hashers import make_password, check_password
from django_ratelimit.decorators import ratelimit

from .models import Customer, Restaurant, Meal
from .forms import MealForm

import subprocess
import json
import numpy as np
import faiss
from openai import OpenAI


# ===============================================================
#                   LAZY RAG SEARCH (IMPORTANT)
# ===============================================================
def rag_search_query(q):
    """
    Lazy import for FAISS on run Django
    """
    from rag_query import search
    try:
        return search(q)
    except Exception:
        return "AI explanation is temporarily unavailable. Please try again later."


# ===============================================================
#                   WELCOME PAGE
# ===============================================================
def welcome(request):
    return render(request, "customer/welcome.html")


# ===============================================================
#                   R SCRIPT MOOD ANALYSIS
# ===============================================================
def run_r_mood_analysis(answers):
    try:
        r_script_path = "mood_analysis.R"
        r_executable = r"C:\Program Files\R\R-4.2.2\bin\Rscript.exe"

        answers_json = json.dumps(answers)

        result = subprocess.run(
            [r_executable, r_script_path, answers_json],
            capture_output=True,
            text=True
        )

        mood = result.stdout.strip()
        if mood == "":
            mood = "Neutral"

        return mood

    except Exception as e:
        print("R ERROR:", e)
        return "Neutral"


# ===============================================================
#                   RESTAURANT AUTH & DASHBOARD
# ===============================================================
@ratelimit(key='ip', rate='5/m', method='POST', block=True)
def restaurant_login(request):
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")

        try:
            restaurant = Restaurant.objects.get(email=email)
        except Restaurant.DoesNotExist:
            return render(request, "restaurant/login.html", {"error": "Invalid email or password"})

        if not check_password(password, restaurant.password):
            return render(request, "restaurant/login.html", {"error": "Invalid email or password"})

        if restaurant.status != "approved":
            return render(request, "restaurant/login.html", {"error": "Your account is pending admin approval."})

        request.session['restaurant_id'] = restaurant.id
        return redirect('restaurant_dashboard')

    return render(request, "restaurant/login.html")


def restaurant_signup(request):
    if request.method == "POST":
        email = request.POST.get("email")
        if Restaurant.objects.filter(email=email).exists():
            return render(request, "restaurant/signup.html", {"error": "Email already exists"})

        Restaurant.objects.create(
            name=request.POST.get("name"),
            email=email,
            password=make_password(request.POST.get("password")),
            phone=request.POST.get("phone"),
            address=request.POST.get("address"),
            status="pending",
        )

        return render(request, "restaurant/signup.html", {
            "success": "Signup received. Your account is pending admin approval before you can log in."
        })

    return render(request, "restaurant/signup.html")


def restaurant_dashboard(request):
    if 'restaurant_id' not in request.session:
        return redirect('restaurant_login')

    restaurant = Restaurant.objects.get(id=request.session['restaurant_id'])
    total_meals = Meal.objects.filter(restaurant=restaurant).count()

    return render(request, 'restaurant/dashboard.html', {
        'restaurant': restaurant,
        'total_meals': total_meals
    })


def restaurant_logout(request):
    request.session.flush()
    return redirect('restaurant_login')


# ===============================================================
#                   RESTAURANT MEALS CRUD
# ===============================================================
def meals_list(request):
    if 'restaurant_id' not in request.session:
        return redirect('restaurant_login')

    restaurant = Restaurant.objects.get(id=request.session['restaurant_id'])
    meals = Meal.objects.filter(restaurant=restaurant)

    return render(request, "restaurant/meals_list.html", {"meals": meals})


def meal_add(request):
    if 'restaurant_id' not in request.session:
        return redirect('restaurant_login')

    restaurant = Restaurant.objects.get(id=request.session['restaurant_id'])

    if request.method == "POST":
        Meal.objects.create(
            restaurant=restaurant,
            name=request.POST.get('name'),
            description=request.POST.get('description'),
            price=request.POST.get('price'),
            calories=request.POST.get('calories'),
            protein=request.POST.get('protein'),
            carbs=request.POST.get('carbs'),
            fat=request.POST.get('fat'),
            allergens=request.POST.get('allergens'),
            image=request.FILES.get('image') 

        )
        return redirect('meals_list')

    return render(request, "restaurant/meal_add.html")


def meal_edit(request, meal_id):
    if 'restaurant_id' not in request.session:
        return redirect('restaurant_login')

    meal = Meal.objects.get(id=meal_id)
    if meal.restaurant_id != request.session['restaurant_id']:
        return redirect('meals_list')

    if request.method == "POST":
        form = MealForm(request.POST, request.FILES, instance=meal)
        if form.is_valid():
            form.save()
            return redirect('meals_list')
    else:
        form = MealForm(instance=meal)

    return render(request, "restaurant/meal_edit.html", {"form": form, "meal": meal})


def meal_delete(request, meal_id):
    if 'restaurant_id' not in request.session:
        return redirect('restaurant_login')

    meal = Meal.objects.get(id=meal_id)
    if meal.restaurant_id != request.session['restaurant_id']:
        return redirect('meals_list')

    meal.delete()
    return redirect('meals_list')


def restaurant_profile(request):
    if 'restaurant_id' not in request.session:
        return redirect('restaurant_login')

    restaurant = Restaurant.objects.get(id=request.session['restaurant_id'])

    if request.method == "POST":
        restaurant.name = request.POST.get('name')
        restaurant.email = request.POST.get('email')
        restaurant.phone = request.POST.get('phone')
        restaurant.address = request.POST.get('address')
        restaurant.password = request.POST.get('password')
        restaurant.save()
        return redirect('restaurant_dashboard')

    return render(request, "restaurant/restaurant_profile.html", {"restaurant": restaurant})


# ===============================================================
#                   CUSTOMER AUTH
# ===============================================================
def customer_signup(request):
    if request.method == "POST":
        email = request.POST.get("email")
        if Customer.objects.filter(email=email).exists():
            return render(request, "customer/signup.html", {"error": "Email already exists"})

        def to_number(value):
            return value if value not in (None, "") else None

        Customer.objects.create(
            name=request.POST.get("name"),
            email=email,
            password=make_password(request.POST.get("password")),
            gender=request.POST.get("gender"),
            age=to_number(request.POST.get("age")),
            weight=to_number(request.POST.get("weight")),
            height=to_number(request.POST.get("height")),
            goal=request.POST.get("goal"),
            likes=request.POST.get("likes"),
            dislikes=request.POST.get("dislikes"),
            allergies=request.POST.get("allergies"),
            preferred_calories_min=to_number(request.POST.get("preferred_calories_min")),
            preferred_calories_max=to_number(request.POST.get("preferred_calories_max")),
        )

        request.session["customer_email"] = email
        return redirect("customer_home")

    return render(request, "customer/signup.html")


@ratelimit(key='ip', rate='5/m', method='POST', block=True)
def customer_login(request):
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")

        try:
            customer = Customer.objects.get(email=email)
        except Customer.DoesNotExist:
            return render(request, "customer/login.html", {"error": "Invalid email or password"})

        if check_password(password, customer.password):
            request.session["customer_email"] = customer.email
            return redirect("customer_home")

        return render(request, "customer/login.html", {"error": "Invalid email or password"})

    return render(request, "customer/login.html")


def customer_logout(request):
    request.session.flush()
    return redirect("customer_login")


# ===============================================================
#                   CUSTOMER HOME + RESTAURANTS + MEALS
# ===============================================================
def customer_home(request):
    if "customer_email" not in request.session:
        return redirect("customer_login")

    customer = Customer.objects.get(email=request.session["customer_email"])
    return render(request, "customer/home.html", {"customer": customer})


def customer_restaurants(request):
    if "customer_email" not in request.session:
        return redirect("customer_login")

    restaurants = Restaurant.objects.all()
    return render(request, "customer/restaurants.html", {"restaurants": restaurants})


def customer_meals(request, rest_id):
    restaurant = Restaurant.objects.get(id=rest_id)
    meals = Meal.objects.filter(restaurant=restaurant)

    return render(request, "customer/meals.html", {
        "restaurant": restaurant,
        "meals": meals
    })




# ===============================================================
#               NUTRITION FILTERING & SCORING
# ===============================================================
def filter_meals_for_customer(meals, customer):
    # Calories range
    if customer.preferred_calories_min:
        meals = meals.filter(calories__gte=customer.preferred_calories_min)

    if customer.preferred_calories_max:
        meals = meals.filter(calories__lte=customer.preferred_calories_max)

    # Allergies exclusion
    if customer.allergies:
        meals = meals.exclude(allergens__icontains=customer.allergies)

    # Likes / Dislikes
    if customer.likes:
        meals = meals.filter(description__icontains=customer.likes)

    if customer.dislikes:
        meals = meals.exclude(description__icontains=customer.dislikes)

    return meals


def nutrition_score(meal, customer):
    score = 0

    if customer.goal == "loss":
        score += max(0, 600 - (meal.calories or 0))
        score -= (meal.fat or 0)

    elif customer.goal == "gain":
        score += (meal.protein or 0) * 2
        score += (meal.calories or 0) * 0.2

    else:  # maintain
        score += (meal.protein or 0)
        score -= (meal.fat or 0)

    return score
    
    
    
# ===============================================================
#                   CUSTOMER QUIZ + RAG LOGIC
# ===============================================================
def customer_quiz(request):
    if request.method == "POST":
        answers = [
            request.POST.get("q1"),
            request.POST.get("q2"),
            request.POST.get("q3"),
            request.POST.get("q4"),
            request.POST.get("q5"),
            request.POST.get("q6"),
            request.POST.get("q7"),
        ]

        request.session["quiz_answers"] = answers
        return redirect("customer_quiz_result")

    return render(request, "customer/quiz.html")


@ratelimit(key='ip', rate='10/m', block=True)
def customer_quiz_result(request):
    if "customer_email" not in request.session:
        return redirect("customer_login")

    customer = Customer.objects.get(email=request.session["customer_email"])
    answers = request.session.get("quiz_answers", [])
    mood = run_r_mood_analysis(answers)

    # -----------------------
    # STEP 1: BASE MEALS
    # -----------------------
    meals_qs = Meal.objects.all()

    # -----------------------
    # STEP 2: FILTER BY CUSTOMER PROFILE
    # -----------------------
    meals_qs = filter_meals_for_customer(meals_qs, customer)

    # -----------------------
    # STEP 3: SCORE & RANK
    # -----------------------
    scored_meals = sorted(
        meals_qs,
        key=lambda m: nutrition_score(m, customer),
        reverse=True
    )

    recommended_meals = scored_meals[:6]

    # -----------------------
    # STEP 4: BUILD RAG CONTEXT (EXPLANATION)
    # -----------------------
    rag_context = f"""
Customer Profile:
Age: {customer.age}
Weight: {customer.weight}
Height: {customer.height}
Goal: {customer.goal}
Likes: {customer.likes}
Dislikes: {customer.dislikes}
Allergies: {customer.allergies}
Calories Range: {customer.preferred_calories_min} - {customer.preferred_calories_max}
Mood: {mood}

Recommended Meals:
"""

    for meal in recommended_meals:
        rag_context += f"""
Meal: {meal.name}
Calories: {meal.calories}
Protein: {meal.protein}
Carbs: {meal.carbs}
Fat: {meal.fat}
Allergens: {meal.allergens}
"""

    # Save context for chat later
    request.session["last_recommendation_context"] = rag_context

    # Ask RAG to explain
    rag_explanation = rag_search_query(
        "Explain why these meals are suitable...\n" + rag_context
    )

    return render(request, "customer/quiz_result.html", {
        "mood": mood,
        "recommended_meals": recommended_meals,
        "rag_explanation": rag_explanation
    })



# ===============================================================
#                   NUTRITION CHAT (RAG)
# ===============================================================
@ratelimit(key='ip', rate='20/m', method='POST', block=True)
def nutrition_chat(request):
    if request.method == "POST":
        user_message = request.POST.get("message", "")

        # customer_quiz_result
        context = request.session.get("last_recommendation_context", "")

        prompt = f"""
You are a nutrition assistant chatbot.

Context:
{context}

User Question:
{user_message}
"""

        reply = rag_search_query(prompt)

        return JsonResponse({"reply": reply})

    return JsonResponse({"error": "Invalid request"}, status=400)
    

# ===============================================================
#                   RAG DATA EXPORT
# ===============================================================
def rag_data_export(request):
    if 'restaurant_id' not in request.session:
        return JsonResponse({"error": "Unauthorized"}, status=403)

    restaurants = list(Restaurant.objects.values())
    meals = list(Meal.objects.values())
    customers = list(Customer.objects.values())

    data = {
        "restaurants": restaurants,
        "meals": meals,
        "customers": customers
    }

    return JsonResponse(data, safe=False)
