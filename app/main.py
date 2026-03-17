from pathlib import Path

from fastapi import FastAPI, Request, Depends, Form, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from starlette.middleware.sessions import SessionMiddleware

from .database import SessionLocal, engine, Base
from . import models, schemas
from .auth import hash_password, verify_password
from .seed import seed_products
from .recommender import dashboard_metrics
from .ml import (
    recommend as ml_recommend,
    normalize_shop_type,
    display_shop_type,
    get_inventory_for_shop_type,
)

BASE_DIR = Path(__file__).resolve().parent

app = FastAPI(title="SmartShop AI")
app.add_middleware(SessionMiddleware, secret_key="smartshop-ai-secret-key")
app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))

Base.metadata.create_all(bind=engine)
seed_products()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def current_user(request: Request, db: Session):
    user_id = request.session.get("user_id")
    if not user_id:
        return None
    return db.query(models.Shopkeeper).filter(models.Shopkeeper.id == user_id).first()


def convert_ml_results_to_ui(db: Session, raw_results):
    results = []
    for rec in raw_results:
        matched_product = (
            db.query(models.Product)
            .filter(models.Product.name == rec["name"])
            .first()
        )

        if matched_product:
            results.append({
                "name": matched_product.name,
                "category": matched_product.category,
                "price": matched_product.base_price,
                "score": rec["score"],
                "reason": "Recommended using item-to-item cosine similarity",
            })
        else:
            results.append({
                "name": rec["name"],
                "category": "Unknown",
                "price": 0,
                "score": rec["score"],
                "reason": "Recommended using item-to-item cosine similarity",
            })
    return results


def render_dashboard(request: Request, db: Session, user, result=None, selected=None):
    inventory_names = get_inventory_for_shop_type(user.shop_type)

    products = (
        db.query(models.Product)
        .filter(models.Product.name.in_(inventory_names))
        .order_by(models.Product.name.asc())
        .all()
    )

    metrics = dashboard_metrics(db, user.id)

    return templates.TemplateResponse(
        "dashboard.html",
        {
            "request": request,
            "user": user,
            "display_shop_type": display_shop_type(user.shop_type),
            "products": products,
            "metrics": metrics,
            "result": result,
            "selected": selected,
        },
    )


@app.get("/", response_class=HTMLResponse)
def root(request: Request, db: Session = Depends(get_db)):
    user = current_user(request, db)
    if user:
        return RedirectResponse(url="/dashboard", status_code=302)
    return templates.TemplateResponse("index.html", {"request": request, "error": None})


@app.get("/dashboard", response_class=HTMLResponse)
def dashboard_page(request: Request, db: Session = Depends(get_db)):
    user = current_user(request, db)
    if not user:
        return RedirectResponse(url="/", status_code=302)
    return render_dashboard(request, db, user)


@app.post("/signup", response_class=HTMLResponse)
def signup(
    request: Request,
    shop_name: str = Form(...),
    owner_name: str = Form(...),
    username: str = Form(...),
    password: str = Form(...),
    location: str = Form(...),
    shop_type: str = Form(...),
    db: Session = Depends(get_db),
):
    existing = db.query(models.Shopkeeper).filter(models.Shopkeeper.username == username).first()
    if existing:
        return templates.TemplateResponse(
            "index.html",
            {"request": request, "error": "Username already exists. Please choose another username."},
            status_code=400,
        )

    normalized_shop_type = normalize_shop_type(shop_type)

    user = models.Shopkeeper(
        shop_name=shop_name,
        owner_name=owner_name,
        username=username,
        password_hash=hash_password(password),
        location=location,
        shop_type=normalized_shop_type,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    request.session["user_id"] = user.id
    return RedirectResponse(url="/dashboard", status_code=302)


@app.post("/login", response_class=HTMLResponse)
def login(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db),
):
    user = db.query(models.Shopkeeper).filter(models.Shopkeeper.username == username).first()
    if not user or not verify_password(password, user.password_hash):
        return templates.TemplateResponse(
            "index.html",
            {"request": request, "error": "Invalid username or password."},
            status_code=401,
        )
    request.session["user_id"] = user.id
    return RedirectResponse(url="/dashboard", status_code=302)


@app.get("/logout")
def logout(request: Request):
    request.session.clear()
    return RedirectResponse(url="/", status_code=302)


@app.post("/recommend", response_class=HTMLResponse)
def recommend_form(
    request: Request,
    product_id: int = Form(...),
    db: Session = Depends(get_db),
):
    user = current_user(request, db)
    if not user:
        return RedirectResponse(url="/", status_code=302)

    base_product = db.query(models.Product).filter(models.Product.id == product_id).first()
    if not base_product:
        raise HTTPException(status_code=404, detail="Product not found")

    raw_results = ml_recommend(
        item_name=base_product.name,
        shop_type=user.shop_type,
        top_n=4,
    )

    results = convert_ml_results_to_ui(db, raw_results)

    search = models.SearchLog(
        shopkeeper_id=user.id,
        product_id=base_product.id,
    )
    db.add(search)
    db.commit()

    result = {
        "base_product": base_product.name,
        "recommendations": results,
        "explanation": "Recommendations are generated using an ML-based item-to-item similarity model built from transaction data.",
    }

    selected = {
        "product_id": product_id,
    }

    return render_dashboard(request, db, user, result=result, selected=selected)


@app.get("/api/products", response_model=list[schemas.ProductOut])
def products(request: Request, db: Session = Depends(get_db)):
    user = current_user(request, db)
    if not user:
        raise HTTPException(status_code=401, detail="Login required")

    inventory_names = get_inventory_for_shop_type(user.shop_type)

    return (
        db.query(models.Product)
        .filter(models.Product.name.in_(inventory_names))
        .order_by(models.Product.name.asc())
        .all()
    )


@app.post("/api/recommend")
def recommend_api(payload: schemas.RecommendRequest, request: Request, db: Session = Depends(get_db)):
    user = current_user(request, db)
    if not user:
        raise HTTPException(status_code=401, detail="Login required")

    base_product = db.query(models.Product).filter(models.Product.id == payload.product_id).first()
    if not base_product:
        raise HTTPException(status_code=404, detail="Product not found")

    raw_results = ml_recommend(
        item_name=base_product.name,
        shop_type=user.shop_type,
        top_n=payload.top_n,
    )

    results = convert_ml_results_to_ui(db, raw_results)

    search = models.SearchLog(
        shopkeeper_id=user.id,
        product_id=base_product.id,
    )
    db.add(search)
    db.commit()

    return JSONResponse(
        {
            "base_product": base_product.name,
            "recommendations": results,
            "explanation": "Recommendations are generated using an ML-based item-to-item similarity model built from transaction data.",
        }
    )


@app.get("/api/metrics")
def metrics(request: Request, db: Session = Depends(get_db)):
    user = current_user(request, db)
    if not user:
        raise HTTPException(status_code=401, detail="Login required")
    return dashboard_metrics(db, user.id)