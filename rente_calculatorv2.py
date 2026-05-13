import streamlit as st
import pandas as pd

def bereken_totale_rente(lening, jaar_rente, looptijd, restschuld):

    r = (jaar_rente / 100) / 12  
    n = looptijd  

    # Annuïteit berekenen
    A = (lening - restschuld / ((1 + r) ** n)) / ((1 - (1 + r) ** -n) / r)

    # Totale rentekosten
    totale_betalingen = A * n + restschuld
    totale_rente = totale_betalingen - lening

    return A, totale_rente


st.title('Lease Calculator')

# Inputvelden
lening = st.text_input('Lening bedrag (€)', '20000').replace(',', '.')
restschuld = st.text_input('Restschuld (€)', '7500').replace(',', '.')
jaar_rente = st.text_input('Jaarlijkse rente (%)', '9,0').replace(',', '.')
looptijd = st.text_input('Looptijd (maanden)', '36')

# Knop om berekening uit te voeren
if st.button('Bereken'):
    try:
        # Omzetten van tekst naar getal
        lening = float(lening)
        restschuld = float(restschuld)
        jaar_rente = float(jaar_rente)
        looptijd = int(looptijd)

        # Berekening uitvoeren
        maandlast, totale_rente = bereken_totale_rente(lening, jaar_rente, looptijd, restschuld)

        # Tabel met aflossingsoverzicht maken
        data = []
        huidige_restschuld = lening

        for maand in range(1, looptijd + 1):
            rente = (huidige_restschuld * (jaar_rente / 100)) / 12
            aflossing = maandlast - rente
            huidige_restschuld -= aflossing

            # Zorg dat restschuld niet negatief wordt
            if huidige_restschuld < 0:
                huidige_restschuld = 0

            data.append([
                        maand, 
                        f'{maandlast:,.2f}'.replace(',', 'X').replace('.', ',').replace('X', '.'),  
                        f'{aflossing:,.2f}'.replace(',', 'X').replace('.', ',').replace('X', '.'),  
                        f'{rente:,.2f}'.replace(',', 'X').replace('.', ',').replace('X', '.'),  
                        f'{huidige_restschuld:,.2f}'.replace(',', 'X').replace('.', ',').replace('X', '.')  
                        ])

        # Dataframe maken
        df = pd.DataFrame(data, columns=['Periode', 'Leasetermijn (€)', 'Aflossing (€)', 'Rente (€)', 'Restschuld (€)'])

        # Format output naar Nederlandse notatie
        formatted_maandlast = f'{maandlast:,.2f}'.replace(',', 'X').replace('.', ',').replace('X', '.')
        formatted_totale_rente = f'{totale_rente:,.2f}'.replace(',', 'X').replace('.', ',').replace('X', '.')

        # Output tonen
        st.success(f'Maandelijks bedrag (Aflossing + Rente): €{formatted_maandlast}')
        st.info(f'Totale rentekosten over de looptijd: €{formatted_totale_rente}')
        st.write('Aflossingsoverzicht:')
        st.dataframe(df, hide_index=True)

    except ValueError:
        st.error('Voer alstublieft geldige numerieke waarden in.')
