import streamlit as st

def count_executed_orders(volatility_percent, iterations, spread, distance):
    start_ask = round(spread / 2, 10)
    step = distance
    upper_limit = volatility_percent
    lower_limit = -volatility_percent
    total_executed_orders = 0

    for _ in range(iterations):
        asks = []
        bids = []

        price = start_ask
        while price <= upper_limit:
            asks.append(round(price, 10))
            new_bid = round(price - (spread - distance), 10)
            bids.append(new_bid)
            price += step

        bids_executed = [b for b in bids if lower_limit <= b <= upper_limit]
        new_asks = [round(b + (spread - distance), 10) for b in bids_executed]
        asks_executed = [a for a in new_asks if lower_limit <= a <= 0]

        executed_this_cycle = len(asks) + len(bids_executed) + len(asks_executed)
        executed_this_cycle -= 1  # последний не исполняется

        total_executed_orders += executed_this_cycle

    return total_executed_orders

# UI
st.title("Симулятор исполнения ордеров")
st.markdown("---")

st.header("Основные параметры")
volatility = st.number_input("Волатильность (%)", min_value=0.1, step=0.1, value=5.0)
iterations = st.number_input("Итерации", min_value=1, step=1, value=1)
fee = st.number_input("Комиссия (fee, %)", min_value=0.0, step=0.01, value=0.05)

st.header("Параметры задач")
num_tasks = st.number_input("Сколько задач рассчитать", min_value=1, step=1, value=1)

spreads = []
distances = []
volumes = []

for i in range(num_tasks):
    st.subheader(f"Задача {i+1}")
    col1, col2, col3 = st.columns(3)
    with col1:
        spread = st.number_input(f"Spread (%) - задача {i+1}", key=f"spread_{i}", min_value=0.01, step=0.01, value=0.6)
    with col2:
        distance = st.number_input(f"Distance (%) - задача {i+1}", key=f"dist_{i}", min_value=0.01, step=0.01, value=0.2)
    with col3:
        volume = st.number_input(f"Объём одного ордера ($) - задача {i+1}", key=f"volume_{i}", min_value=0.01, step=0.01, value=10.0)
    spreads.append(spread)
    distances.append(distance)
    volumes.append(volume)

if st.button("Рассчитать"):
    st.markdown("---")
    st.header("Результаты")
    total_volume = 0
    total_profit = 0
    total_percent_sum = 0
    total_orders = 0

    for i in range(num_tasks):
        count = count_executed_orders(volatility, iterations, spreads[i], distances[i])
        volume_total = count * volumes[i]
        profit_percent = spreads[i] - distances[i] - 2 * fee
        profit_dollars = (profit_percent / 100) * (volume_total / 2)

        total_volume += volume_total
        total_profit += profit_dollars
        total_percent_sum += profit_percent
        total_orders += count

        st.write(f"Задача {i+1}: Spread = {spreads[i]}%, Distance = {distances[i]}%, Volume = {volumes[i]} → 🧮 {count} ордеров исполнено")
        st.write(f"📦 Общий объём: ${volume_total:.2f}, 💰 Прибыль: ${profit_dollars:.4f} (доходность: {profit_percent:.2f}%)")

    st.markdown("---")
    st.header("Сводка по всем задачам")
    avg_percent = total_percent_sum / num_tasks if num_tasks > 0 else 0
    avg_liquidity_dollars = (2 / (2 * volatility)) * total_volume if volatility > 0 else 0

    st.write(f"🔢 Общий объём всех ордеров: ${total_volume:.2f}")
    st.write(f"💰 Общая прибыль: ${total_profit:.4f}")
    st.write(f"📈 Средний % дохода: {avg_percent:.2f}%")
    st.write(f"🌊 Средняя ликвидность в пределах 2% (по объёму): ${avg_liquidity_dollars:.2f}")
