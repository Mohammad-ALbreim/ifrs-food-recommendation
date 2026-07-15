from django.db import models


# -------------------------------
# RESTAURANT MODEL
# -------------------------------
class Restaurant(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('suspended', 'Suspended'),
    ]

    name = models.CharField(max_length=255)
    email = models.CharField(max_length=255, unique=True)
    password = models.CharField(max_length=255)
    phone = models.CharField(max_length=50, null=True, blank=True)
    address = models.CharField(max_length=255, null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Restaurant"
        verbose_name_plural = "Restaurants"


# -------------------------------
# CUSTOMER MODEL
# -------------------------------
class Customer(models.Model):
    GENDER_CHOICES = [
        ('male', 'Male'),
        ('female', 'Female'),
    ]

    GOAL_CHOICES = [
        ('loss', 'Loss'),
        ('gain', 'Gain'),
        ('maintain', 'Maintain'),
    ]

    name = models.CharField(max_length=255)
    email = models.CharField(max_length=255, unique=True)
    password = models.CharField(max_length=255)

    gender = models.CharField(max_length=10, choices=GENDER_CHOICES)
    age = models.IntegerField(null=True, blank=True)
    weight = models.FloatField(null=True, blank=True)
    height = models.FloatField(null=True, blank=True)

    goal = models.CharField(max_length=20, choices=GOAL_CHOICES)

    likes = models.TextField(null=True, blank=True)
    dislikes = models.TextField(null=True, blank=True)
    allergies = models.TextField(null=True, blank=True)

    preferred_calories_min = models.IntegerField(null=True, blank=True)
    preferred_calories_max = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Customer"
        verbose_name_plural = "Customers"


# -------------------------------
# MEAL MODEL
# -------------------------------
class Meal(models.Model):
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    calories = models.IntegerField(null=True, blank=True)
    protein = models.FloatField(null=True, blank=True)
    carbs = models.FloatField(null=True, blank=True)
    fat = models.FloatField(null=True, blank=True)

    allergens = models.TextField(null=True, blank=True)
    image = models.ImageField(upload_to='meals/', null=True, blank=True)
    
    
    
    
    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Meal"
        verbose_name_plural = "Meals"


# -------------------------------
# CART MODEL
# -------------------------------
class Cart(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Cart #{self.id} ({self.customer.name})"

    class Meta:
        verbose_name = "Cart"
        verbose_name_plural = "Carts"


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name="items")
    meal = models.ForeignKey(Meal, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    unit_price_snapshot = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.quantity} x {self.meal.name}"

    @property
    def line_total(self):
        return self.quantity * self.unit_price_snapshot

    class Meta:
        verbose_name = "Cart Item"
        verbose_name_plural = "Cart Items"
