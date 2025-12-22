import numpy as np
import matplotlib.pyplot as plt

class LinearRegression:
    def __init__(self):
        self.slope = None
        self.intercept = None
        self.r_squared = None
    
    def fit(self, X, y):
        """
        Fit linear regression model using normal equation
        y = mx + b
        """
        # Convert to numpy arrays if not already
        X = np.array(X)
        y = np.array(y)
        
        # Calculate slope (m) and intercept (b) using normal equation
        n = len(X)
        sum_x = np.sum(X)
        sum_y = np.sum(y)
        sum_xy = np.sum(X * y)
        sum_x2 = np.sum(X ** 2)
        
        self.slope = (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x ** 2)
        self.intercept = (sum_y - self.slope * sum_x) / n
        
        # Calculate R-squared
        y_pred = self.predict(X)
        ss_res = np.sum((y - y_pred) ** 2)
        ss_tot = np.sum((y - np.mean(y)) ** 2)
        self.r_squared = 1 - (ss_res / ss_tot)
        
        return self
    
    def predict(self, X):
        """Make predictions using the fitted model"""
        if self.slope is None or self.intercept is None:
            raise ValueError("Model must be fitted before making predictions")
        
        X = np.array(X)
        return self.slope * X + self.intercept
    
    def get_params(self):
        """Return model parameters"""
        return {
            'slope': self.slope,
            'intercept': self.intercept,
            'r_squared': self.r_squared
        }
    
    def plot(self, X, y, title="Linear Regression"):
        """Create a visualization of the regression line and data points"""
        if self.slope is None or self.intercept is None:
            raise ValueError("Model must be fitted before plotting")
        
        plt.figure(figsize=(10, 6))
        
        # Plot data points
        plt.scatter(X, y, color='blue', alpha=0.7, label='Data points')
        
        # Plot regression line
        X_line = np.linspace(min(X), max(X), 100)
        y_line = self.predict(X_line)
        plt.plot(X_line, y_line, color='red', linewidth=2, label=f'Regression line: y = {self.slope:.4f}x + {self.intercept:.4f}')
        
        plt.xlabel('X')
        plt.ylabel('y')
        plt.title(f'{title} (R\u00b2 = {self.r_squared:.4f})')
        plt.legend()
        plt.grid(True, alpha=0.3)
        plt.show()

def example_usage():
    """Example demonstrating how to use the LinearRegression class"""
    print("=== Linear Regression Example ===")
    
    # Generate sample data
    np.random.seed(42)
    X = np.array([1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
    y = 2.5 * X + 1.2 + np.random.normal(0, 1, len(X))
    
    print(f"X values: {X}")
    print(f"y values: {y}")
    
    # Create and fit model
    model = LinearRegression()
    model.fit(X, y)
    
    # Get parameters
    params = model.get_params()
    print(f"Model Parameters:")
    print(f"Slope (m): {params['slope']:.4f}")
    print(f"Intercept (b): {params['intercept']:.4f}")
    print(f"R-squared: {params['r_squared']:.4f}")
    
    # Make predictions
    X_test = np.array([11, 12, 13])
    predictions = model.predict(X_test)
    print(f"Predictions for X = {X_test}:")
    for x, y_pred in zip(X_test, predictions):
        print(f"  f({x}) = {y_pred:.4f}")
    
    # Plot results
    model.plot(X, y, title="Linear Regression Example")
    
    return model

if __name__ == "__main__":
    # Run example when script is executed directly
    example_usage()