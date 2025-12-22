// Calculator State
const calculator = {
    currentOperand: '0',
    previousOperand: '',
    operation: undefined,
    waitingForNewOperand: false,
    history: []
};

// DOM Elements
const currentOperandElement = document.getElementById('current-operand');
const previousOperandElement = document.getElementById('previous-operand');
const historyListElement = document.getElementById('history-list');
const clearHistoryButton = document.getElementById('clear-history');

// Initialize calculator
function initCalculator() {
    updateDisplay();
    setupEventListeners();
    loadHistoryFromStorage();
}

// Update the display
function updateDisplay() {
    currentOperandElement.textContent = calculator.currentOperand;
    previousOperandElement.textContent = calculator.previousOperand;
    
    // Remove error class if present
    currentOperandElement.classList.remove('error');
    previousOperandElement.classList.remove('error');
}

// Clear the calculator
function clearCalculator() {
    calculator.currentOperand = '0';
    calculator.previousOperand = '';
    calculator.operation = undefined;
    calculator.waitingForNewOperand = false;
    updateDisplay();
}

// Delete the last digit
function deleteLastDigit() {
    if (calculator.currentOperand.length === 1) {
        calculator.currentOperand = '0';
    } else {
        calculator.currentOperand = calculator.currentOperand.slice(0, -1);
    }
    updateDisplay();
}

// Append a number to the current operand
function appendNumber(number) {
    // If we're waiting for a new operand, start fresh
    if (calculator.waitingForNewOperand) {
        calculator.currentOperand = number;
        calculator.waitingForNewOperand = false;
    } else {
        // Prevent multiple leading zeros
        if (calculator.currentOperand === '0' && number !== '.') {
            calculator.currentOperand = number;
        } else {
            // Prevent adding more than one decimal point
            if (number === '.' && calculator.currentOperand.includes('.')) {
                return;
            }
            calculator.currentOperand += number;
        }
    }
    updateDisplay();
}

// Choose an operation
function chooseOperation(operation) {
    // If there's already an operation pending, calculate it first
    if (calculator.previousOperand !== '') {
        calculate();
    }
    
    calculator.operation = operation;
    calculator.previousOperand = `${calculator.currentOperand} ${getOperationSymbol(operation)}`;
    calculator.waitingForNewOperand = true;
    updateDisplay();
}

// Calculate the result
function calculate() {
    let computation;
    const prev = parseFloat(calculator.previousOperand);
    const current = parseFloat(calculator.currentOperand);
    
    // Check if inputs are valid numbers
    if (isNaN(prev) || isNaN(current)) {
        showError('Invalid input');
        return;
    }
    
    // Prevent division by zero
    if (calculator.operation === 'divide' && current === 0) {
        showError('Cannot divide by zero');
        return;
    }
    
    // Perform calculation based on operation
    switch (calculator.operation) {
        case 'add':
            computation = prev + current;
            break;
        case 'subtract':
            computation = prev - current;
            break;
        case 'multiply':
            computation = prev * current;
            break;
        case 'divide':
            computation = prev / current;
            break;
        case 'percentage':
            computation = prev * (current / 100);
            break;
        default:
            return;
    }
    
    // Format the result to avoid floating point precision issues
    computation = parseFloat(computation.toFixed(10));
    
    // Create history entry
    const historyEntry = {
        expression: `${prev} ${getOperationSymbol(calculator.operation)} ${current}`,
        result: computation,
        timestamp: new Date().toLocaleTimeString()
    };
    
    // Add to history
    calculator.history.unshift(historyEntry);
    if (calculator.history.length > 10) {
        calculator.history.pop();
    }
    
    // Update calculator state
    calculator.currentOperand = computation.toString();
    calculator.previousOperand = '';
    calculator.operation = undefined;
    calculator.waitingForNewOperand = true;
    
    // Update display and history
    updateDisplay();
    updateHistoryDisplay();
    saveHistoryToStorage();
}

// Calculate percentage
function calculatePercentage() {
    const current = parseFloat(calculator.currentOperand);
    if (isNaN(current)) {
        showError('Invalid input for percentage');
        return;
    }
    
    calculator.currentOperand = (current / 100).toString();
    updateDisplay();
}

// Show error message
function showError(message) {
    calculator.currentOperand = message;
    currentOperandElement.classList.add('error');
    previousOperandElement.classList.add('error');
    
    // Reset after 2 seconds
    setTimeout(() => {
        clearCalculator();
    }, 2000);
}

// Get operation symbol for display
function getOperationSymbol(operation) {
    switch (operation) {
        case 'add': return '+';
        case 'subtract': return '\u2212';
        case 'multiply': return '\u00d7';
        case 'divide': return '\u00f7';
        case 'percentage': return '%';
        default: return '';
    }
}

// Update history display
function updateHistoryDisplay() {
    historyListElement.innerHTML = '';
    
    calculator.history.forEach(entry => {
        const li = document.createElement('li');
        li.innerHTML = `
            <strong>${entry.expression}</strong> = ${entry.result}
            <span style="float: right; font-size: 0.8rem; color: #888;">${entry.timestamp}</span>
        `;
        historyListElement.appendChild(li);
    });
}

// Save history to localStorage
function saveHistoryToStorage() {
    try {
        localStorage.setItem('calculatorHistory', JSON.stringify(calculator.history));
    } catch (e) {
        console.warn('Could not save history to localStorage:', e);
    }
}

// Load history from localStorage
function loadHistoryFromStorage() {
    try {
        const savedHistory = localStorage.getItem('calculatorHistory');
        if (savedHistory) {
            calculator.history = JSON.parse(savedHistory);
            updateHistoryDisplay();
        }
    } catch (e) {
        console.warn('Could not load history from localStorage:', e);
    }
}

// Clear history
function clearHistory() {
    calculator.history = [];
    updateHistoryDisplay();
    localStorage.removeItem('calculatorHistory');
}

// Setup event listeners
function setupEventListeners() {
    // Number buttons
    document.querySelectorAll('.btn.number[data-number]').forEach(button => {
        button.addEventListener('click', () => {
            appendNumber(button.getAttribute('data-number'));
        });
    });
    
    // Decimal button
    document.querySelector('.btn.number[data-action="decimal"]').addEventListener('click', () => {
        appendNumber('.');
    });
    
    // Operation buttons
    document.querySelectorAll('.btn.operator[data-action]').forEach(button => {
        button.addEventListener('click', () => {
            const action = button.getAttribute('data-action');
            
            switch (action) {
                case 'clear':
                    clearCalculator();
                    break;
                case 'backspace':
                    deleteLastDigit();
                    break;
                case 'percentage':
                    if (calculator.previousOperand === '') {
                        calculatePercentage();
                    } else {
                        chooseOperation('percentage');
                    }
                    break;
                case 'add':
                case 'subtract':
                case 'multiply':
                case 'divide':
                    chooseOperation(action);
                    break;
            }
        });
    });
    
    // Equals button
    document.querySelector('.btn.equals[data-action="equals"]').addEventListener('click', () => {
        calculate();
    });
    
    // Clear history button
    clearHistoryButton.addEventListener('click', clearHistory);
    
    // Keyboard support
    document.addEventListener('keydown', event => {
        const key = event.key;
        
        if (key >= '0' && key <= '9') {
            appendNumber(key);
        } else if (key === '.') {
            appendNumber('.');
        } else if (key === '+') {
            chooseOperation('add');
        } else if (key === '-') {
            chooseOperation('subtract');
        } else if (key === '*') {
            chooseOperation('multiply');
        } else if (key === '/') {
            event.preventDefault();
            chooseOperation('divide');
        } else if (key === 'Enter' || key === '=') {
            event.preventDefault();
            calculate();
        } else if (key === 'Escape' || key === 'Delete') {
            clearCalculator();
        } else if (key === 'Backspace') {
            deleteLastDigit();
        } else if (key === '%') {
            if (calculator.previousOperand === '') {
                calculatePercentage();
            } else {
                chooseOperation('percentage');
            }
        }
    });
}

// Initialize the calculator when the page loads
window.addEventListener('DOMContentLoaded', initCalculator);