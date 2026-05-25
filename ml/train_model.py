"""
Random Forest Training & Evaluation
AI-Powered Career Path Recommender — Lagos State University
Author: Adegbite Moyomade Akanji

This script:
1. Loads the synthetic dataset
2. Splits features (X) from target (y)
3. Encodes the career labels into numbers
4. Splits into 80% training / 20% testing
5. Trains a Random Forest classifier
6. Evaluates with accuracy, precision, recall, F1
7. Runs 5-fold cross-validation
8. Produces a confusion matrix and feature importance plot
9. Saves the trained model for the Flask backend to use
"""

import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')  # so it works without a screen (we save images to file)
import matplotlib.pyplot as plt
import seaborn as sns
import joblib

from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import LabelEncoder
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    classification_report, confusion_matrix
)

RANDOM_SEED = 42  # same seed everywhere = reproducible results


# ============================================================
# BLOCK 1 — LOAD THE DATA
# ============================================================
print("BLOCK 1: Loading dataset...")
df = pd.read_csv('career_dataset.csv')
print(f"  Loaded {len(df)} students with {len(df.columns)-1} features each.")
print()


# ============================================================
# BLOCK 2 — SEPARATE FEATURES (X) FROM TARGET (y)
# ============================================================
# X = the 17 inputs the model learns from
# y = the career we want it to predict
print("BLOCK 2: Separating inputs (X) from output (y)...")
X = df.drop('Career', axis=1)   # everything EXCEPT the career column
y = df['Career']                # ONLY the career column
print(f"  X shape: {X.shape}  (rows=students, cols=features)")
print(f"  y shape: {y.shape}  (one career label per student)")
print()


# ============================================================
# BLOCK 3 — ENCODE CAREER LABELS INTO NUMBERS
# ============================================================
# Machine learning models work with numbers, not text.
# So "Software Developer" becomes 0, "Data Scientist" becomes 1, etc.
# We keep the encoder so we can convert back to names later.
print("BLOCK 3: Encoding career names into numbers...")
label_encoder = LabelEncoder()
y_encoded = label_encoder.fit_transform(y)
print("  Career -> Number mapping:")
for i, name in enumerate(label_encoder.classes_):
    print(f"    {i:2d} = {name}")
print()


# ============================================================
# BLOCK 4 — TRAIN/TEST SPLIT (80/20)
# ============================================================
# stratify=y_encoded ensures both sets have the same proportion
# of each career (so we don't accidentally put all teachers in test).
print("BLOCK 4: Splitting into 80% training / 20% testing...")
X_train, X_test, y_train, y_test = train_test_split(
    X, y_encoded,
    test_size=0.20,
    random_state=RANDOM_SEED,
    stratify=y_encoded
)
print(f"  Training students: {len(X_train)}")
print(f"  Testing students:  {len(X_test)}  (model never sees these during training)")
print()


# ============================================================
# BLOCK 5 — TRAIN THE RANDOM FOREST
# ============================================================
# n_estimators=200 -> build 200 decision trees
# max_depth=None   -> let trees grow until pure (RF controls overfitting itself)
# random_state     -> reproducible
print("BLOCK 5: Training the Random Forest (200 trees)...")
model = RandomForestClassifier(
    n_estimators=200,
    max_depth=None,
    min_samples_split=5,
    min_samples_leaf=2,
    random_state=RANDOM_SEED,
    n_jobs=-1 
)
model.fit(X_train, y_train) 
print("  Training complete.")
print()


# ============================================================
# BLOCK 6 — EVALUATE ON THE UNSEEN TEST SET
# ============================================================
print("BLOCK 6: Evaluating on the 20% unseen test students...")
y_pred = model.predict(X_test)

accuracy = accuracy_score(y_test, y_pred)
precision = precision_score(y_test, y_pred, average='weighted')
recall = recall_score(y_test, y_pred, average='weighted')
f1 = f1_score(y_test, y_pred, average='weighted')

print(f"  Accuracy:  {accuracy*100:.2f}%")
print(f"  Precision: {precision*100:.2f}%")
print(f"  Recall:    {recall*100:.2f}%")
print(f"  F1-Score:  {f1*100:.2f}%")
print()


# ============================================================
# BLOCK 7 — 5-FOLD CROSS-VALIDATION
# ============================================================
# Re-test the model 5 different ways to confirm it's consistently good.
print("BLOCK 7: Running 5-fold cross-validation...")
cv_scores = cross_val_score(model, X, y_encoded, cv=5, scoring='accuracy', n_jobs=-1)
print(f"  Individual fold scores: {[f'{s*100:.2f}%' for s in cv_scores]}")
print(f"  Mean CV accuracy: {cv_scores.mean()*100:.2f}% (+/- {cv_scores.std()*100:.2f}%)")
print()


# ============================================================
# BLOCK 8 — PER-CAREER DETAILED REPORT
# ============================================================
print("BLOCK 8: Per-career performance report...")
report = classification_report(
    y_test, y_pred,
    target_names=label_encoder.classes_,
    digits=3
)
print(report)


# ============================================================
# BLOCK 9 — CONFUSION MATRIX (saved as image)
# ============================================================
print("BLOCK 9: Building confusion matrix image...")
cm = confusion_matrix(y_test, y_pred)
plt.figure(figsize=(12, 10))
sns.heatmap(
    cm, annot=True, fmt='d', cmap='Blues',
    xticklabels=label_encoder.classes_,
    yticklabels=label_encoder.classes_
)
plt.title('Confusion Matrix — Random Forest Career Recommender', fontsize=14)
plt.ylabel('Actual Career')
plt.xlabel('Predicted Career')
plt.xticks(rotation=45, ha='right')
plt.yticks(rotation=0)
plt.tight_layout()
plt.savefig('confusion_matrix.png', dpi=150, bbox_inches='tight')
plt.close()
print("  Saved: confusion_matrix.png")
print()


# ============================================================
# BLOCK 10 — FEATURE IMPORTANCE (saved as image)
# ============================================================
print("BLOCK 10: Building feature importance plot...")
importances = pd.Series(model.feature_importances_, index=X.columns).sort_values(ascending=True)
plt.figure(figsize=(10, 8))
importances.plot(kind='barh', color='steelblue')
plt.title('Feature Importance — Which inputs matter most?', fontsize=14)
plt.xlabel('Importance Score')
plt.tight_layout()
plt.savefig('feature_importance.png', dpi=150, bbox_inches='tight')
plt.close()
print("  Saved: feature_importance.png")
print("  Top 5 most important features:")
for feat, imp in importances.sort_values(ascending=False).head(5).items():
    print(f"    {feat:18s}: {imp:.4f}")
print()


# ============================================================
# BLOCK 11 — SAVE THE TRAINED MODEL
# ============================================================
# We save the model AND the label encoder together, so the Flask
# backend can load them and make predictions later.
print("BLOCK 11: Saving trained model and encoder...")
joblib.dump(model, 'career_model.pkl')
joblib.dump(label_encoder, 'label_encoder.pkl')
joblib.dump(list(X.columns), 'feature_names.pkl')
print("  Saved: career_model.pkl, label_encoder.pkl, feature_names.pkl")
print()
print("=" * 60)
print("TRAINING COMPLETE")
print("=" * 60)
