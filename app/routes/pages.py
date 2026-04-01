from fastapi import APIRouter, Request, Form, HTTPException, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from typing import List, Optional
from app.models import RecipeCreate, RecipeUpdate
from app.services.storage import recipe_storage

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


def _split_comma_separated(value: str) -> List[str]:
    return [item.strip() for item in value.split(",") if item.strip()]


def _split_instruction_steps(value: List[str] | str) -> List[str]:
    if isinstance(value, str):
        value = [value]

    return [step.strip() for step in value if step and step.strip()]


def _clean_optional_text(value: str) -> Optional[str]:
    text = value.strip()
    return text or None


@router.get("/", response_class=HTMLResponse)
def home(request: Request, search: Optional[str] = None, message: Optional[str] = None):
    """Home page with recipe list and search"""
    if search:
        recipes = recipe_storage.search_recipes(search)
    else:
        recipes = recipe_storage.get_all_recipes()
    
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "recipes": recipes,
            "search_query": search or "",
            "message": message,
        },
    )


@router.get("/recipes/new", response_class=HTMLResponse)
def new_recipe_form(request: Request):
    """New recipe form"""
    return templates.TemplateResponse(
        request=request,
        name="recipe_form.html",
        context={
            "recipe": None,
            "is_edit": False,
        },
    )


@router.get("/recipes/{recipe_id}", response_class=HTMLResponse)
def recipe_detail(request: Request, recipe_id: str, message: Optional[str] = None):
    """Recipe detail page"""
    recipe = recipe_storage.get_recipe(recipe_id)
    if not recipe:
        raise HTTPException(status_code=404, detail="Recipe not found")
    
    return templates.TemplateResponse(
        request=request,
        name="recipe_detail.html",
        context={
            "recipe": recipe,
            "message": message,
        },
    )


@router.get("/recipes/{recipe_id}/edit", response_class=HTMLResponse)
def edit_recipe_form(request: Request, recipe_id: str):
    """Edit recipe form"""
    recipe = recipe_storage.get_recipe(recipe_id)
    if not recipe:
        raise HTTPException(status_code=404, detail="Recipe not found")
    
    return templates.TemplateResponse(
        request=request,
        name="recipe_form.html",
        context={
            "recipe": recipe,
            "is_edit": True,
        },
    )


@router.post("/recipes/new")
def create_recipe_form(
    request: Request,
    title: str = Form(...),
    description: str = Form(...),
    difficulty: str = Form(...),
    ingredients: str = Form(...),
    instruction_steps: List[str] = Form(...),
    tags: str = Form(""),
    region: str = Form(""),
    cuisine: str = Form("")
):
    """Handle new recipe form submission"""
    try:
        # Check title length
        if len(title) > 200:
            raise ValueError("Title too long")
        
        # Parse ingredients, instruction steps, and tags
        ingredient_list = [ing.strip() for ing in ingredients.split('\n') if ing.strip()]
        instruction_list = _split_instruction_steps(instruction_steps)
        tag_list = _split_comma_separated(tags)
        
        # Validation
        if len(ingredient_list) == 0:
            raise ValueError("At least one ingredient required")
        
        if len(instruction_list) == 0:
            raise ValueError("At least one instruction step is required")
        
        recipe_data = RecipeCreate(
            title=title,
            description=description,
            difficulty=difficulty,
            ingredients=ingredient_list,
            instructions=instruction_list,
            tags=tag_list,
            region=_clean_optional_text(region),
            cuisine=_clean_optional_text(cuisine)
        )
        
        new_recipe = recipe_storage.create_recipe(recipe_data)
        return RedirectResponse(
            url=f"/recipes/{new_recipe.id}?message=Recipe created successfully",
            status_code=303
        )
    except Exception as e:
        return RedirectResponse(
            url=f"/?message=Error creating recipe: {str(e)}",
            status_code=303
        )


@router.post("/recipes/{recipe_id}/edit")
def update_recipe_form(
    request: Request,
    recipe_id: str,
    title: str = Form(...),
    description: str = Form(...),
    difficulty: str = Form(...),
    ingredients: str = Form(...),
    instruction_steps: List[str] = Form(...),
    tags: str = Form(""),
    region: str = Form(""),
    cuisine: str = Form("")
):
    """Handle edit recipe form submission"""
    try:
        # Check title length
        if len(title) > 200:
            raise ValueError("Title is too long!")
        
        # Parse ingredients, instruction steps, and tags
        ingredient_list = [ing.strip() for ing in ingredients.split('\n') if ing.strip()]
        instruction_list = _split_instruction_steps(instruction_steps)
        tag_list = _split_comma_separated(tags)
        
        if len(ingredient_list) == 0:
            raise ValueError("Need ingredients!")
            
        if len(instruction_list) == 0:
            raise ValueError("At least one instruction step is required")
        
        recipe_data = RecipeUpdate(
            title=title,
            description=description,
            difficulty=difficulty,
            ingredients=ingredient_list,
            instructions=instruction_list,
            tags=tag_list,
            region=_clean_optional_text(region),
            cuisine=_clean_optional_text(cuisine)
        )
        
        updated_recipe = recipe_storage.update_recipe(recipe_id, recipe_data)
        if not updated_recipe:
            return RedirectResponse(
                url=f"/?message=Recipe not found",
                status_code=303
            )
        
        return RedirectResponse(
            url=f"/recipes/{recipe_id}?message=Recipe updated successfully",
            status_code=303
        )
    except Exception as e:
        return RedirectResponse(
            url=f"/recipes/{recipe_id}?message=Error updating recipe: {str(e)}",
            status_code=303
        )


@router.post("/recipes/{recipe_id}/delete")
def delete_recipe_form(recipe_id: str):
    """Handle recipe deletion"""
    success = recipe_storage.delete_recipe(recipe_id)
    if success:
        return RedirectResponse(
            url="/?message=Recipe deleted successfully",
            status_code=303
        )
    else:
        return RedirectResponse(
            url="/?message=Recipe not found",
            status_code=303
        )


@router.get("/import", response_class=HTMLResponse)
def import_page(request: Request, message: Optional[str] = None):
    """Import recipes page"""
    return templates.TemplateResponse(
        request=request,
        name="import.html",
        context={
            "message": message,
        },
    )
