
# Custom User yozish  
  
Assalomu alaykum. Ushbu maqolada AbstractUserdan foydalangan holda custom User model yozishni o'rganamiz  
  
## Eslatma  
  
**Agar siz Custom user ishlatmoqchi bo'lsangiz - proyektni yaratganingizdan keyin migrate qilmasdan oldin User modelni yozib chiqishingiz kerak bo'ladi. Bo'lmasa keyinchalik databaseda muammolar chiqish ehtimoli bor!**  
  
  
## AbstractUser   
Yuqorida aytib o'rganimdek biz Custom User yozish uchun AbstractUserdan voris olishimiz kerak bo'ladi (inherit). Bu ikkisining farqi nimada?  
  
**AbstractUser**. Agar siz bundan foydalansangiz - Userda bor default fieldlar (username, email, phone, password...) sizni yangi modelingizda ham bo'ladi. Bunda hohlasangiz ularni overwrite qilishingiz yoki yangi field_lar ham qo'shishingiz mumkin. Masalan:   
  
 ``` 
 from django.db import models 
from django.contrib.auth.models import AbstractUser   

class MyUser(AbstractUser):    
     address = models.CharField(max_length=30, blank=True)    
     birth_date = models.DateField()  
```  
bu yerda MyUser modelida `username, password, email` va default `User`ni boshqa fieldlari mavjud (AbstractUserdan olinadi) va biz qo'shimcha ravishda `address` va `birth_date` fieldlarini ham qo'shdik.  
  
  
## Proyektni boshlash  
Avval yangi virtual environment ochib, Djangoni o'rnatamiz  
  
 

    python3 -m venv env 
    source env/bin/activate 
    pip install django

 Keyin proyekt ochib, uni ichida app ochamiz  
  

     django-admin startproject custom_user 
     cd custom_user 
     python manage.py startapp users  

## Model yozish  
users/models.py ni ochib model yozamiz  
  

     from django.db import models    
     from django.contrib.auth.models import AbstractUser    
     from users.managers import UserManager  
     
     class User(AbstractUser):    
        username = models.CharField(max_length=35, unique=True)    
        email = models.EmailField(null=True, blank=True)    
        full_name = models.CharField(max_length=35)    
        phone = models.CharField(max_length=10, null=True, blank=True)
        address = models.CharField(max_length=30)    
        birth_date = models.DateField()    
     
        def __str__(self):    
            return "{}".format(self.full_name)  
  
  
## Usernameni almashtirish
Yuqoridagi kodda, by default - login qilish uchun `username` field ishlatiladi. Lekin biz boshqa fieldni login uchun ishlatmoqchimiz va bizga `username` field kerak emas. Buning uchun ozgina qo'shimcha kod yozamiz:


     from django.db import models    
     from django.contrib.auth.models import AbstractUser    
     from users.managers import UserManager  #yangi
     
     class User(AbstractUser):    
        username = None #yangi    
        email = models.EmailField(null=True, blank=True)    
        full_name = models.CharField(max_length=35)    
        phone = models.CharField(max_length=10, null=True, blank=True)
        address = models.CharField(max_length=30)    
        birth_date = models.DateField()    

        objects = UserManager()  #yangi  
        USERNAME_FIELD = 'phone'   #yangi
        REQUIRED_FIELDS = ['full_name'] #yangi

     
        def __str__(self):    
            return "{}".format(self.full_name)

Bu yerda phone fieldni username sifatida ishlatyabmiz, shuning uchun bizga username kerak emas (`username=None`). Phone ni username sifatida ishlatishimiz uchun Custom Manager  ham yozishimiz kerak bo'ladi. `users` papkasini ochib managers.py oching va quyidagi kodni yozing:  
  

    from django.contrib.auth.base_user import BaseUserManager        
        
    class UserManager(BaseUserManager):    
        use_in_migrations = True    
        
        def _create_user(self, phone, password, **extra_fields):    
            if not phone:    
                raise ValueError("The given phone must be set")      
        
            user = self.model(phone=phone, **extra_fields)    
            user.set_password(password)    
            user.save(using=self._db)    
            return user    
        
        def create_user(self, phone, password=None, **extra_fields):    
            extra_fields.setdefault("is_staff", False)    
            extra_fields.setdefault("is_superuser", False)    
            return self._create_user(phone, password, **extra_fields)    
        
        def create_superuser(self, phone, password, **extra_fields):    
            extra_fields.setdefault("is_staff", True)    
            extra_fields.setdefault("is_superuser", True)    
        
            if extra_fields.get("is_staff") is not True:    
                raise ValueError("Superuser is_staff=True bo'lishi kerak.")    
            if extra_fields.get("is_superuser") is not True:    
                raise ValueError("Superuser is_superuser=True bo'lishi kerak.")    
        
            return self._create_user(phone, password, **extra_fields)  
  
**Eslatma**: agar siz `USERNAME_FIELD` sifatida boshqa field bergan bo'lsangiz, yuqoridagi kodda `phone` ni o'rniga o'sha fieldni yozib chiqasiz. Agar siz `USERNAME_FIELD` dan **foydalanmasangiz**, manager ishlatish **shart bo'lmaydi!**  
  
## settings.py ni yangilash  
`custom_user/settings.py` ni ochib `INSTALLED_APPS` ga `users` appga qo'shamiz:  
  
 

    INSTALLED_APPS = [        
	    "django.contrib.admin",    
        "django.contrib.auth",    
        "django.contrib.contenttypes",    
        "django.contrib.sessions",    
        "django.contrib.messages",    
        "django.contrib.staticfiles",    
            
        "users" #shuyerga qo'shing    
        ]

  
Keyin proyektimizda avtorizatsiyada qaysi modeldan foydalanishni berib ketishimiz kerak:  
  
 

    AUTH_USER_MODEL = 'users.User'

 Bu yerda avtorizatsiya uchun `users` appni `User` modelidan foydalanish kerakligini yozdik.  
  
## User modelimizni admin.py da register qilish  
  
 from django.contrib import admin    from django.contrib.auth.forms import UserChangeForm    
    from django.utils.translation import gettext_lazy as _    
    from django.contrib.auth.admin import UserAdmin as BaseUserAdmin    
        
    from .models import User    
        
        
    class UserAdmin(BaseUserAdmin):    
        form = UserChangeForm    
        fieldsets = (    
            (_('Login details'), {'fields': ('phone', 'password', )}),    
            (_('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser',    
                                          'groups', 'user_permissions')}),    
            (_('Important dates'), {'fields': ('last_login', 'date_joined')}),    
            (_('User info'), {'fields': ('full_name', 'email')}),    
         )    
        add_fieldsets = (    
            (None, {    
                'classes': ('wide', ),    
             'fields': ('phone', 'full_name', 'password1', 'password2'),    
                     }),    
         )    
        list_display = ['phone', 'first_name', 'last_name', 'is_staff', "full_name", "phone"]    
        search_fields = ('phone', 'first_name', 'last_name')    
        ordering = ('phone', )    
        
        
    admin.site.register(User, UserAdmin)  
  
Kodda `fieldsets` qismida `User` fieldlarini 4 bo'limga bo'ldik.   
  
`add_fieldsets` dagi `fields` qismida - yangi user qo'shayotganda qaysi fieldlar chiqishi kerakligini yozdik.  
  
## Migration va testlash  
Ana endi migratsiya qilib yasagan custom User modelimizni testlab ko'rishimiz mumkin.  
  
 python manage.py makemigrations python manage.py migrateYangi superuser yaratamiz:  
  
 python manage.py createsuperuser     Phone: 901112233  
 Full name: Dilbarov Uktamjon Password:    Password (again):   
    Superuser created successfully.  
  
Adminkadan yangi user qo'shish:  
![Screenshot-from-2023-01-12-15-20-57](https://i.ibb.co/TqYyJwr/Screenshot-from-2023-01-12-15-20-57.png)  
Bu yerda biz admin.py da `add_filtersets` ga bergan fieldlarimizni ko'rishimiz mumkin.   
  
## Xulosa  
Xulosa qilib aytganda custom User yozish uchun quyidagi steplar bajariladi:  
1. Proyekt yaratiladi  
2. Users uchun app yasaladi  
3. Model & Admin yoziladi  
4. Settings.py to'g'irlanadi  
5. Vanihoyat migrate qilinadi, tamom!  
  
### Umid qilamanki ushbu maqola foydali bo'ldi!






