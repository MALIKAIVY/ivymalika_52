# Vunoh Global — Diaspora AI Assistant 🇰🇪

Vunoh Global is an AI-powered concierge and task management platform designed to help Kenyans living abroad manage local tasks in Kenya with ease and transparency. 

From sending money and verifying land titles to hiring local services or arranging airport transfers, Vunoh Global transforms complex requests into organized action plans and multi-channel communication templates.

---

## 🚀 Setup Instructions

### 1. Prerequisites
- Python 3.9+
- PostgreSQL
- Gemini API Key (Google Generative AI)

### 2. Installation
1. Clone the repository and navigate to the project root.
2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\\Scripts\\activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

### 3. Environment Configuration
Create a `.env` file in the root directory and add the following:
```env
DATABASE_URL=postgres://user:password@localhost:5432/vunoh
SECRET_KEY=your_django_secret_key
DEBUG=True
GEMINI_API_KEY=your_gemini_api_key_here
```

### 4. Database Setup
1. Run migrations:
   ```bash
   python manage.py migrate
   ```
2. Seed the database with sample tasks (required for submission):
   ```bash
   python manage.py seed_tasks
   ```

### 5. Running the Application
```bash
python manage.py runserver
```
- **Customer Portal**: [http://localhost:8000/](http://localhost:8000/)
- **Operations Dashboard**: [http://localhost:8000/dashboard/](http://localhost:8000/dashboard/)

---

## ✨ Key Features

- **🧠 AI Orchestration**: Uses Gemini 2.0 Flash to extract intent and entities from natural language requests.
- **🛡️ Risk Assessment**: Automated risk scoring (0-100) based on task intent, urgency, and financial complexity.
- **📋 Action Planning**: Generates step-by-step fulfillment plans for the internal operations team.
- **💬 Multi-Format Communication**: Instant generation of personalized WhatsApp, Email, and SMS templates.
- **📊 Operations Dashboard**: Secure internal interface with live analytics, status tracking, and department assignments (Finance, Legal, etc.).
- **🔒 Access Segregation**: Separated customer-facing intake portal and internal management dashboard for data privacy.

---

## 🏛️ Decisions I Made and Why

### 1. Choice of AI: Gemini 2.0 Flash
I chose **Gemini 2.0 Flash** via the `google-genai` SDK because of its high-speed inference and exceptional ability to produce structured JSON outputs. This allowed for reliable intent extraction and entity recognition without complex parsing logic.

### 2. Security: Access Segregation
I decided to split the application into two distinct views (`/` for customers and `/dashboard/` for staff). This ensures that customers cannot see the analytics, risk scores, or other customers' data, maintaining professional data privacy and operational security.

### 3. Technical Stack: Django + Vanilla Frontend
**Django** was chosen for the backend due to its robust ORM, admin security features, and "batteries-included" philosophy, which made handling PostgreSQL relations (Task -> Steps/Messages) seamless. On the frontend, I opted for **Vanilla HTML, CSS, and JS** to ensure maximum performance, zero dependency bloat, and full control over the premium design aesthetics.

### 4. Data Persistence: Atomic Transactions
All task creation logic is wrapped in **Django atomic transactions**. This ensures that the Task, TaskSteps, and TaskMessages are saved together or not at all, preventing "orphaned" tasks in the database if the AI or database fails during processing.

### 5. Personalization: Customer Context
The system was designed to capture customer contact details (Name, Phone, Email) at the intake stage. This allows the AI to personalize all communication templates (e.g., Addressing the customer by name), making the platform feel like a high-end concierge service.

---

## 📁 Repository Structure
- `assistant/`: Core app logic (OCR, calculations, views).
- `vunoh_global/`: Project configuration and settings.
- `templates/`: User interfaces (Customer Portal & Ops Dashboard).
- `static/css/`: Shared premium design styles.
- `vunoh_dump.sql`: Full database schema and 5 sample tasks (Required for submission).

---

## 📝 Submission Confirmation
The **SQL dump file** (`vunoh_dump.sql`) is committed in the root directory and contains:
1. Full database schema.
2. 5 Sample Tasks with complete data (Extracted entities, steps, 3 messages, risk scores, and assignments).
