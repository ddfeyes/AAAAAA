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
    total_net_pnl = 0
    total_gross_pnl = 0
    total_fees = 0
    total_orders = 0

    for i in range(num_tasks):
        count = count_executed_orders(volatility, iterations, spreads[i], distances[i])
        volume_total = count * volumes[i]

        gross_pnl_percent = spreads[i] - distances[i]  # without fees
        net_pnl_percent = gross_pnl_percent - 2 * fee

        gross_pnl_dollars = (gross_pnl_percent / 100) * (volume_total / 2)
        net_pnl_dollars = (net_pnl_percent / 100) * (volume_total / 2)
        fee_dollars = (2 * fee / 100) * (volume_total / 2)

        total_volume += volume_total
        total_net_pnl += net_pnl_dollars
        total_gross_pnl += gross_pnl_dollars
        total_fees += fee_dollars
        total_orders += count

        avg_volume_per_trade = volume_total / count if count > 0 else 0

        st.write(f"Task {i+1}: Spread = {spreads[i]}%, Distance = {distances[i]}%, Volume = {volumes[i]} → 🧮 {count} orders executed")
        st.write(f"📦 Total Volume: ${volume_total:.2f}, 💸 Fees: ${fee_dollars:.4f}")
        st.write(f"📈 Gross PNL: ${gross_pnl_dollars:.4f}, Net PNL: ${net_pnl_dollars:.4f} (Per-trade yield: {net_pnl_percent:.2f}%)")

    st.markdown("---")
    st.header("Summary")
    avg_net_yield = (total_net_pnl / (total_volume / 2)) * 100 if total_volume > 0 else 0
    avg_liquidity_dollars = (2 / (2 * volatility)) * total_volume if volatility > 0 else 0
    avg_volume_per_trade_total = total_volume / total_orders if total_orders > 0 else 0
    net_pnl_per_trade = (avg_net_yield / 100) * (avg_volume_per_trade_total / 2)

    st.write(f"🔢 Total Volume of All Orders: ${total_volume:.2f}")
    st.write(f"💸 Total Fees: ${total_fees:.4f}")
    st.write(f"📈 Gross PNL (before fees): ${total_gross_pnl:.4f}")
    st.write(f"✅ Net PNL (after fees): ${total_net_pnl:.4f}")
    st.write(f"📊 Average Yield per Orderbook: {avg_net_yield:.2f}%")
    st.write(f"📉 Average Volume per Trade: ${avg_volume_per_trade_total:.2f}, Net PNL per Trade: ${net_pnl_per_trade:.4f}")
    st.write(f"🌊 Avg Liquidity Within 2% Range (volume-based): ${avg_liquidity_dollars:.2f}")
