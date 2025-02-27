import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import io
import zipfile
import tempfile
import os

st.set_page_config(layout="wide", page_title="Analyse DVF")

st.title("Analyse des données DVF (Demandes de Valeur Foncière)")

# Sidebar configuration
st.sidebar.header("Configuration")
MAX_PRICE = st.sidebar.number_input("Prix maximum au m² (€/m²)", value=10000, min_value=1000, max_value=50000, step=1000)

# File upload section
st.header("1. Chargement des données")
st.write("Téléchargez les fichiers CSV du DVF ou une archive ZIP contenant ces fichiers.")

upload_option = st.radio("Méthode de téléchargement", ["Fichiers CSV", "Archive ZIP"])

if upload_option == "Fichiers CSV":
    uploaded_files = st.file_uploader("Téléchargez les fichiers CSV", type="csv", accept_multiple_files=True)
    zip_file = None
else:
    uploaded_files = None
    zip_file = st.file_uploader("Téléchargez une archive ZIP", type="zip")

# Function to process the dataframe
@st.cache_data
def process_dataframe(df):
    try:
        # Convert date_mutation to datetime
        if 'date_mutation' in df.columns:
            df['date_mutation'] = pd.to_datetime(df['date_mutation'], errors='coerce')
            # Drop rows with invalid dates
            df = df.dropna(subset=['date_mutation'])
        else:
            st.error("Colonne 'date_mutation' manquante dans les données.")
            return None
        
        # Check for required columns
        required_columns = ['type_local', 'valeur_fonciere', 'surface_reelle_bati']
        missing_columns = [col for col in required_columns if col not in df.columns]
        
        if missing_columns:
            st.error(f"Colonnes manquantes dans les données: {', '.join(missing_columns)}")
            return None
        
        # Drop unused columns if they exist
        columns_to_drop = [
            'numero_disposition', 'code_departement', 'ancien_code_commune',
            'ancien_nom_commune', 'ancien_id_parcelle', 'numero_volume', 
            'lot1_numero', 'lot1_surface_carrez', 'lot2_numero',
            'lot2_surface_carrez', 'lot3_numero', 'lot3_surface_carrez',
            'lot4_numero', 'lot4_surface_carrez', 'lot5_numero',
            'lot5_surface_carrez', 'code_type_local',
            'code_nature_culture', 'nature_culture', 'code_nature_culture_speciale',
            'nature_culture_speciale', 'section_prefixe'
        ]
        
        columns_to_drop = [col for col in columns_to_drop if col in df.columns]
        if columns_to_drop:
            df.drop(columns_to_drop, axis=1, inplace=True)
        
        # Filter for only houses and apartments
        if 'type_local' in df.columns:
            df = df[(df['type_local'] == 'Appartement') | (df['type_local'] == 'Maison')]
        
        # Drop rows with missing or zero values for required calculations
        df = df.dropna(subset=['valeur_fonciere', 'surface_reelle_bati'])
        df = df[(df['valeur_fonciere'] > 0) & (df['surface_reelle_bati'] > 0)]
        
        # Calculate price per square meter
        df["price(€/m2)"] = df.valeur_fonciere / df.surface_reelle_bati
        
        # Filter out prices above MAX_PRICE
        df = df[(df["price(€/m2)"] <= MAX_PRICE)]
        
        # Add year column
        df['year_mutation'] = df['date_mutation'].dt.year
        
        return df
    
    except Exception as e:
        st.error(f"Erreur lors du traitement des données: {str(e)}")
        return None

# Function to read CSV files
def read_csv_file(file):
    try:
        return pd.read_csv(file, sep=";")
    except Exception as e:
        st.error(f"Erreur lors de la lecture du fichier {file.name}: {str(e)}")
        return None

# Main dataframe
combined_df = None

# Process uploaded files
if uploaded_files:
    with st.spinner("Traitement des fichiers CSV..."):
        dataframes = []
        for uploaded_file in uploaded_files:
            df = read_csv_file(uploaded_file)
            if df is not None:
                dataframes.append(df)
        
        if dataframes:
            combined_df = pd.concat(dataframes, ignore_index=True)
            combined_df = process_dataframe(combined_df)
        else:
            st.error("Aucun fichier CSV valide n'a pu être traité.")
            
elif zip_file:
    with st.spinner("Extraction et traitement de l'archive ZIP..."):
        dataframes = []
        with tempfile.TemporaryDirectory() as tmpdirname:
            try:
                with zipfile.ZipFile(zip_file, 'r') as zip_ref:
                    zip_ref.extractall(tmpdirname)
                
                csv_files = [f for f in os.listdir(tmpdirname) if f.endswith(".csv")]
                
                if not csv_files:
                    st.error("Aucun fichier CSV trouvé dans l'archive ZIP.")
                else:
                    for filename in csv_files:
                        file_path = os.path.join(tmpdirname, filename)
                        try:
                            df = pd.read_csv(file_path, sep=";")
                            dataframes.append(df)
                        except Exception as e:
                            st.error(f"Erreur lors de la lecture du fichier {filename}: {str(e)}")
                
                if dataframes:
                    combined_df = pd.concat(dataframes, ignore_index=True)
                    combined_df = process_dataframe(combined_df)
            
            except Exception as e:
                st.error(f"Erreur lors de l'extraction de l'archive ZIP: {str(e)}")

# Display analysis if data is loaded
if combined_df is not None and not combined_df.empty:
    st.success(f"Données chargées avec succès! {len(combined_df)} transactions trouvées.")
    
    st.header("2. Résumé des données")
    
    # Show basic statistics
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Nombre total de transactions", len(combined_df))
    
    with col2:
        avg_price = round(combined_df["price(€/m2)"].mean(), 2)
        st.metric("Prix moyen au m²", f"{avg_price} €/m²")
    
    with col3:
        years_range = f"{combined_df['year_mutation'].min()} - {combined_df['year_mutation'].max()}"
        st.metric("Période couverte", years_range)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Répartition par type de bien")
        type_counts = combined_df['type_local'].value_counts().reset_index()
        type_counts.columns = ['Type de bien', 'Nombre']
        
        fig = px.pie(
            type_counts, 
            values='Nombre', 
            names='Type de bien',
            title="Répartition par type de bien"
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("Répartition par année")
        year_counts = combined_df['year_mutation'].value_counts().sort_index().reset_index()
        year_counts.columns = ['Année', 'Nombre']
        
        fig = px.bar(
            year_counts,
            x='Année',
            y='Nombre',
            title="Nombre de transactions par année"
        )
        st.plotly_chart(fig, use_container_width=True)
    
    # Filtering options
    st.header("3. Filtres")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        selected_types = st.multiselect(
            "Type de bien",
            options=combined_df['type_local'].unique(),
            default=combined_df['type_local'].unique()
        )
    
    with col2:
        # Get all available number of rooms
        available_rooms = sorted(combined_df['nombre_pieces_principales'].dropna().unique())
        selected_rooms = st.multiselect(
            "Nombre de pièces",
            options=available_rooms,
            default=available_rooms
        )
    
    with col3:
        # Year range slider
        years = sorted(combined_df['year_mutation'].unique())
        year_range = st.slider(
            "Période",
            min_value=int(min(years)),
            max_value=int(max(years)),
            value=(int(min(years)), int(max(years)))
        )
    
    # Filter data based on selections
    filtered_df = combined_df[
        (combined_df['type_local'].isin(selected_types)) & 
        (combined_df['nombre_pieces_principales'].isin(selected_rooms)) &
        (combined_df['year_mutation'] >= year_range[0]) &
        (combined_df['year_mutation'] <= year_range[1])
    ]
    
    if not filtered_df.empty:
        st.success(f"Nombre de transactions après filtrage: {len(filtered_df)}")
        
        # Visualizations
        st.header("4. Visualisations")
        
        viz_tabs = st.tabs(["Boxplots", "Carte"])
        
        with viz_tabs[0]:  # Boxplots
            st.subheader("Prix au m² par type de bien et nombre de pièces")
            
            for property_type in selected_types:
                type_df = filtered_df[filtered_df['type_local'] == property_type]
                
                if not type_df.empty:
                    type_df = type_df.sort_values(by='nombre_pieces_principales')
                    
                    fig = px.box(
                        type_df, 
                        x="nombre_pieces_principales", 
                        y="price(€/m2)", 
                        color="nombre_pieces_principales",
                        title=f"Type de bien: {property_type}"
                    )
                    
                    # Calculate counts for each number of rooms
                    counts = type_df['nombre_pieces_principales'].value_counts()
                    
                    # Add annotations for counts
                    for rooms in counts.index:
                        if rooms in selected_rooms:
                            room_data = type_df[type_df['nombre_pieces_principales'] == rooms]
                            if not room_data.empty:
                                fig.add_annotation(
                                    x=rooms,
                                    y=room_data['price(€/m2)'].mean(),
                                    text=f"Nombre: {counts[rooms]}",
                                    showarrow=True,
                                    arrowhead=1,
                                    ax=0,
                                    ay=-30,
                                    font=dict(size=12, color="black"),
                                    align="center",
                                    bgcolor="rgba(255,255,255,0.7)",
                                    bordercolor="black",
                                    borderwidth=1
                                )
                    
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info(f"Aucune donnée disponible pour le type de bien: {property_type} avec les filtres actuels.")
        
        with viz_tabs[1]:  # Map
            st.subheader("Carte des prix au m²")
            
            # Check if latitude and longitude columns exist
            if 'latitude' in filtered_df.columns and 'longitude' in filtered_df.columns:
                # Remove rows with missing lat/lon
                map_df = filtered_df.dropna(subset=['latitude', 'longitude'])
                
                if not map_df.empty:
                    # Year selection for map
                    map_years = sorted(map_df['year_mutation'].unique())
                    selected_map_year = st.selectbox(
                        "Sélectionnez l'année pour la carte", 
                        options=map_years,
                        index=len(map_years)-1  # Default to the most recent year
                    )
                    
                    # Filter by selected year
                    year_df = map_df[map_df['year_mutation'] == selected_map_year]
                    
                    if not year_df.empty:
                        fig = px.scatter_mapbox(
                            year_df,
                            lat="latitude",
                            lon="longitude",
                            color="price(€/m2)",
                            size="nombre_pieces_principales",
                            color_continuous_scale=px.colors.sequential.Jet,
                            hover_name="type_local",
                            hover_data={
                                "valeur_fonciere": ":,.2f €",
                                "surface_reelle_bati": ":,.0f m²",
                                "nombre_pieces_principales": True,
                                "price(€/m2)": ":,.0f €/m²",
                                "latitude": False,
                                "longitude": False
                            },
                            size_max=15,
                            zoom=12,
                            mapbox_style="open-street-map",
                            title=f"Prix au m² pour l'année {selected_map_year}"
                        )
                        
                        st.plotly_chart(fig, use_container_width=True)
                    else:
                        st.warning(f"Aucune donnée disponible pour l'année {selected_map_year} avec les filtres actuels.")
                else:
                    st.warning("Les données filtrées ne contiennent pas de coordonnées géographiques valides pour afficher la carte.")
            else:
                st.warning("Les colonnes de latitude et longitude sont manquantes dans les données.")
    else:
        st.warning("Aucune donnée ne correspond aux filtres sélectionnés.")
else:
    if uploaded_files or zip_file:
        st.error("Impossible de traiter les données. Veuillez vérifier les fichiers téléchargés.")
    else:
        st.info("Veuillez télécharger des fichiers CSV du DVF ou une archive ZIP contenant ces fichiers pour commencer l'analyse.")

# Add information section
st.sidebar.header("Informations")
st.sidebar.info(
    """
    Cette application permet d'analyser les données DVF (Demandes de Valeur Foncière).
    
    Pour commencer:
    1. Téléchargez un ou plusieurs fichiers CSV ou une archive ZIP contenant les fichiers
    2. Utilisez les filtres pour sélectionner les propriétés qui vous intéressent
    3. Explorez les visualisations (boxplots et carte)
    
    Les données DVF sont disponibles sur [le site officiel](https://www.data.gouv.fr/fr/datasets/demandes-de-valeurs-foncieres/)
    """
)

# Add footer
st.markdown("---")
st.caption("Application développée pour l'analyse des données DVF")
