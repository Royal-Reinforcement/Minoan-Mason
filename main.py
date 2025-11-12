import streamlit as st
import pandas as pd
import smartsheet

APP_NAME = 'Minoan Mason'


@st.cache_data(ttl=300)
def smartsheet_to_dataframe(sheet_id):
    smartsheet_client = smartsheet.Smartsheet(st.secrets['smartsheet']['access_token'])
    sheet             = smartsheet_client.Sheets.get_sheet(sheet_id)
    columns           = [col.title for col in sheet.columns]
    rows              = []
    for row in sheet.rows: rows.append([cell.value for cell in row.cells])
    return pd.DataFrame(rows, columns=columns)


st.set_page_config(page_title=APP_NAME, page_icon='💬', layout='centered')

st.image(st.secrets['images']["rr_logo"], width=100)

st.title(APP_NAME)

key  = st.query_params.get('auth')

if key is None or key != st.secrets['auth']['key']:
    st.warning('It appears you are using an invalid link. Please contact the MOD for access.')

else:
    st.info('Generate a Minoan quote based on the Royal Destinations template.')

    df = smartsheet_to_dataframe(st.secrets['smartsheet']['sheets']['template'])
    df = df.drop(columns=['Quantity']) 
    df['ID'] = df.index + 1

    with st.form("item_form"):
        inputs = {}

        for _, row in df.iterrows():
            item_id         = row['ID']
            item_name       = row['Product Name'].replace(' ¬Æ ', ' ').replace(' ‚Ñ¢ ', ' ')
            item_variant    = row['Variant']
            title           = f'**{item_name}** | {item_variant}'
            key             = f'{item_name} - {item_variant}'
            
            inputs[item_id] = st.number_input(
                label=title,
                min_value=0,
                value=0,
                step=1,
                key=key
            )

        submitted = st.form_submit_button("Generate Quote File", use_container_width=True)

    if submitted:
        result = pd.DataFrame(list(inputs.items()), columns=["ID", "Quantity"])
        result = result[result['Quantity'] > 0]
        result = result.merge(df, on='ID', how='left')
        result = result[['Product Name', 'Variant', 'Quantity','Product URL']]

        st.download_button(
            label="Download Quote as CSV",
            data=result.to_csv(index=False).encode('utf-8'),
            file_name='minoan_quote.csv',
            mime='text/csv',
            type='primary',
            use_container_width=True
        )
