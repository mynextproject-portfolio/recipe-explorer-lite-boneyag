#!/usr/bin/env python3
"""Verify the recipe schema and validator logic works correctly."""

import sys
from app.models import Recipe, RecipeCreate

# Test data matching the test fixture
test_data = {
    "title": "Test Recipe",
    "description": "A test recipe",
    "ingredients": ["ingredient 1", "ingredient 2"],
    "instructions": ["First, do step 1.", "Then, do step 2."],
    "tags": ["test"],
    "region": "Test Region",
    "cuisine": "Test Cuisine",
    "difficulty": "Easy"
}

try:
    # Create a RecipeCreate from test data
    recipe_create = RecipeCreate(**test_data)
    print("✓ RecipeCreate validation passed")
    print(f"  Instructions type: {type(recipe_create.instructions)}")
    print(f"  Instructions: {recipe_create.instructions}")
    
    # Convert to Recipe (this is what storage does)
    recipe = Recipe(**recipe_create.model_dump())
    print("✓ Recipe creation passed")
    print(f"  Instructions type: {type(recipe.instructions)}")
    print(f"  Instructions: {recipe.instructions}")
    
    # Serialize to dict (what the API returns)
    recipe_dict = recipe.model_dump()
    print("✓ Recipe serialization passed")
    print(f"  Serialized instructions: {recipe_dict['instructions']}")
    print(f"  Serialized region: {recipe_dict['region']}")
    print(f"  Serialized cuisine: {recipe_dict['cuisine']}")
    
    # Verify the roundtrip
    assert recipe_dict['instructions'] == test_data['instructions'], "Instructions don't match!"
    assert recipe_dict['region'] == test_data['region'], "Region doesn't match!"
    assert recipe_dict['cuisine'] == test_data['cuisine'], "Cuisine doesn't match!"
    
    print("\n✓ All schema validations passed!")
    sys.exit(0)
    
except Exception as e:
    print(f"✗ Schema validation failed: {e}", file=sys.stderr)
    import traceback
    traceback.print_exc()
    sys.exit(1)
