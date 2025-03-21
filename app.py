from flask import Flask, render_template, request
import pandas as pd
import plotly.express as px
import os

app = Flask(__name__)
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/upload", methods=["POST"])
def upload():
    file = request.files["file"]

    if file:
        filepath = os.path.join(UPLOAD_FOLDER, file.filename)
        file.save(filepath)

        # Lire le fichier (CSV ou Excel)
        if file.filename.endswith(".xlsx"):
            df = pd.read_excel(filepath)
        else:
            df = pd.read_csv(filepath)

        # Générer une analyse automatique
        summary = df.describe(include="all").transpose().to_html()

        # Générer des visualisations et interprétations
        graph_html, interpretations = generate_visualization(df)

        return render_template("report.html", summary=summary, graph_html=graph_html, interpretations=interpretations)

    return "Aucun fichier sélectionné"


def generate_visualization(df):
    """Génère plusieurs visualisations et des interprétations en fonction des données détectées"""
    visualizations = ""
    interpretations = ""

    if df.empty:
        return "<p>Fichier vide</p>", "<p>Aucune interprétation disponible</p>"

    numeric_cols = df.select_dtypes(include=["number"]).columns
    categorical_cols = df.select_dtypes(include=["object"]).columns

    # Histogramme pour chaque variable numérique
    for col in numeric_cols:
        fig = px.histogram(df, x=col, title=f"Distribution de {col}")
        visualizations += fig.to_html(full_html=False)
        interpretations += f"<p><strong>{col} :</strong> La distribution de cette variable montre comment les valeurs sont réparties. Un pic indique une concentration de valeurs autour d’une certaine plage.</p>"

    # Boxplot pour détecter les valeurs aberrantes
    for col in numeric_cols:
        fig = px.box(df, y=col, title=f"Répartition et valeurs aberrantes de {col}")
        visualizations += fig.to_html(full_html=False)
        interpretations += f"<p><strong>{col} :</strong> Ce boxplot permet d’identifier les valeurs extrêmes (points en dehors des moustaches). Si une boîte est très étroite, cela signifie que la plupart des valeurs sont proches de la médiane.</p>"

    # Scatterplot entre deux variables numériques
    if len(numeric_cols) >= 2:
        fig = px.scatter(df, x=numeric_cols[0], y=numeric_cols[1], title=f"Relation entre {numeric_cols[0]} et {numeric_cols[1]}")
        visualizations += fig.to_html(full_html=False)
        interpretations += f"<p><strong>{numeric_cols[0]} vs {numeric_cols[1]} :</strong> Un graphique de dispersion montre s'il existe une corrélation entre ces deux variables. Si les points forment une ligne, il y a une relation linéaire.</p>"

    # Bar chart pour les variables catégoriques
    for col in categorical_cols:
        count_df = df[col].value_counts().reset_index()
        #fig = px.bar(count_df, x="index", y=col, title=f"Répartition de {col}")
        fig = px.bar(count_df, x=count_df.index, y=col, title=f"Répartition de {col}")
        visualizations += fig.to_html(full_html=False)
        interpretations += f"<p><strong>{col} :</strong> Ce graphique en barres montre la fréquence des différentes catégories. Une valeur dominante peut indiquer une forte préférence dans les données.</p>"

    return visualizations, interpretations

if __name__ == "__main__":
    app.run(debug=True)
