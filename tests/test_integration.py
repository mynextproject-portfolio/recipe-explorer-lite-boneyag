"""
Integration test to verify the recipe schema works end-to-end.
Tests schema validation, storage operations, and Pydantic serialization.
"""

import json
from pathlib import Path
from app.models import Recipe, RecipeCreate, RecipeUpdate
from app.services.storage import RecipeStorage


def test_sample_recipes_load():
    """Test that sample recipes can be loaded from JSON."""
    sample_file = Path(__file__).parent.parent / "sample-recipes.json"
    assert sample_file.exists(), f"Sample file not found: {sample_file}"
    
    with open(sample_file) as f:
        sample_data = json.load(f)
    
    assert len(sample_data) > 0, "Sample data is empty"
    assert len(sample_data) == 3, f"Expected 3 sample recipes, got {len(sample_data)}"


def test_sample_recipes_schema_validation():
    """Test that all sample recipes validate against the Recipe schema."""
    sample_file = Path(__file__).parent.parent / "sample-recipes.json"
    
    with open(sample_file) as f:
        sample_data = json.load(f)
    
    for i, recipe_dict in enumerate(sample_data):
        recipe = Recipe(**recipe_dict)
        
        # Verify instructions is a list
        assert isinstance(recipe.instructions, list), \
            f"Recipe {i}: instructions should be list, got {type(recipe.instructions)}"
        assert len(recipe.instructions) > 0, \
            f"Recipe {i}: instructions list should not be empty"
        
        # Verify region and cuisine are present
        assert recipe.region is not None, f"Recipe {i}: region is missing"
        assert recipe.cuisine is not None, f"Recipe {i}: cuisine is missing"
        
        # Verify basic fields
        assert recipe.title, f"Recipe {i}: title is missing"
        assert recipe.description, f"Recipe {i}: description is missing"
        assert recipe.ingredients, f"Recipe {i}: ingredients is missing"


def test_storage_import_and_retrieval():
    """Test that storage can import recipes and retrieve them."""
    sample_file = Path(__file__).parent.parent / "sample-recipes.json"
    
    with open(sample_file) as f:
        sample_data = json.load(f)
    
    storage = RecipeStorage()
    count = storage.import_recipes(sample_data)
    
    assert count == len(sample_data), \
        f"Expected {len(sample_data)} recipes imported, got {count}"
    
    # Verify all recipes are retrievable
    all_recipes = storage.get_all_recipes()
    assert len(all_recipes) == count, \
        f"Expected {count} recipes in storage, got {len(all_recipes)}"
    
    # Verify specific recipe retrieval
    if all_recipes:
        first_recipe = all_recipes[0]
        retrieved = storage.get_recipe(first_recipe.id)
        assert retrieved is not None, "Failed to retrieve specific recipe"
        assert retrieved.instructions == first_recipe.instructions, \
            "Instructions don't match after retrieval"


def test_pydantic_serialization():
    """Test that Pydantic models serialize correctly for JSON responses."""
    test_recipe_data = {
        "title": "Test Recipe",
        "description": "A test recipe",
        "ingredients": ["ingredient 1", "ingredient 2"],
        "instructions": ["First, do step 1.", "Then, do step 2."],
        "tags": ["test"],
        "region": "Test Region",
        "cuisine": "Test Cuisine",
        "difficulty": "Easy"
    }
    
    # Create via RecipeCreate model
    recipe_create = RecipeCreate(**test_recipe_data)
    
    # Create Recipe from RecipeCreate
    recipe = Recipe(**recipe_create.model_dump())
    
    # Serialize to dict (what the API returns)
    recipe_dict = recipe.model_dump()
    
    # Verify instructions, region, cuisine are preserved
    assert recipe_dict['instructions'] == test_recipe_data['instructions'], \
        "Instructions not preserved in serialization"
    assert recipe_dict['region'] == test_recipe_data['region'], \
        "Region not preserved in serialization"
    assert recipe_dict['cuisine'] == test_recipe_data['cuisine'], \
        "Cuisine not preserved in serialization"


def test_instruction_normalization():
    """Test that instruction field validators normalize various input formats."""
    # Test 1: List input (modern format)
    recipe1 = Recipe(
        title="Test",
        description="Test",
        ingredients=["ing1"],
        instructions=["Step 1", "Step 2"],
        difficulty="Easy"
    )
    assert recipe1.instructions == ["Step 1", "Step 2"]
    
    # Test 2: String input with double newlines (legacy format)
    recipe2 = Recipe(
        title="Test",
        description="Test",
        ingredients=["ing1"],
        instructions="Step 1\n\nStep 2\n\nStep 3",
        difficulty="Easy"
    )
    assert recipe2.instructions == ["Step 1", "Step 2", "Step 3"]
    
    # Test 3: String with Windows line endings
    recipe3 = Recipe(
        title="Test",
        description="Test",
        ingredients=["ing1"],
        instructions="Step 1\r\n\r\nStep 2",
        difficulty="Easy"
    )
    assert recipe3.instructions == ["Step 1", "Step 2"]
