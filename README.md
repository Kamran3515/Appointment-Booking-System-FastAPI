# Appointment Booking System FastAPI

یک پروژه‌ی بک‌اند کامل پیاده‌سازی‌شده با **FastAPI** برای مدیریت کاربران، نقش‌ها، نوبت‌دهی و دسترسی‌ها. این پروژه به‌صورت ماژولار، قابل توسعه و مناسب قرار گرفتن در رزومه طراحی شده است.

---

## ✨ ویژگی‌ها

* احراز هویت و مجوزدهی با JWT
* مدیریت کاربران با نقش‌های مختلف:

  * Client
  * Provider
  * Admin
* ثبت‌نام و ورود کاربران
* دریافت پروفایل کاربر لاگین‌شده
* مدیریت Availability برای Providerها
* ایجاد Appointment توسط Clientها
* کنترل سطح دسترسی (Role-Based Access Control)
* ساختار تمیز و استاندارد پروژه
* آماده برای Docker و توسعه بیشتر

---

## 🧱 تکنولوژی‌ها

* **Python 3.11+**
* **FastAPI**
* **SQLAlchemy (Async)**
* **PostgreSQL**
* **Alembic** (Migration)
* **Pydantic**
* **JWT Authentication**
* **Docker & Docker Compose**

---

## 📂 ساختار پروژه

```
app/
├── api/
│   ├── v1/
│   │   ├── auth.py
│   │   ├── users.py
│   │   ├── availability.py
│   │   ├── service.py
│   │   ├── provider_service.py
│   │   └── appointments.py
│   └── deps.py
├── core/
│   ├── config.py
│   └── security.py
├── db/
│   ├── base.py
│   └── session.py
├── models/
│   ├── user.py
│   ├── service.py
│   ├── provider_service.py
│   ├── availability.py
│   └── appointment.py
├── schemas/
│   ├── appionment_schema.py
│   ├── availability_schema.py
│   ├── provider_service_schema.py
│   ├── service_schema.py
│   └── user_schema.py
└── main.py
```

---

## 🔐 احراز هویت

* ثبت‌نام: `POST /auth/register`
* ورود: `POST /auth/login`
* استفاده از توکن JWT در هدر:

```
Authorization: Bearer <access_token>
```

---

## 👤 نقش‌ها و دسترسی‌ها

| نقش      | دسترسی‌ها                 |
| -------- | ------------------------- |
| Client   | مشاهده پروفایل، رزرو نوبت |
| Provider | ایجاد Availability        |
| Admin    | مدیریت کامل سیستم         |

---

## ⚙️ راه‌اندازی پروژه

### 1. کلون کردن پروژه

```bash
git clone <repository-url>
cd project-name
```

### 2. اجرای پروژه با Docker

```bash
docker-compose up --build
```

### 3. دسترسی به مستندات API

```
http://localhost:8000/docs
```

یا

```
http://localhost:8000/redoc
```

---

## 🧪 تست‌ها

در این پروژه زیرساخت تست در نظر گرفته شده و قابلیت توسعه تست‌ها با `pytest` وجود دارد.

---

## 🎯 هدف پروژه

این پروژه با هدف:

* تمرین معماری بک‌اند واقعی
* پیاده‌سازی احراز هویت و سطح دسترسی
* آمادگی برای پروژه‌های Production
* استفاده در رزومه و GitHub

توسعه داده شده است.

---

## 📌 برنامه‌های آینده

* اتصال به Frontend
* اضافه کردن Refresh Token
* بهبود لاگ‌ها و Error Handling
* نوشتن تست‌های کامل

---

## 👨‍💻 توسعه‌دهنده

**Kamran**
Backend Developer (Python / FastAPI / Django)

---

⭐ اگر پروژه رو دوست داشتی، حتماً Star بده!
