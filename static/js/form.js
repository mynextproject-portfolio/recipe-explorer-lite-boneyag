// Dynamic form fields for ingredients and instructions

var MAX_INGREDIENTS = 20;
const maxInstructions = 15;

document.addEventListener('DOMContentLoaded', function() {
    
    // Ingredients functionality
    const ingredientsContainer = document.getElementById('ingredients-container');
    const addIngredientBtn = document.getElementById('add-ingredient');
    
    if (addIngredientBtn) {
        addIngredientBtn.addEventListener('click', function() {
            addIngredient();
        });
    }
    
    if (ingredientsContainer) {
        // Add event listeners to existing remove buttons
        ingredientsContainer.addEventListener('click', function(e) {
            if (e.target.classList.contains('remove-ingredient')) {
                removeIngredient(e.target);
            }
        });
    }
    
    // Instructions functionality  
    const instructionsContainer = document.getElementById('instructions-container');
    const addInstructionBtn = document.getElementById('add-instruction');
    
    if (addInstructionBtn) {
        addInstructionBtn.addEventListener('click', function() {
            addInstruction();
        });
    }
    
    if (instructionsContainer) {
        // Add event listeners to existing instruction controls
        instructionsContainer.addEventListener('click', function(e) {
            if (e.target.classList.contains('remove-instruction')) {
                removeInstruction(e.target);
            }
        });

        instructionsContainer.addEventListener('dragstart', function(e) {
            const handle = e.target.closest('.instruction-drag-handle');
            if (!handle) return;

            const instructionItem = handle.closest('.instruction-item');
            if (!instructionItem) return;

            instructionItem.classList.add('dragging');
            if (e.dataTransfer) {
                e.dataTransfer.effectAllowed = 'move';
                e.dataTransfer.setData('text/plain', '');
            }
        });

        instructionsContainer.addEventListener('dragover', function(e) {
            e.preventDefault();

            const draggedItem = instructionsContainer.querySelector('.instruction-item.dragging');
            if (!draggedItem) return;

            const afterElement = getDragAfterElement(instructionsContainer, e.clientY);
            if (afterElement == null) {
                instructionsContainer.appendChild(draggedItem);
            } else {
                instructionsContainer.insertBefore(draggedItem, afterElement);
            }

            updateInstructionNumbers();
        });

        instructionsContainer.addEventListener('dragend', function() {
            const draggedItem = instructionsContainer.querySelector('.instruction-item.dragging');
            if (draggedItem) {
                draggedItem.classList.remove('dragging');
            }
            updateInstructionNumbers();
        });
    }
    
    // Update instruction numbers when page loads
    updateInstructionNumbers();
});

function addIngredient() {
    const container = document.getElementById('ingredients-container');
    
    // Check max ingredients (not enforced in backend)
    var currentCount = container.children.length;
    if (currentCount >= MAX_INGREDIENTS) {
        alert("Maximum " + MAX_INGREDIENTS + " ingredients allowed");
        return;
    }
    
    const ingredientDiv = document.createElement('div');
    ingredientDiv.className = 'ingredient-item mb-2';
    
    ingredientDiv.innerHTML = `
        <div class="input-group">
            <input type="text" class="form-control ingredient-input" 
                   placeholder="Enter ingredient..." required>
            <button type="button" class="btn btn-outline-danger remove-ingredient">Remove</button>
        </div>
    `;
    
    container.appendChild(ingredientDiv);
}

function removeIngredient(button) {
    const ingredientItem = button.closest('.ingredient-item');
    const container = document.getElementById('ingredients-container');
    
    // Don't remove if it's the only ingredient
    if (container.children.length > 1) {
        ingredientItem.remove();
    }
}

function addInstruction() {
    const container = document.getElementById('instructions-container');
    if (!container) return;

    const currentCount = container.children.length;
    if (currentCount >= maxInstructions) {
        alert("Maximum " + maxInstructions + " steps allowed");
        return;
    }

    const instructionDiv = document.createElement('div');
    instructionDiv.className = 'instruction-item mb-2';
    instructionDiv.setAttribute('draggable', 'true');

    instructionDiv.innerHTML = `
        <div class="row g-2 align-items-start">
            <div class="col-auto pt-2 d-flex flex-column align-items-center gap-2">
                <button type="button" class="btn btn-outline-secondary btn-sm instruction-drag-handle" draggable="true" aria-label="Drag to reorder">
                    Drag
                </button>
                <span class="instruction-number badge bg-primary">${currentCount + 1}</span>
            </div>
            <div class="col">
                <textarea class="form-control instruction-input" name="instruction_steps" rows="2" 
                          placeholder="Enter instruction step..." required></textarea>
            </div>
            <div class="col-auto pt-1">
                <button type="button" class="btn btn-outline-danger remove-instruction">Remove</button>
            </div>
        </div>
    `;
    
    container.appendChild(instructionDiv);
    updateInstructionNumbers();
}

function removeInstruction(button) {
    const instructionItem = button.closest('.instruction-item');
    const container = document.getElementById('instructions-container');
    if (!container || !instructionItem) return;
    
    // Don't remove if it's the only instruction
    if (container.children.length > 1) {
        instructionItem.remove();
        updateInstructionNumbers();
    }
}

function getDragAfterElement(container, y) {
    const draggableElements = [...container.querySelectorAll('.instruction-item:not(.dragging)')];

    return draggableElements.reduce(function(closest, child) {
        const box = child.getBoundingClientRect();
        const offset = y - box.top - box.height / 2;

        if (offset < 0 && offset > closest.offset) {
            return { offset: offset, element: child };
        }

        return closest;
    }, { offset: Number.NEGATIVE_INFINITY, element: null }).element;
}

function updateInstructionNumbers() {
    const container = document.getElementById('instructions-container');
    if (!container) return;
    
    const instructionItems = container.querySelectorAll('.instruction-item');
    instructionItems.forEach((item, index) => {
        const numberSpan = item.querySelector('.instruction-number');
        if (numberSpan) {
            numberSpan.textContent = index + 1;
        }
    });
}
