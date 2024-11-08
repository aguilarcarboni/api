from app.helpers.logger import logger

logger.announcement('Initializing Tools.', 'info')
logger.announcement('Tools initialized successfully', 'success')

def calculate_energy_consumption(watt_hours: float) -> dict:
    """
    Calculate energy consumption and cost based on given watt-hours.
    
    Args:
    watt_hours (float): The watt-hours of the machine.
    
    Returns:
    dict: A dictionary containing daily and monthly consumption, and total cost.
    """
    # Convert Wh to kWh and calculate monthly consumption
    daily_kwh = watt_hours / 1000 * 24
    monthly_kwh = daily_kwh * 30  # Assuming 30 days per month

    # Define consumption blocks
    blocks = [
        (30, 2138.40),  # Fixed charge for 0-30 kWh
        (170, 71.28),   # 31-200 kWh
        (100, 109.39),  # 201-300 kWh
        (float('inf'), 113.09)  # > 300 kWh
    ]

    total_cost = 0
    remaining_kwh = monthly_kwh

    for limit, rate in blocks:
        if remaining_kwh <= 0:
            break
        
        if limit == 30:  # Fixed charge for first block
            total_cost += rate
            remaining_kwh -= limit
        else:
            consumed = min(remaining_kwh, limit)
            print(f"Consumed: {consumed} kWh")
            total_cost += consumed * rate
            remaining_kwh -= consumed

    return {
        "daily_consumption_kwh": round(daily_kwh, 2),
        "monthly_consumption_kwh": round(monthly_kwh, 2),
        "total_cost": round(total_cost, 2)
    }
