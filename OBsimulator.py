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
        executed_this_cycle -= 1  # the last one is not executed

        total_executed_orders += executed_this_cycle

    return total_executed_orders

# UI
st.title("Order Execution Simulator")
st.markdown("---")

st.header("General Parameters")
volatility = st.number_input("Volatility (%)", min_value=0.1, step=0.1, value=5.0)
iterations = st.number_input("Iterations", min_value=1, step=1, value=1)
fee = st.number_input("Fee (%)", min_value=0.0, step=0.01, value=0.05)

st.header("Task Parameters")
num_tasks = st.number_input("How many tasks to calculate", min_value=1, step=1, value=1)

spreads = []
distances = []
volumes = []

for i in range(num_tasks):
    st.subheader(f"Task {i+1}")
    col1, col2, col3 = st.columns(3)
    with col1:
        spread = st.number_input(f"Spread (%) - Task {i+1}", key=f"spread_{i}", min_value=0.01, step=0.01, value=0.6)
    with col2:
        distance = st.number_input(f"Distance (%) - Task {i+1}", key=f"dist_{i}", min_value=0.01, step=0.01, value=0.2)
    with col3:
        volume = st.number_input(f"Order Volume ($) - Task {i+1}", key=f"volume_{i}", min_value=0.01, step=0.01, value=10.0)
    spreads.append(spread)
    distances.append(distance)
    volumes.append(volume)

if st.button("Calculate"):
    st.markdown("---")
    st.header("Results")
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

        st.write(f"Task {i+1}: Spread = {spreads[i]}%, Distance = {distances[i]}%, Volume = {volumes[i]} → 🧮 {count} orders executed")
        st.write(f"📦 Total Volume: ${volume_total:.2f}, 💰 Profit: ${profit_dollars:.4f} (Profitability: {profit_percent:.2f}%)")

    st.markdown("---")
    st.header("Summary")
    avg_percent = total_percent_sum / num_tasks if num_tasks > 0 else 0
    avg_liquidity_dollars = (2 / (2 * volatility)) * total_volume if volatility > 0 else 0

    st.write(f"🔢 Total Volume of All Orders: ${total_volume:.2f}")
    st.write(f"💰 Total Profit: ${total_profit:.4f}")
    st.write(f"📈 Average Profitability: {avg_percent:.2f}%")
    st.write(f"🌊 Average Liquidity Within 2% Range (based on volume): ${avg_liquidity_dollars:.2f}")
