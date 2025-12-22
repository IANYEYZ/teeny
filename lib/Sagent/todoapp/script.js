// Simple Todo App - JavaScript
// Works with existing index.html and style.css

// Todo item data structure
// {
//   id: number (unique identifier),
//   text: string (task description),
//   completed: boolean,
//   createdAt: string (ISO date string)
// }

// Global variables
let todos = [];
let nextId = 1;
let currentFilter = 'all';

// DOM Elements
let taskInput;
let addBtn;
let taskList;
let filterButtons;
let clearCompletedBtn;
let clearAllBtn;
let emptyState;
let totalTasksSpan;
let completedTasksSpan;
let pendingTasksSpan;

// Initialize the application
function init() {
    // Get DOM elements
    taskInput = document.getElementById('taskInput');
    addBtn = document.getElementById('addBtn');
    taskList = document.getElementById('taskList');
    filterButtons = document.querySelectorAll('.filter-btn');
    clearCompletedBtn = document.getElementById('clearCompleted');
    clearAllBtn = document.getElementById('clearAll');
    emptyState = document.getElementById('emptyState');
    totalTasksSpan = document.getElementById('totalTasks');
    completedTasksSpan = document.getElementById('completedTasks');
    pendingTasksSpan = document.getElementById('pendingTasks');
    
    // Load todos from localStorage
    loadTodos();
    
    // Set up event listeners
    setupEventListeners();
    
    // Render initial todos
    renderTodos();
    
    // Update empty state
    updateEmptyState();
}

// Load todos from localStorage
function loadTodos() {
    const storedTodos = localStorage.getItem('todos');
    if (storedTodos) {
        todos = JSON.parse(storedTodos);
        // Find the highest ID to set nextId
        if (todos.length > 0) {
            nextId = Math.max(...todos.map(todo => todo.id)) + 1;
        }
    }
}

// Save todos to localStorage
function saveTodos() {
    localStorage.setItem('todos', JSON.stringify(todos));
}

// Set up all event listeners
function setupEventListeners() {
    // Add task button click
    addBtn.addEventListener('click', addTask);
    
    // Enter key in input field
    taskInput.addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            addTask();
        }
    });
    
    // Filter buttons
    filterButtons.forEach(button => {
        button.addEventListener('click', function() {
            // Remove active class from all filter buttons
            filterButtons.forEach(btn => btn.classList.remove('active'));
            // Add active class to clicked button
            this.classList.add('active');
            
            currentFilter = this.dataset.filter;
            renderTodos();
        });
    });
    
    // Clear completed button
    clearCompletedBtn.addEventListener('click', clearCompletedTasks);
    
    // Clear all button
    clearAllBtn.addEventListener('click', clearAllTasks);
}

// Add a new task
function addTask() {
    const text = taskInput.value.trim();
    
    if (text === '') {
        alert('Please enter a task');
        return;
    }
    
    const newTask = {
        id: nextId++,
        text: text,
        completed: false,
        createdAt: new Date().toISOString()
    };
    
    todos.push(newTask);
    saveTodos();
    renderTodos();
    updateEmptyState();
    
    // Clear input and focus
    taskInput.value = '';
    taskInput.focus();
}

// Render todos to the DOM
function renderTodos() {
    // Clear current list
    taskList.innerHTML = '';
    
    // Filter todos based on current filter
    let filteredTodos = todos;
    if (currentFilter === 'pending') {
        filteredTodos = todos.filter(todo => !todo.completed);
    } else if (currentFilter === 'completed') {
        filteredTodos = todos.filter(todo => todo.completed);
    }
    
    // Create task items
    filteredTodos.forEach(todo => {
        const taskItem = createTaskElement(todo);
        taskList.appendChild(taskItem);
    });
    
    // Update counters
    updateCounters();
}

// Create a single task element
function createTaskElement(todo) {
    const li = document.createElement('li');
    li.className = `task-item ${todo.completed ? 'completed' : ''}`;
    li.dataset.id = todo.id;
    
    // Checkbox
    const checkbox = document.createElement('input');
    checkbox.type = 'checkbox';
    checkbox.className = 'task-checkbox';
    checkbox.checked = todo.completed;
    checkbox.addEventListener('change', () => toggleTaskCompletion(todo.id));
    
    // Task text
    const textSpan = document.createElement('span');
    textSpan.className = 'task-text';
    textSpan.textContent = todo.text;
    
    // Double-click to edit
    textSpan.addEventListener('dblclick', () => enableEditMode(todo.id, textSpan));
    
    // Actions container
    const actionsDiv = document.createElement('div');
    actionsDiv.className = 'task-actions';
    
    // Edit button
    const editBtn = document.createElement('button');
    editBtn.className = 'edit-btn';
    editBtn.innerHTML = '<i class="fas fa-edit"></i>';
    editBtn.title = 'Edit task';
    editBtn.addEventListener('click', () => enableEditMode(todo.id, textSpan));
    
    // Delete button
    const deleteBtn = document.createElement('button');
    deleteBtn.className = 'delete-btn';
    deleteBtn.innerHTML = '<i class="fas fa-trash"></i>';
    deleteBtn.title = 'Delete task';
    deleteBtn.addEventListener('click', () => deleteTask(todo.id));
    
    // Assemble actions
    actionsDiv.appendChild(editBtn);
    actionsDiv.appendChild(deleteBtn);
    
    // Assemble task item
    li.appendChild(checkbox);
    li.appendChild(textSpan);
    li.appendChild(actionsDiv);
    
    return li;
}

// Enable edit mode for a task
function enableEditMode(taskId, textElement) {
    const taskItem = textElement.parentElement;
    const currentText = textElement.textContent;
    
    // Create input field
    const input = document.createElement('input');
    input.type = 'text';
    input.className = 'edit-input';
    input.value = currentText;
    
    // Replace text with input
    textElement.replaceWith(input);
    input.focus();
    input.select();
    
    // Add editing class
    taskItem.classList.add('editing');
    
    // Save on Enter or blur
    const saveEdit = () => {
        const newText = input.value.trim();
        if (newText && newText !== currentText) {
            editTask(taskId, newText);
        } else {
            // Restore original text
            input.replaceWith(textElement);
            taskItem.classList.remove('editing');
        }
    };
    
    input.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            saveEdit();
        }
    });
    
    input.addEventListener('blur', saveEdit);
}

// Edit task text
function editTask(taskId, newText) {
    const taskIndex = todos.findIndex(todo => todo.id === taskId);
    if (taskIndex !== -1 && newText.trim() !== '') {
        todos[taskIndex].text = newText.trim();
        saveTodos();
        renderTodos();
    }
}

// Toggle task completion status
function toggleTaskCompletion(taskId) {
    const taskIndex = todos.findIndex(todo => todo.id === taskId);
    if (taskIndex !== -1) {
        todos[taskIndex].completed = !todos[taskIndex].completed;
        saveTodos();
        renderTodos();
        updateEmptyState();
    }
}

// Delete a task
function deleteTask(taskId) {
    if (confirm('Are you sure you want to delete this task?')) {
        todos = todos.filter(todo => todo.id !== taskId);
        saveTodos();
        renderTodos();
        updateEmptyState();
    }
}

// Clear all completed tasks
function clearCompletedTasks() {
    const completedCount = todos.filter(todo => todo.completed).length;
    
    if (completedCount === 0) {
        alert('No completed tasks to clear');
        return;
    }
    
    if (confirm(`Clear ${completedCount} completed task(s)?`)) {
        todos = todos.filter(todo => !todo.completed);
        saveTodos();
        renderTodos();
        updateEmptyState();
    }
}

// Clear all tasks
function clearAllTasks() {
    if (todos.length === 0) {
        alert('No tasks to clear');
        return;
    }
    
    if (confirm(`Clear all ${todos.length} task(s)? This cannot be undone.`)) {
        todos = [];
        nextId = 1;
        saveTodos();
        renderTodos();
        updateEmptyState();
    }
}

// Update task counters
function updateCounters() {
    const totalCount = todos.length;
    const completedCount = todos.filter(todo => todo.completed).length;
    const pendingCount = totalCount - completedCount;
    
    totalTasksSpan.textContent = `Total: ${totalCount}`;
    completedTasksSpan.textContent = `Completed: ${completedCount}`;
    pendingTasksSpan.textContent = `Pending: ${pendingCount}`;
}

// Update empty state visibility
function updateEmptyState() {
    const filteredTodos = getFilteredTodos();
    
    if (filteredTodos.length === 0) {
        emptyState.style.display = 'block';
    } else {
        emptyState.style.display = 'none';
    }
}

// Get todos based on current filter
function getFilteredTodos() {
    if (currentFilter === 'pending') {
        return todos.filter(todo => !todo.completed);
    } else if (currentFilter === 'completed') {
        return todos.filter(todo => todo.completed);
    }
    return todos;
}

// Utility function to format date
function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', { 
        weekday: 'short', 
        year: 'numeric', 
        month: 'short', 
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    });
}

// Initialize the app when DOM is loaded
document.addEventListener('DOMContentLoaded', init);

// Export functions for debugging if needed
window.todoApp = {
    todos,
    addTask,
    toggleTaskCompletion,
    deleteTask,
    clearCompletedTasks,
    clearAllTasks,
    saveTodos,
    loadTodos,
    renderTodos
};