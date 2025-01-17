import pandas as pd
import streamlit as st
import seaborn as sns
import plotly.express as px
from PIL import Image
from io import BytesIO

custom_params = {"axes.spines.right": False, "axes.spines.top": False}
sns.set_theme(style="ticks", rc=custom_params)

# LEITURA DE DADOS
@st.cache_data(show_spinner=True)
def load_data(file_data):
    try:
        return pd.read_csv(file_data, sep=';')
    except:
        return pd.read_excel(file_data)

@st.cache_data
def multiselect_filter(relatorio, col, selecionados):
    if 'all' in selecionados:
        return relatorio
    else:
        return relatorio[relatorio[col].isin(selecionados)].reset_index(drop=True)

############################################################################################################# TAREFA 2 
@st.cache_data 
def convert_df(df: pd.DataFrame):
    return df.to_csv(index=False).encode('utf-8')

def to_txt(df: pd.DataFrame):
    return df.to_string(index=False).encode('utf-8')

# Função para converter o df para excel
@st.cache_data
def to_excel(df: pd.DataFrame):
    output = BytesIO()
    writer = pd.ExcelWriter(output, engine='xlsxwriter')
    df.to_excel(writer, index=False, sheet_name='Sheet1')
    writer.close()  # Use close instead of save
    processed_data = output.getvalue()
    return processed_data

# Função principal da aplicação
def main():
    # Configuração inicial da página da aplicação
    st.set_page_config(page_title='Telemarketing Analysis', 
                       page_icon='../img/telmarketing_icon.png',
                       layout="wide",
                       initial_sidebar_state='expanded')

    # Título principal da aplicação
    st.write('# Telemarketing Analysis')
    st.markdown("---")
    
    # Apresenta a imagem na barra lateral da aplicação
    image = Image.open("../img/bank.png")
    st.sidebar.image(image, width=150)

    # Botão para carregar arquivo na aplicação
    st.sidebar.write("## Suba o arquivo")
    data_file_1 = st.sidebar.file_uploader("Bank marketing data", type=['csv', 'xlsx', 'txt'])

    # Verifica se há conteúdo carregado na aplicação
    if data_file_1 is not None:
        bank_raw = load_data(data_file_1)
        bank = bank_raw.copy()

        st.write('## Antes dos filtros')
        st.write(bank_raw.head())

        with st.sidebar.form(key='my_form'):

            # SELECIONA O TIPO DE GRÁFICO
            graph_type = st.radio('Tipo de gráfico:', ('Barras', 'Pizza'))
        
            # IDADES
            max_age = int(bank.age.max())
            min_age = int(bank.age.min())
            idades = st.slider(label='Idade', 
                               min_value=min_age,
                               max_value=max_age, 
                               value=(min_age, max_age),
                               step=1)

            # PROFISSÕES
            jobs_list = bank.job.unique().tolist()
            jobs_list.append('all')
            jobs_selected = st.multiselect("Profissão", jobs_list, ['all'])

            # ESTADO CIVIL
            marital_list = bank.marital.unique().tolist()
            marital_list.append('all')
            marital_selected = st.multiselect("Estado civil", marital_list, ['all'])

            # DEFAULT?
            default_list = bank.default.unique().tolist()
            default_list.append('all')
            default_selected = st.multiselect("Default", default_list, ['all'])

            # TEM FINANCIAMENTO IMOBILIÁRIO?
            housing_list = bank.housing.unique().tolist()
            housing_list.append('all')
            housing_selected = st.multiselect("Tem financiamento imob?", housing_list, ['all'])

            # TEM EMPRÉSTIMO?
            loan_list = bank.loan.unique().tolist()
            loan_list.append('all')
            loan_selected = st.multiselect("Tem empréstimo?", loan_list, ['all'])

            # MEIO DE CONTATO?
            contact_list = bank.contact.unique().tolist()
            contact_list.append('all')
            contact_selected = st.multiselect("Meio de contato", contact_list, ['all'])

            # MÊS DO CONTATO
            month_list = bank.month.unique().tolist()
            month_list.append('all')
            month_selected = st.multiselect("Mês do contato", month_list, ['all'])

            # DIA DA SEMANA
            day_of_week_list = bank.day_of_week.unique().tolist()
            day_of_week_list.append('all')
            day_of_week_selected = st.multiselect("Dia da semana", day_of_week_list, ['all'])

            # encadeamento de métodos para filtrar a seleção
            bank = (bank.query("age >= @idades[0] and age <= @idades[1]")
                        .pipe(multiselect_filter, 'job', jobs_selected)
                        .pipe(multiselect_filter, 'marital', marital_selected)
                        .pipe(multiselect_filter, 'default', default_selected)
                        .pipe(multiselect_filter, 'housing', housing_selected)
                        .pipe(multiselect_filter, 'loan', loan_selected)
                        .pipe(multiselect_filter, 'contact', contact_selected)
                        .pipe(multiselect_filter, 'month', month_selected)
                        .pipe(multiselect_filter, 'day_of_week', day_of_week_selected))

            submit_button = st.form_submit_button(label='Aplicar')
        
        # Botões de download dos dados filtrados
        st.write('## Após os filtros')
        st.write(bank.head())

        col_download1, col_download2, col_download3 = st.columns(3)
        
        df_xlsx = to_excel(bank)
        col_download1.download_button(label='📥 Download tabela filtrada em EXCEL',
                           data=df_xlsx,
                           file_name='bank_filtered.xlsx')
        
        df_csv = convert_df(bank)
        col_download2.download_button(label='📥 Download tabela CSV',
                           data=df_csv,
                           file_name='bank_filtered.csv')
        
        df_txt = to_txt(bank)
        col_download3.download_button(label='📥 Download tabela TXT',
                           data=df_txt,
                           file_name='bank_filtered.txt')
        
        st.markdown("---")

        # PLOTS    
        bank_raw_target_perc = bank_raw.y.value_counts(normalize=True).to_frame().reset_index()
        bank_raw_target_perc.columns = ['y', 'percentage']
        bank_raw_target_perc['percentage'] *= 100
        
        if 'y' in bank.columns:
            bank_target_perc = bank.y.value_counts(normalize=True).to_frame().reset_index()
            bank_target_perc.columns = ['y', 'percentage']
            bank_target_perc['percentage'] *= 100
        else:
            st.error('Erro: A coluna "y" não existe nos dados filtrados.')
            return

        col1, col2 = st.columns(2)

        df_xlsx = to_excel(bank_raw_target_perc)
        col1.write('### Proporção original')
        col1.write(bank_raw_target_perc)
        col1.download_button(label='📥 Download',
                             data=df_xlsx,
                             file_name='bank_raw_y.xlsx')
        
        df_xlsx = to_excel(bank_target_perc)
        col2.write('### Proporção da tabela com filtros')
        col2.write(bank_target_perc)
        col2.download_button(label='📥 Download',
                             data=df_xlsx,
                             file_name='bank_y.xlsx')
        st.markdown("---")

        st.write('## Proporção de aceite')
        
        if graph_type == 'Barras':
            fig1 = px.bar(bank_raw_target_perc, x='y', y='percentage', title='Dados brutos')
            fig2 = px.bar(bank_target_perc, x='y', y='percentage', title='Dados filtrados')
        else:
            fig1 = px.pie(bank_raw_target_perc, names='y', values='percentage', title='Dados brutos', hole=0.3)
            fig2 = px.pie(bank_target_perc, names='y', values='percentage', title='Dados filtrados', hole=0.3)

        col3, col4 = st.columns(2)
        col3.plotly_chart(fig1, use_container_width=True)
        col4.plotly_chart(fig2, use_container_width=True)

if __name__ == '__main__':
    main()
