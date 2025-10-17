# 🍽️ Hostel Meal Management System – Django Web Application

**Hostel Meal Management System** is a professional-grade Django web application designed to manage student meals, preferences, daily meal status, and monthly cost summaries in a hostel environment.  
It provides a complete digital solution for **students, managers, and admins**, enabling seamless coordination between meal tracking, cost calculation, and token issuance.

---

## 🚀 Features (Till Now)

### 👨‍🎓 Student Features
- 🟢 Toggle daily meal status (ON/OFF for breakfast, lunch, dinner)
- 🕕 Cutoff time control (change allowed before 6:00 PM)
- 🍛 Choose monthly meal preferences (Beef/Fish vs Mutton/Egg)
- 💰 View monthly meal summary with total cost
- 📅 View cost history and total ON/OFF days

### 👨‍🍳 Manager Features
- 👀 View student meal status by room number
- 🎟️ Issue meal tokens based on student preferences
- 📊 View daily and monthly summaries
- 📤 Export monthly summaries to Excel
- 📈 View total Beef/Mutton and Fish/Egg statistics

### 🧑‍💼 Admin Features
- ➕ Register new students, managers
- ✏️ Edit or deactivate existing students, managers
- 👥 Manage roles (Admin / Manager / Student)
- 📈 View total Beef/Mutton and Fish/Egg statistics
- 🧾 Generate monthly reports for all students

### 🍲 Meal Management
- 📆 Manage weekly menus (Breakfast, Lunch, Dinner)
- 🔄 Automatically handle substitutions:
  - Beef → Mutton
  - Fish → Egg
- 💸 Calculate cost dynamically based on menu & preferences
- 🗓️ Track total ON days and generate cost summaries for every student

---

## 🛠️ Tech Stack

- **Backend**:  Django 5.x (Python 3.11+)
- **Frontend**: Tailwind CSS + HTML Templates Bootstrap
- **Database**: PostgreSQL
- **Excel Export**: `openpyxl`
- **Authentication**: Custom User Model with Role-based Access (Admin, Manager, Student)
- **Version Control**: Git + GitHub

---

## 📁 Project Structure
```
meal_management/
├── accounts/               #(Admin/Manager/Student)
├── admins/                 # Admin-related views & controls
├── managers/               # Manager dashboards,token issue,reports export
├── students/               # Student dashboard, daily status, preferences
├── meal_system/            # Core app for meal types, weekly menu, and summaries
├── notices/                # Notice management module
├── media/                  # User-uploaded files 
├── static/                 # Static assets (CSS, JS, images)
├── templates/              # Global and app-level templates
├── .env                    # Environment variables
├── requirements.txt        # Dependencies
├── manage.py
└── README.md
```


---

## ⚙️ Setup Instructions

### 1. Clone the Repository
```
git clone https://github.com/your-username/meal-management-system.git
cd meal-management-system
```
### 2. Create and Activate Virtual Environment
```
python -m venv venv
source venv/bin/activate       # On Windows: venv\Scripts\activate
```
### 3. Install Dependencies
```
pip install -r requirements.txt
```
### 4. Create .env File
At the root of your project:
```
DEBUG=True
SECRET_KEY=your-secret-key
ALLOWED_HOSTS=127.0.0.1,localhost
DATABASE_URL=sqlite:///db.sqlite3
```
### 5. Apply Migrations
```
python manage.py migrate
```
### 6. Create Superuser
```
python manage.py createsuperuser
```
### 7. Run the Server
```
python manage.py runserver
```
### 8. Access the App 🌐

🏠 Main App: http://127.0.0.1:8000

🔐 Admin Panel: http://127.0.0.1:8000/admin

## 📸 Screenshots(will be added)

### 🏠 Student Dashboard

### 🧾 Monthly Meal Summary

### 👨‍🍳 Manager Dashboard

### 📤 Excel Export

### 📅 Admin Dashboard


## 🧩 Future Roadmap

- 📱 Add mobile-friendly dashboard using Tailwind responsive design  
- 🔔 Real-time notifications for managers when students toggle meals  
- 💳 Add payment tracking for monthly meal bills  
- 📊 Add analytics dashboard with charts for meal statistics  
- 🧩 Implement role-based dashboards with custom widgets for admins, managers, and students  
- 🌐 Multi-hostel support for managing students across different buildings  
- ⚡ Optimize daily meal calculations and token issuance for large student datasets  
- 🛠️ Add automated email reminders for students about meal cutoff times

🪪 License
This project is licensed under the MIT License – see the LICENSE file for details.

## 🙋‍♂️ Author

Md Mahfuz Hossain  
Backend Developer | Django Enthusiast  
[GitHub](https://github.com/mdmahfuzbipu) | [LinkedIn](https://www.linkedin.com/in/muhammadmahfuzhossain/)