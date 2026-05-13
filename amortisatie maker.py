import streamlit as st
import pandas as pd
from datetime import date, timedelta
from dateutil.relativedelta import relativedelta

def bereken_totale_rente(lening, jaar_rente, looptijd, restschuld):

    r = (jaar_rente / 100) / 12  
    n = looptijd  

    A = (lening - restschuld / ((1 + r) ** n)) / ((1 - (1 + r) ** -n) / r)

    totale_betalingen = A * n + restschuld
    totale_rente = totale_betalingen - lening

    return A, totale_rente


st.title('Lease Calculator')

# Inputs
startdatum = st.date_input('Startdatum lease', date.today())

lening = st.text_input('Lening bedrag (€)', '20000').replace(',', '.')
restschuld = st.text_input('Restschuld (€)', '7500').replace(',', '.')
jaar_rente = st.text_input('Jaarlijkse rente (%)', '9,0').replace(',', '.')
looptijd = st.text_input('Looptijd (maanden)', '36')

if st.button('Bereken'):
    try:
        lening = float(lening)
        restschuld = float(restschuld)
        jaar_rente = float(jaar_rente)
        looptijd = int(looptijd)

        maandlast, totale_rente = bereken_totale_rente(
            lening, jaar_rente, looptijd, restschuld
        )

        data = []
        huidige_restschuld = lening

        start = startdatum
        eind = start + relativedelta(months=looptijd)

        # itereren per kalendermaand
        huidige = start

        periode = 1

        while huidige < eind:

            maand_start = huidige.replace(day=1)
            volgende_maand = (maand_start + relativedelta(months=1))
            maand_einde = volgende_maand - timedelta(days=1)

            periode_start = max(huidige, maand_start)
            periode_einde = min(maand_einde, eind - timedelta(days=1))

            dagen_in_maand = (maand_einde - maand_start).days + 1
            dagen_in_periode = (periode_einde - periode_start).days + 1

            # pro rata factor
            factor = dagen_in_periode / dagen_in_maand

            rente = (huidige_restschuld * (jaar_rente / 100) / 12) * factor
            aflossing = (maandlast * factor) - rente

            huidige_restschuld -= aflossing
            if huidige_restschuld < 0:
                huidige_restschuld = 0

            data.append([
                periode,
                periode_start,
                periode_einde,
                f'{(maandlast * factor):,.2f}'.replace(',', 'X').replace('.', ',').replace('X', '.'),
                f'{aflossing:,.2f}'.replace(',', 'X').replace('.', ',').replace('X', '.'),
                f'{rente:,.2f}'.replace(',', 'X').replace('.', ',').replace('X', '.'),
                f'{huidige_restschuld:,.2f}'.replace(',', 'X').replace('.', ',').replace('X', '.')
            ])

            periode += 1
            huidige = volgende_maand

        df = pd.DataFrame(data, columns=[
            'Periode',
            'Start',
            'Einde',
            'Termijn (€)',
            'Aflossing (€)',
            'Rente (€)',
            'Restschuld (€)'
        ])

        formatted_maandlast = f'{maandlast:,.2f}'.replace(',', 'X').replace('.', ',').replace('X', '.')
        formatted_totale_rente = f'{totale_rente:,.2f}'.replace(',', 'X').replace('.', ',').replace('X', '.')

        st.success(f'Volledige maandtermijn: €{formatted_maandlast}')
        st.info(f'Totale rentekosten: €{formatted_totale_rente}')
        st.write('Aflossingsoverzicht:')
        st.dataframe(df, hide_index=True)

    except ValueError:
        st.error('Voer alstublieft geldige numerieke waarden in.')