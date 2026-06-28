"""
Random Forest training & evaluation for the AI-Powered Career Path Recommender.

Loads the synthetic dataset, trains a Random Forest, evaluates it (accuracy,
top-k, cross-validation, per-career report), compares it against three other
classifiers, and saves the model plus the artifacts the Flask backend needs.
"""

import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')  # headless: render charts to file, no display needed
import matplotlib.pyplot as plt
import seaborn as sns
import joblib

from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.svm import SVC
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import make_pipeline
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    classification_report, confusion_matrix, top_k_accuracy_score
)

RANDOM_SEED = 42  # fixed everywhere for reproducibility


# --- Load data ---
print("Loading dataset...")
df = pd.read_csv('career_dataset.csv')
print(f"  {len(df)} students, {len(df.columns)-1} features each.")

X = df.drop('Career', axis=1)
y = df['Career']

# Models need numeric targets; keep the encoder to map predictions back to names.
label_encoder = LabelEncoder()
y_encoded = label_encoder.fit_transform(y)

# stratify keeps each career's proportion equal across train and test.
X_train, X_test, y_train, y_test = train_test_split(
    X, y_encoded, test_size=0.20, random_state=RANDOM_SEED, stratify=y_encoded
)


# --- Train ---
print("Training Random Forest (200 trees)...")
model = RandomForestClassifier(
    n_estimators=200,
    max_depth=None,
    min_samples_split=5,
    min_samples_leaf=2,
    random_state=RANDOM_SEED,
    n_jobs=-1,
)
model.fit(X_train, y_train)


# --- Evaluate on the unseen test set ---
y_pred = model.predict(X_test)
accuracy = accuracy_score(y_test, y_pred)
precision = precision_score(y_test, y_pred, average='weighted')
recall = recall_score(y_test, y_pred, average='weighted')
f1 = f1_score(y_test, y_pred, average='weighted')
print(f"  Accuracy:  {accuracy*100:.2f}%")
print(f"  Precision: {precision*100:.2f}%")
print(f"  Recall:    {recall*100:.2f}%")
print(f"  F1-Score:  {f1*100:.2f}%")

# The app recommends the top 3, so top-3 accuracy is the metric that matches real use.
y_proba = model.predict_proba(X_test)
top2 = top_k_accuracy_score(y_test, y_proba, k=2, labels=model.classes_)
top3 = top_k_accuracy_score(y_test, y_proba, k=3, labels=model.classes_)
print(f"  Top-2 Accuracy: {top2*100:.2f}%")
print(f"  Top-3 Accuracy: {top3*100:.2f}%  (the product metric)")

cv_scores = cross_val_score(model, X, y_encoded, cv=5, scoring='accuracy', n_jobs=-1)
print(f"  5-fold CV: {cv_scores.mean()*100:.2f}% (+/- {cv_scores.std()*100:.2f}%)")

print(classification_report(y_test, y_pred, target_names=label_encoder.classes_, digits=3))


# --- Model comparison (justifies the Random Forest choice) ---
# All four classifiers are trained on the same split. RF is kept as the deployed
# model because its native feature_importances_ power the per-prediction
# explanations, at an accuracy cost within cross-validation noise on top-3.
print("Comparing candidate algorithms...")
candidate_models = {
    'Random Forest': RandomForestClassifier(
        n_estimators=200, min_samples_split=5, min_samples_leaf=2,
        random_state=RANDOM_SEED, n_jobs=-1),
    'SVM (RBF)': make_pipeline(StandardScaler(), SVC(random_state=RANDOM_SEED)),
    'Logistic Regression': make_pipeline(
        StandardScaler(), LogisticRegression(max_iter=1000, random_state=RANDOM_SEED)),
    'Gradient Boosting': GradientBoostingClassifier(random_state=RANDOM_SEED),
}

comparison_rows = []
for name, clf in candidate_models.items():
    clf.fit(X_train, y_train)
    preds = clf.predict(X_test)
    cv = cross_val_score(clf, X, y_encoded, cv=5, scoring='accuracy', n_jobs=-1)
    comparison_rows.append({
        'Model': name,
        'Test Accuracy': round(accuracy_score(y_test, preds) * 100, 2),
        'Precision': round(precision_score(y_test, preds, average='weighted') * 100, 2),
        'Recall': round(recall_score(y_test, preds, average='weighted') * 100, 2),
        'F1-Score': round(f1_score(y_test, preds, average='weighted') * 100, 2),
        'CV Mean': round(cv.mean() * 100, 2),
        'CV Std': round(cv.std() * 100, 2),
    })

comparison_df = pd.DataFrame(comparison_rows).sort_values('Test Accuracy', ascending=False)
print(comparison_df.to_string(index=False))
comparison_df.to_csv('model_comparison.csv', index=False)

metrics_to_plot = ['Test Accuracy', 'Precision', 'Recall', 'F1-Score']
plot_df = comparison_df.set_index('Model')[metrics_to_plot]
ax = plot_df.plot(kind='bar', figsize=(11, 7), colormap='viridis', edgecolor='black')
ax.set_title('Model Comparison — Career Recommender (same train/test split)', fontsize=14)
ax.set_ylabel('Score (%)')
ax.set_ylim(0, 100)
ax.set_xticklabels(plot_df.index, rotation=20, ha='right')
ax.legend(loc='lower right')
ax.grid(axis='y', linestyle='--', alpha=0.4)
plt.tight_layout()
plt.savefig('model_comparison.png', dpi=150, bbox_inches='tight')
plt.close()


# --- Confusion matrix ---
cm = confusion_matrix(y_test, y_pred)
plt.figure(figsize=(12, 10))
sns.heatmap(cm, annot=True, fmt='d', cmap='Blues',
            xticklabels=label_encoder.classes_, yticklabels=label_encoder.classes_)
plt.title('Confusion Matrix — Random Forest Career Recommender', fontsize=14)
plt.ylabel('Actual Career')
plt.xlabel('Predicted Career')
plt.xticks(rotation=45, ha='right')
plt.yticks(rotation=0)
plt.tight_layout()
plt.savefig('confusion_matrix.png', dpi=150, bbox_inches='tight')
plt.close()


# --- Feature importance ---
importances = pd.Series(model.feature_importances_, index=X.columns).sort_values(ascending=True)
plt.figure(figsize=(10, 8))
importances.plot(kind='barh', color='steelblue')
plt.title('Feature Importance — Which inputs matter most?', fontsize=14)
plt.xlabel('Importance Score')
plt.tight_layout()
plt.savefig('feature_importance.png', dpi=150, bbox_inches='tight')
plt.close()


# --- Save model + backend artifacts ---
# compress=3 keeps the pickle under GitHub's 100 MB limit and lowers RAM on Render.
joblib.dump(model, 'career_model.pkl', compress=3)
joblib.dump(label_encoder, 'label_encoder.pkl')
joblib.dump(list(X.columns), 'feature_names.pkl')

# Explainability artifacts, computed from TRAINING data only (no test-set leak):
# class_profiles = per-career mean of each feature; feature_stats = overall mean/std.
train_df = X_train.copy()
train_df['__career__'] = label_encoder.inverse_transform(y_train)
class_profiles = train_df.groupby('__career__')[list(X.columns)].mean()
feature_stats = pd.DataFrame({
    'mean': X_train.mean(),
    'std': X_train.std().replace(0, 1e-9),  # guard against divide-by-zero
})
joblib.dump(class_profiles, 'class_profiles.pkl')
joblib.dump(feature_stats, 'feature_stats.pkl')

print("Saved model + artifacts. Training complete.")
