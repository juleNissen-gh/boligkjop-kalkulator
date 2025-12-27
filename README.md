# Boligkjøp Kalkulator

Et verktøy for å analysere boliger på finn.no og beregne lånekostnader når du kjøper sammen med andre.

## Funksjoner

- **Web scraper** for finn.no som henter boligdata automatisk
- **Lånekalkulator** som beregner din andel av kostnader når du kjøper med mediere
- Tar hensyn til utleieinntekt fra ledige rom
- Beregner verdistigning og netto månedlig kostnad

## Installasjon

```bash
pip install selenium webdriver-manager
```

## Bruk

### 1. Lånekalkulator (alene)

Hvis du bare vil regne på én bolig:

```python
from loan_calculator import calculate_loan

result = calculate_loan(
    property_price=5_000_000,      # Totalpris (inkl. fellesgjeld)
    down_payment=500_000,           # DIN egenkapital (ikke total!)
    loan_term_years=30,             # Nedbetalingstid
    annual_interest_rate=0.05,      # Årlig rente (5% = 0.05)
    num_bedrooms=4,                 # Antall soverom
    num_co_owners=2,                # Antall medeiere
    rent_per_room=6_000,            # Leie per rom per måned
    total_common_costs=4_000,       # Total felleskostnad per måned
    annual_appreciation_rate=0.03,  # Forventet verdistigning (3% = 0.03)
)
```

### 2. Finn.no Scraper (automatisk søk)

#### Steg 1: Opprett din personlige config-fil

Lag en fil `my_config.py` i samme mappe (denne filen blir **ikke** committet til GitHub):

```python
"""Personal configuration"""

# Your finn.no search URL
# Go to finn.no, set filters (location, price, bedrooms, etc.), copy the URL
# Tip: Add &sort=PRICE_ASC to sort by price (low to high)
SEARCH_URL = "https://www.finn.no/realestate/homes/search.html?location=0.20001&sort=PRICE_ASC&min_bedrooms=2"

# Your personal loan parameters
LOAN_PARAMS = {
    'down_payment': 800_000,        # Your down payment (egenkapital)
    'loan_term_years': 30,          # Loan term
    'annual_interest_rate': 0.0508, # Annual interest rate
    'num_co_owners': 2,             # Number of co-owners
    'rent_per_room': 6_500,         # Expected rent per room
    'annual_appreciation_rate': 0.036, # Expected annual appreciation
}

# Maximum property price to consider
MAX_PRICE = 5_200_000
```

#### Steg 2: Kjør scraperen

```bash
python finn_scraper_selenium.py
```

Scraperen vil automatisk laste verdiene fra `my_config.py` og:
- Hente alle boliger fra ditt søk
- Beregne lånekostnader for hver bolig
- Sortere etter laveste netto månedlig kostnad
- Lagre resultatene til `finn_properties_selenium.json`

**Merk:** Hvis `my_config.py` ikke eksisterer, vil scraperen bruke eksempel-verdier fra koden.

## Hvordan det fungerer

1. Scraperen finner boliger på finn.no basert på søkekriterier
2. For hver bolig hentes: totalpris, antall soverom, og felleskostnad
3. Lånekalkulatoren beregner:
   - Din andel av lånet (boligpris ÷ antall medeiere - din egenkapital)
   - Månedlig lånebetaling
   - Din andel av felleskostnad
   - Utleieinntekt fra ledige rom
   - Netto månedlig kostnad
   - Verdistigning per måned

## Viktige detaljer

### Egenkapital
⚠️ **VIKTIG:** `down_payment` er **DIN** egenkapital, ikke total egenkapital for alle medeiere!

**Eksempel:**
- Bolig koster 5 000 000 kr
- Dere er 2 medeiere
- Din andel = 2 500 000 kr
- Din egenkapital = 500 000 kr
- Ditt lån = 2 500 000 - 500 000 = 2 000 000 kr

### Fordeling av kostnader
- **Felleskostnader:** Deles likt mellom alle medeiere
- **Utleieinntekt:** Deles likt mellom alle medeiere
- **Verdistigning:** Beregnes på hele boligen, deretter din andel

### Finn.no scraping
- Scraperen kan bli blokkert hvis du gjør for mange requests for raskt
- Delay mellom requests er satt til 1 sekund (kan justeres i koden)
- Screenshots lagres hvis data mangler (for debugging)
