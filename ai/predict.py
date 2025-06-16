import pandas as pd
import matplotlib.pyplot as plt

# Завантаження CSV
df = pd.read_csv('rates_data.csv', encoding='cp1251')  # або 'latin1', якщо не підійде


# Обчислення прибутку (%)
df['profit_percent'] = ((df['sell_rate'] - df['buy_rate']) / df['buy_rate']) * 100

# Вивід
print(df[['date', 'buy_rate', 'sell_rate', 'profit_percent']])

# Графік
plt.plot(df['date'], df['profit_percent'], marker='o')
plt.title('Прибуток по днях (%)')
plt.xticks(rotation=45)
plt.ylabel('Прибуток %')
plt.grid(True)
plt.tight_layout()
plt.show()
