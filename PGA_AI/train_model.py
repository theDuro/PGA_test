import numpy as np
from sklearn.linear_model import LinearRegression
import joblib

# 1️⃣ Generujemy dane treningowe (1000 par 6->6)
N = 1000
X = np.random.rand(N, 6).astype(np.float32)
Y = (2 * X + 1).astype(np.float32)  # przykład: y = 2*x + 1

# 2️⃣ Tworzymy model i trenujemy
model = LinearRegression()
model.fit(X, Y)

# 3️⃣ Zapisujemy model do pliku
joblib.dump(model, "model.joblib")
print("Model zapisany jako model.joblib")