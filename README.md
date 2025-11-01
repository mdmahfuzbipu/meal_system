# 🍽️ Hall Meal Management System – Django Web Application

**Hall Meal Management System** is a professional-grade Django web application designed to manage student meals, preferences, daily meal status, and monthly cost summaries in a hostel environment.  
It provides a complete digital solution for **students, managers, and admins**, enabling seamless coordination between meal tracking, cost calculation, token issuance, voting, notices, and complaints.
It goes beyond traditional digital systems by introducing REST API endpoints, enabling future integration with **AI Agents, mobile apps, and research systems** — making it a future-proof smart meal solution for modern institutions. It also has **AI chatbot integration (Gemini)** and a **Dockerized** production-ready environment.

---

## 🚀 Features (Till Now) — **Total 2+ Features**

### 🌟Core Highlights

- ✅ AI-Powered Chatbot – Gemini 2.0 Flash integrated chatbot for student queries and smart meal assistance
- 🐳 Docker Support – Full Docker setup for easy deployment and isolated PostgreSQL database
- 📊 Automated Meal Costing – Dynamic calculation based on preferences & menus
- 🧠 Smart Substitutions – Beef ↔ Mutton, Fish ↔ Egg handled automatically
- 🗳️ Voting, Notices, and Reports – Engage, announce, and track everything in one system
- 💬 Complaints Module – Students can raise issues digitally
- 🔒 Role-Based Access – Secure portals for Admins, Managers, and Students


### 👨‍🎓 Student Features (8)
- 🟢 Toggle daily meal status (ON/OFF for breakfast, lunch, dinner)
- 🕕 Automatic meal cutoff system (before 8:00 PM)
- 🍛 Select monthly meal preference (Beef/Fish vs Mutton/Egg)
- 💰 View detailed monthly cost summary
- 📅 See cost history & total ON/OFF days
- 🗳️ Participate in hostel voting (Universal / Floor-wise polls)
- 💬 Interact with AI Chatbot (Gemini) for meal-related help
- 📝 Submit complaints or feedback

### 👨‍🍳 Manager Features (6)
- 👀 View student status by room number
- 🎟️ Issue meal tokens dynamically based on preferences
- 📊 View daily and monthly reports
- 📤 Export monthly summaries to Excel
- 📈 Track Beef/Mutton and Fish/Egg counts
- 🗳️ Manage polls and results

### 🧑‍💼 Admin Features (5)
- ➕ Register and manage all users (Admin, Manager, Student)
- ✏️ Edit/deactivate users
- 📊 Access global summaries and reports
- 👥 Manage roles and permissions
- 🧾 Generate monthly reports for all students

### 🍲 Meal Management (4)
- 📆 Manage weekly menus (Breakfast, Lunch, Dinner)  
- 🔄 Automatically handle substitutions:  
  - Beef → Mutton  
  - Fish → Egg  
- 💸 Calculate cost dynamically based on menu & preferences  
- 🗓️ Track total ON days and generate cost summaries for every student  


### 🗞️ Notices & Complaints (2)
- 📰 Create and view notices (with images)
- 📝 Submit and manage complaints


### 🗳️ Voting System
- 📌 Floor-wise voting  
- 🌐 Universal voting  


### 🧠 AI Chatbot (Gemini Integration)
- 🤖 Built-in student chatbot powered by Google Gemini 2.0 Flash API
- 💬 Students can ask meal-related, system, or hostel questions
- 🧩 Integrated via ai_utils.py using .env stored GOOGLE_API_KEY
- 🔒 Secure environment handling — no hardcoded keys


### 🧩 REST API Integration
- 🧠 Designed to serve AI systems and external mobile apps
- 📡 Exposes secure, authenticated DRF endpoints
- 📊 Can be used for data analysis, ML training, or predictive systems
- ⚙️ Used internally for chatbot queries and decision support


### 🐳 Docker Deployment Support
- 🗂️ PostgreSQL container for database isolation
- 📦 Django app container using .env for all secrets
- 💾 Persistent volumes for static & media files
- ⚙️ Docker Compose for one-command setup


---

## 🛠️ Tech Stack

- **Backend**:  Django 5.x (Python 3.11+)
- **Frontend**: Tailwind CSS + HTML Templates Bootstrap
- **Database**: PostgreSQL
- **AI Integration**:	Google Gemini 2.0 Flash
- **Deployment**:	Docker + Docker Compose
- **Excel Export**: `openpyxl`
- **Authentication**: Custom User Model with Role-based Access (Admin, Manager, Student)
- **Version Control**: Git + GitHub
- **API**: Django REST Framework (DRF)
---

## 📁 Project Structure
```
meal_management/
├── accounts/               #(Admin/Manager/Student)
├── admins/                 # Admin-related views & controls
├── managers/               # Manager dashboards,token issue,reports export
├── students/               # Student dashboard, daily status, preferences
├── meal_system/            # Core app for meal types, weekly menu, and summaries
├── chatbot/                # Gemini AI integration (ai_utils.py)
├── notices/                # Notice management module
├── votes/                  # Voting system app
├── media/                  # User-uploaded files 
├── static/                 # Static assets (CSS, JS, images)
├── templates/              # Global and app-level templates
├── .env                    # Environment variables
├── Dockerfile
├── docker-compose.yml
├── requirements.txt        # Dependencies
├── manage.py
└── README.md
```


---

## ⚙️ Setup Instructions

### 1. Clone the Repository
```
git clone https://github.com/mdmahfuzbipu/meal_system.git
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
DATABASE_URL=postgresql:///db.postgresql
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
- 🧠 Full AI Agent support for decision automation
- 📱 Responsive UI for all devices (mobile-first)
- 🔔 Real-time meal & notice notifications
- 💳 Payment & billing integration
- 📊 Interactive analytics dashboard
- 🌐 Multi-hall support
- ☁️ Cloud deployment via Docker
- 📬 Automated meal reminders through email or chatbot

🪪 License
This project is licensed under the MIT License – see the LICENSE file for details.

## 🙋‍♂️ Author

Md Mahfuz Hossain  
Backend Developer | Django Enthusiast  
[GitHub](https://github.com/mdmahfuzbipu) | [LinkedIn](https://www.linkedin.com/in/muhammadmahfuzhossain/)