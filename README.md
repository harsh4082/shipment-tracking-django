#  Shipment Project

This is a Django-based shipment management application.

---

## Steps to Use the App

### 1. Clone the Repository

```bash
git clone <your-repo-url>
cd shipment_project
```

## 2. Install Dependencies
```bash
pip install -r requirements.txt
```
Make sure your requirements.txt includes:
```
Django==5.0.6
djangorestframework==3.15.2
openpyxl==3.1.2
XlsxWriter==3.1.3
reportlab==4.1.3
cryptography==41.0.4
```

## 3. Apply Migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

## 4. Create a Superuser
```bash
python manage.py createsuperuser
```
###### Set your username, email, and password as prompted.

## 5. Run the Project
```bash
python manage.py runserver
```

#### Access the project at:
```
http://127.0.0.1:8000/
```

## 6. Access Admin Panel
Go to the admin login page:
```
http://127.0.0.1:8000/admin/
```
Log in with your superuser credentials.

## 7. Add Admin and Users
Once logged in, you can add Admin accounts and Customers.
Manage Containers, Orders, and explore all functionalities.
Export orders to Excel or PDF and send credentials via email.

## 8. Explore the Website

Navigate through the app and test all features.

Add more data via the admin panel to see how the system works.