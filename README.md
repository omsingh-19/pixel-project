# 🛍️ Vyapar-Sarthi AI — Smart Recommendation System for Local Shops

## 📌 Overview
Vyapar-Sarthi AI is a lightweight recommendation system designed for **local shopkeepers** to increase sales through **smart product suggestions**.

It helps shop owners discover which products to recommend together (cross-selling), improving **customer engagement and basket value**.

---

## 🚀 Features

- 🔐 Shopkeeper Login & Signup
- 📊 Dashboard with analytics
- 🛒 Product-based recommendations
- 📈 Search tracking & insights
- ⚡ FastAPI backend with Jinja2 frontend

---

## 🧠 How It Works

This system uses an **Item-Based Recommendation Approach**:

1. Products are converted into feature vectors (category, tags, etc.)
2. **Cosine similarity** is computed between products
3. When a shopkeeper selects a product:
   - Similar products are recommended
4. Recommendations are displayed with:
   - Score
   - Reason
   - Price

---

## 📊 Example

If a shopkeeper selects:

> 🥖 Bread

The system may suggest:

- 🥛 Milk  
- 🧈 Butter  
- 🍓 Jam  

---

## 🏗️ Tech Stack

### Backend
- FastAPI
- SQLAlchemy
- SQLite

### Machine Learning
- Pandas
- Scikit-learn (Cosine Similarity)

### Frontend
- HTML, CSS (Jinja2 Templates)

---
