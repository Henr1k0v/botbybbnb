import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, r2_score
import joblib  # для збереження моделі

# Читання даних
df = pd.read_csv('rates_data.csv', sep=',', encoding='utf-8')
df.columns = df.columns.str.strip()
df = df.dropna(axis=1, how='all')

# Обчислення прибутку
df['profit_percent'] = ((df['sell_rate'] - df['buy_rate']) / df['buy_rate']) * 100

# Ознаки та ціль
X = df[['buy_rate', 'sell_rate']]
y = df['profit_percent']

# Розділення
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Навчання моделі
model = LinearRegression()
model.fit(X_train, y_train)

# Прогноз
y_pred = model.predict(X_test)

# Метрики
print("MSE:", mean_squared_error(y_test, y_pred))
print("R2 Score:", r2_score(y_test, y_pred))

# Приклад прогнозу
print("\nSample prediction:")
print(model.predict([[40.5, 44.1]]))  # можна замінити значення на актуальні

# Збереження моделі у файл
joblib.dump(model, 'profit_predictor.pkl')
print("\nМодель успішно збережена у файл profit_predictor.pkl")
