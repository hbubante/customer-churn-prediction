import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import RandomizedSearchCV
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix
import joblib
import os
from pathlib import Path
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score

def run():
    root_path = Path(__file__).resolve().parents[1]
    processed_path = root_path / "data" / "processed"
    models_path = root_path / "models"

    # Check if preprocessed data exists
    if not all((processed_path / f).exists() for f in ["processed_train.csv", "processed_test.csv", "processed_val.csv"]):
        print("Preprocessed data not found! Please run the preprocessing script first.")
        exit()

    print("Preprocessed data found. Proceeding with model training and hyperparameter tuning...\n")

    # Load preprocessed data
    train_df = pd.read_csv(processed_path / "processed_train.csv")
    val_df = pd.read_csv(processed_path / "processed_val.csv")

    # Split into features (X) and target (y)
    X_train, y_train = train_df.drop("Churn", axis=1), train_df["Churn"]
    X_val, y_val = val_df.drop("Churn", axis=1), val_df["Churn"]

    # Define hyperparameter grid
    param_grid = {
        'n_estimators': [100, 200, 300],
        'max_depth': [10, 20, None],
        'min_samples_split': [2, 5, 10],
        'min_samples_leaf': [1, 2, 4]
    }

    # Perform Randomized Search for Hyperparameter Tuning
    rf_model = RandomForestClassifier(random_state=42)
    random_search = RandomizedSearchCV(rf_model, param_grid, n_iter=10, cv=3, scoring='accuracy', n_jobs=-1, random_state=42)
    random_search.fit(X_train, y_train)

    # Get best model from tuning
    best_rf_model = random_search.best_estimator_
    print("Best model hyperparameters:", random_search.best_params_, "\n")

    # Predictions
    y_pred_val = best_rf_model.predict(X_val)

    # Evaluate model
    print("Validation Set Evaluation:")
    print(f"Accuracy: {accuracy_score(y_val, y_pred_val):.4f}")
    print(f"Precision: {precision_score(y_val, y_pred_val):.4f}")
    print(f"Recall: {recall_score(y_val, y_pred_val):.4f}")
    print(f"F1 Score: {f1_score(y_val, y_pred_val):.4f}\n")
    print("Confusion Matrix:")
    print(confusion_matrix(y_val, y_pred_val), "\n")

    # For plotting
    accuracy = accuracy_score(y_val, y_pred_val)
    precision = precision_score(y_val, y_pred_val)
    recall = recall_score(y_val, y_pred_val)
    f1 = f1_score(y_val, y_pred_val)

    # Metrics dictionary
    metrics = {
        'Accuracy': accuracy,
        'Precision': precision,
        'Recall': recall,
        'F1 Score': f1
    }

    # Plot
    plt.figure(figsize=(8, 6))
    sns.barplot(x=list(metrics.keys()), y=list(metrics.values()), palette="viridis")
    plt.ylim(0, 1)
    plt.title("Model Evaluation Metrics")
    plt.ylabel("Score")
    plt.grid(axis='y')
    plt.tight_layout()
    plt.show()


    # Save best model
    joblib.dump(best_rf_model, models_path / "random_forest_model.pkl")
    print("Best model trained and saved as 'random_forest_model.pkl.'")