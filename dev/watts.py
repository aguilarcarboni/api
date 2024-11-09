
# Example usage
if __name__ == "__main__":
    machine_wh = int(input("Enter the machine's watt-hours: "))  # Example: 850 Wh
    result = calculate_energy_consumption(machine_wh)
    print(f"Daily consumption: {result['daily_consumption_kwh']} kWh")
    print(f"Monthly consumption: {result['monthly_consumption_kwh']} kWh")
    print(f"Total cost: ${result['total_cost']}")
