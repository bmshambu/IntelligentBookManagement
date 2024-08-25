import pandas as pd
from sklearn.neighbors import NearestNeighbors
from sklearn.preprocessing import StandardScaler
import joblib

# Load dataset
df = pd.read_csv('train_book.csv')

# Data preprocessing
df = pd.get_dummies(df, columns=['Genre'])

# Features and target
X = df[['average_rating'] + [col for col in df.columns if col.startswith('Genre_')]]
y = df['average_rating']  # The target is not used in KNN, but can be used for more complex models

# Feature scaling
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# Train model
knn = NearestNeighbors(n_neighbors=5, algorithm='auto')
knn.fit(X_scaled)

# Save the model and scaler
joblib.dump(knn, 'knn_model.pkl')
joblib.dump(scaler, 'scaler.pkl')


print("Model and scaler saved successfully.")
