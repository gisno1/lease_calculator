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


st.title("Lease Calculator")

# Inputs
startdatum = st.date_input("Startdatum lease", date.today())

lening = st.text_input("Lening bedrag (€)", "20000").replace(",", ".")
restschuld = st.text_input("Restschuld (€)", "7500").replace(",", ".")
jaar_rente = st.text_input("Jaarlijkse rente (%)", "9,0").replace(",", ".")
looptijd = st.text_input("Looptijd (maanden)", "36")

if st.button("Bereken"):
    try:
        lening = float(lening)
        restschuld = float(restschuld)
        jaar_rente = float(jaar_rente)
        looptijd = int(looptijd)

        maandlast, totale_rente = bereken_totale_rente(
            lening, jaar_rente, looptijd, restschuld
        )

        # -----------------------------
        # PERIODEN OPBOUWEN
        # -----------------------------
        periods = []
        huidige = startdatum

        einddatum = startdatum + relativedelta(months=looptijd)

        for i in range(looptijd):
            maand_start = huidige.replace(day=1)
            maand_einde = (maand_start + relativedelta(months=1)) - timedelta(days=1)

            periode_start = max(huidige, maand_start)
            periode_einde = min(maand_einde, einddatum - timedelta(days=1))

            periods.append({
                "periode": i + 1,
                "start": periode_start,
                "einde": periode_einde
            })

            huidige = maand_start + relativedelta(months=1)

        # -----------------------------
        # PARTIAL ALLOCATIE FIX
        # -----------------------------
        eerste = periods[0]
        laatste = periods[-1]

        dagen_eerste = (eerste["einde"] - eerste["start"]).days + 1
        dagen_laatste = (laatste["einde"] - laatste["start"]).days + 1

        totaal_partial = dagen_eerste + dagen_laatste if looptijd > 1 else 1

        # -----------------------------
        # BEREKENING
        # -----------------------------
        data = []
        huidige_restschuld = lening

        # for p in periods:

        #     if p["periode"] == 1:
        #         factor = dagen_eerste / totaal_partial if looptijd > 1 else 1
        #     elif p["periode"] == looptijd:
        #         factor = dagen_laatste / totaal_partial if looptijd > 1 else 1
        #     else:
        #         factor = 1

        #     termijn = maandlast * factor

        #     rente = (huidige_restschuld * (jaar_rente / 100) / 12) * factor
        #     aflossing = termijn - rente

        #     huidige_restschuld -= aflossing
        #     if huidige_restschuld < 0:
        #         huidige_restschuld = 0

        #     data.append([
        #         p["periode"],
        #         p["start"],
        #         p["einde"],
        #         f"{termijn:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."),
        #         f"{aflossing:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."),
        #         f"{rente:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."),
        #         f"{huidige_restschuld:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        #     ])

        for p in periods:

            if p["periode"] == 1:
                factor = dagen_eerste / totaal_partial if looptijd > 1 else 1
            elif p["periode"] == looptijd:
                factor = dagen_laatste / totaal_partial if looptijd > 1 else 1
            else:
                factor = 1

            termijn = maandlast * factor

            # -----------------------------
            # 1. eerst aflossing schatten
            # -----------------------------
            rente_begin = (huidige_restschuld * (jaar_rente / 100) / 12) * factor
            aflossing = termijn - rente_begin

            # update restschuld eerst
            nieuwe_restschuld = huidige_restschuld - aflossing
            if nieuwe_restschuld < 0:
                nieuwe_restschuld = 0

            # -----------------------------
            # 2. rente over NIEUWE restschuld (jouw eis)
            # -----------------------------
            rente = (nieuwe_restschuld * (jaar_rente / 100) / 12) * factor

            huidige_restschuld = nieuwe_restschuld

            data.append([
                p["periode"],
                p["start"],
                p["einde"],
                f"{termijn:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."),
                f"{aflossing:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."),
                f"{rente:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."),
                f"{huidige_restschuld:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
            ])

        df = pd.DataFrame(
            data,
            columns=[
                "Periode",
                "Start",
                "Einde",
                "Termijn (€)",
                "Aflossing (€)",
                "Rente (€)",
                "Restschuld (€)"
            ]
        )

        formatted_maandlast = f"{maandlast:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        formatted_totale_rente = f"{totale_rente:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

        st.success(f"Volledige maandtermijn: €{formatted_maandlast}")
        st.info(f"Totale rentekosten: €{formatted_totale_rente}")
        st.write("Aflossingsoverzicht:")
        st.dataframe(df, hide_index=True)

    except ValueError:
        st.error("Voer alstublieft geldige numerieke waarden in.")