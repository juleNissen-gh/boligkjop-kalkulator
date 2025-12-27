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

#### Steg 1: Få din finn.no søke-URL

1. Gå til [finn.no/realestate/homes](https://www.finn.no/realestate/homes/search.html)
2. Sett filtre (sted, pris, soverom, osv.)
3. Kopier hele URL-en fra adressefeltet
4. **Tips:** Legg til `&sort=PRICE_ASC` på slutten for å sortere etter pris (lavest først)

**Eksempel URL:**
```
https://www.finn.no/realestate/homes/search.html?location=0.20001&sort=PRICE_ASC&min_bedrooms=2
```

#### Steg 2: Oppdater parametere i `finn_scraper_selenium.py`

Åpne `finn_scraper_selenium.py` og finn `main()` funksjonen (linje ~303). Oppdater:

```python
# Lim inn din finn.no URL her:
search_url = "<Lim inn URL fra steg 1>"

# Juster disse verdiene til din situasjon:
loan_params = {
    'down_payment': 500_000,        # DIN egenkapital
    'loan_term_years': 30,          # Nedbetalingstid
    'annual_interest_rate': 0.05,   # Årlig rente (sjekk bank.no)
    'num_co_owners': 2,             # Antall medeiere
    'rent_per_room': 6_000,         # Forventet leie per rom
    'annual_appreciation_rate': 0.03, # Forventet verdistigning per år
}
```

#### Steg 3: Kjør scraperen

```bash
python finn_scraper_selenium.py
```

Scraperen vil:
- Hente alle boliger fra ditt søk
- Beregne lånekostnader for hver bolig
- Sortere etter laveste netto månedlig kostnad
- Lagre resultatene til `finn_properties_selenium.json`

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
