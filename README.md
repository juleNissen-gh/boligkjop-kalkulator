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

### Lånekalkulator

```python
from loan_calculator import calculate_loan

result = calculate_loan(
    property_price=5_000_000,
    down_payment=400_000,  # DIN egenkapital
    loan_term_years=30,
    annual_interest_rate=0.0508,
    num_bedrooms=4,
    num_co_owners=2,
    rent_per_room=6_500,
    total_common_costs=4_000,
    annual_appreciation_rate=0.036,
)
```

### Finn.no Scraper

```python
from finn_scraper_selenium import FinnPropertyScraperSelenium

scraper = FinnPropertyScraperSelenium(headless=True)

properties = scraper.scrape_all(
    search_url="https://www.finn.no/realestate/homes/search.html?...",
    max_price=5_000_000,
    loan_params={
        'down_payment': 800_000,
        'loan_term_years': 30,
        'annual_interest_rate': 0.0508,
        'num_co_owners': 2,
        'rent_per_room': 6_500,
        'annual_appreciation_rate': 0.036,
    }
)
```

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

- `down_payment` er **din** egenkapital, ikke total
- Utleieinntekt fordeles likt mellom medeiere
- Felleskostnader fordeles likt mellom medeiere
