def calculate_monthly_payment(principal: float, annual_rate: float, years: int) -> float:
    """Calculate monthly loan payment using PMT formula."""
    monthly_rate = annual_rate / 12
    num_payments = years * 12
    if monthly_rate == 0:
        return principal / num_payments
    return principal * (monthly_rate * (1 + monthly_rate) ** num_payments) / ((1 + monthly_rate) ** num_payments - 1)


def calculate_loan(
    property_price: float,
    down_payment: float,
    loan_term_years: int,
    annual_interest_rate: float,
    num_bedrooms: int,
    num_co_owners: int,
    rent_per_room: float,
    total_common_costs: float,
    annual_appreciation_rate: float,
) -> dict:
    """Calculate loan details for your share of a property."""

    your_property_share = property_price / num_co_owners
    your_loan_share = your_property_share - down_payment
    
    monthly_payment = calculate_monthly_payment(your_loan_share, annual_interest_rate, loan_term_years)
    
    your_common_costs = total_common_costs / num_co_owners
    
    rooms_for_rent = num_bedrooms - num_co_owners
    total_rental_income = rooms_for_rent * rent_per_room
    your_rental_income = total_rental_income / num_co_owners
    
    net_monthly_cost = monthly_payment + your_common_costs - your_rental_income
    
    your_monthly_appreciation = (property_price * annual_appreciation_rate / 12) / num_co_owners
    
    net_after_appreciation = net_monthly_cost - your_monthly_appreciation
    
    return {
        "your_loan_share": your_loan_share,
        "monthly_payment": monthly_payment,
        "your_common_costs": your_common_costs,
        "total_rental_income": total_rental_income,
        "your_rental_income": your_rental_income,
        "net_monthly_cost": net_monthly_cost,
        "your_monthly_appreciation": your_monthly_appreciation,
        "net_after_appreciation": net_after_appreciation,
    }


if __name__ == "__main__":
    # Example values
    result = calculate_loan(
        property_price=5_000_000,
        down_payment=500_000,  # Your down payment (egenkapital)
        loan_term_years=30,
        annual_interest_rate=0.05,
        num_bedrooms=4,
        num_co_owners=2,
        rent_per_room=6_000,
        total_common_costs=4_000,
        annual_appreciation_rate=0.03,
    )
    
    print("=== Din låneoversikt ===\n")
    print(f"Din andel av lånebeløp:          {result['your_loan_share']:,.0f} kr")
    print(f"Månedlig lånebetaling:           {result['monthly_payment']:,.0f} kr")
    print(f"Din del av felleskostnad:        {result['your_common_costs']:,.0f} kr")
    print(f"Utleieinntekt (totalt):          {result['total_rental_income']:,.0f} kr")
    print(f"Din andel av utleieinntekt:      {result['your_rental_income']:,.0f} kr")
    print(f"Netto månedlig kostnad:          {result['net_monthly_cost']:,.0f} kr")
    print(f"Din andel av verdistigning/mnd: {result['your_monthly_appreciation']:,.0f} kr")
    print(f"Netto etter verdistigning:       {result['net_after_appreciation']:,.0f} kr")
