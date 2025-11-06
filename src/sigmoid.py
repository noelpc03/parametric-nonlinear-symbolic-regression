import numpy as np
from pysr import PySRRegressor

# ----------------------------
# 1. Generamos datos de ejemplo (ruido puro)
# ----------------------------
np.random.seed(0)
X = np.linspace(-3, 3, 100).reshape(-1, 1)

# Generamos y como ruido puro (sin ninguna función subyacente)
y = np.random.randn(len(X))
y_true = y  # No hay función "verdadera" en este caso

# ---------------------------------
# 2. Definimos la pérdida sigmoidal
# ---------------------------------
def sigmoid_loss(y_true, y_pred, epsilon=0.1, k=10):
    """
    Pérdida suave basada en una sigmoide.
    Cuanto más cerca está el punto (|y - f(x)| <= ε), menor penalización.
    """
    diff = np.abs(y_true - y_pred)
    # Queremos una función que dé 1 cuando el punto está bien ajustado
    # y 0 cuando está lejos
    penalties = 1 / (1 + np.exp(-k * (epsilon - diff)))
    # La pérdida será 1 - cobertura media
    return 1 - np.mean(penalties)

# -----------------------------------------
# 3. Adaptamos PySR para usar métrica sigmoidal
# -----------------------------------------
# Definimos la función de pérdida sigmoid en Julia
# Esta función penaliza menos los puntos que están dentro del epsilon
# y penaliza más los que están fuera
k = 10  # Pendiente de la transición (qué tan suave es la transición)
epsilon = 0.05  # Umbral de tolerancia

# La función devuelve un valor bajo (~0) cuando el punto está dentro del epsilon
# y un valor alto (~1) cuando está fuera
# Fórmula: sigmoid(|error| - epsilon)
loss_function = f"sigmoid_loss(prediction, target) = 1 / (1 + exp(-{k} * (abs(target - prediction) - {epsilon})))"

model = PySRRegressor(
    niterations=100,                  # número de iteraciones evolutivas
    populations=4,
    elementwise_loss=loss_function,   # función de pérdida sigmoidal
    model_selection="best",           # selecciona mejor modelo final
    variable_names=["x"],
    # Permitimos operaciones comunes
    unary_operators=["sin", "cos", "exp", "log"],
    binary_operators=["+", "-", "*", "/"],
)

# Entrenamos el modelo
model.fit(X, y)

# ---------------------------------------
# 4. Mostramos la mejor ecuación encontrada
# ---------------------------------------
print("\n=== Mejor ecuación simbólica encontrada ===")
print(model.get_best())

# ---------------------------------------
# 5. Visualización
# ---------------------------------------
import matplotlib.pyplot as plt

y_pred = model.predict(X)

plt.figure(figsize=(8, 5))
plt.scatter(X, y, label="Datos", s=20)
plt.plot(X, y_true, color="green", lw=2, label="Función real")
plt.plot(X, y_pred, color="red", lw=2, label="Función simbólica")
plt.legend()
plt.title("Regresión Simbólica con Pérdida Sigmoidal Suave")
plt.show()
