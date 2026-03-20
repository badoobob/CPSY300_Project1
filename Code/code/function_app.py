import azure.functions as func
import logging
import json
import os
import time
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import numpy as np
from azure.storage.blob import BlobServiceClient
from io import StringIO, BytesIO
import base64

app = func.FunctionApp(http_auth_level=func.AuthLevel.ANONYMOUS)
 
def get_data_from_blob():
    """Read the Diets Dataset CSV from Azure Blob Storage."""
    connect_str = os.environ["AzureWebJobsStorage"]
    container_name = os.environ.get("BLOB_CONTAINER_NAME", "diet-data")
    blob_name = os.environ.get("BLOB_FILE_NAME", "diets_dataset.csv")
 
    blob_service_client = BlobServiceClient.from_connection_string(connect_str)
    blob_client = blob_service_client.get_blob_client(container=container_name, blob=blob_name)
    blob_data = blob_client.download_blob().readall()
    df = pd.read_csv(StringIO(blob_data.decode("utf-8")))
    return df
 
def fig_to_base64(fig):
    """Convert a matplotlib figure to a base64 string."""
    buf = BytesIO()
    fig.savefig(buf, format="png", bbox_inches="tight")
    buf.seek(0)
    encoded = base64.b64encode(buf.read()).decode("utf-8")
    plt.close(fig)
    return encoded
 
def chart_avg_macronutrients(df):
    """Bar chart: Average Protein, Carbs, Fat by Diet Type."""
    avg = df.groupby("Diet_type")[["Protein(g)", "Carbs(g)", "Fat(g)"]].mean()
    fig, ax = plt.subplots(figsize=(10, 6))
    avg.plot(kind="bar", ax=ax, color=["#4e79a7", "#f28e2b", "#e15759"])
    ax.set_title("Average Macronutrients by Diet Type", fontsize=14, fontweight="bold")
    ax.set_xlabel("Diet Type")
    ax.set_ylabel("Average (g)")
    ax.set_xticklabels(avg.index, rotation=45, ha="right")
    ax.legend(["Protein(g)", "Carbs(g)", "Fat(g)"])
    ax.grid(axis="y", linestyle="--", alpha=0.5)
    fig.tight_layout()
    return fig_to_base64(fig)
 
def chart_scatter_carbs_protein(df):
    """Scatter plot: Carbs vs Protein colored by Diet Type."""
    diet_types = df["Diet_type"].unique()
    colors = list(mcolors.TABLEAU_COLORS.values())
    fig, ax = plt.subplots(figsize=(10, 6))
    for i, diet in enumerate(diet_types):
        subset = df[df["Diet_type"] == diet]
        ax.scatter(
            subset["Protein(g)"], subset["Carbs(g)"],
            label=diet, alpha=0.6, s=40,
            color=colors[i % len(colors)]
        )
    ax.set_title("Carbs vs Protein by Diet Type", fontsize=14, fontweight="bold")
    ax.set_xlabel("Protein (g)")
    ax.set_ylabel("Carbs (g)")
    ax.legend(title="Diet Type", bbox_to_anchor=(1.05, 1), loc="upper left")
    ax.grid(linestyle="--", alpha=0.5)
    fig.tight_layout()
    return fig_to_base64(fig)
 
def chart_nutrient_heatmap(df):
    """Heatmap: Correlation between Protein, Carbs, Fat."""
    corr = df[["Protein(g)", "Carbs(g)", "Fat(g)"]].corr()
    fig, ax = plt.subplots(figsize=(6, 5))
    cax = ax.matshow(corr, cmap="coolwarm", vmin=-1, vmax=1)
    fig.colorbar(cax)
    labels = ["Protein(g)", "Carbs(g)", "Fat(g)"]
    ax.set_xticks(range(len(labels)))
    ax.set_yticks(range(len(labels)))
    ax.set_xticklabels(labels, rotation=45, ha="left")
    ax.set_yticklabels(labels)
    for i in range(len(labels)):
        for j in range(len(labels)):
            ax.text(j, i, f"{corr.iloc[i, j]:.2f}", ha="center", va="center", color="black", fontsize=11)
    ax.set_title("Nutrient Correlation Heatmap", fontsize=14, fontweight="bold", pad=20)
    fig.tight_layout()
    return fig_to_base64(fig)
 
def chart_recipe_pie(df):
    """Pie chart: Recipe count distribution by Diet Type."""
    counts = df["Diet_type"].value_counts()
    fig, ax = plt.subplots(figsize=(8, 8))
    ax.pie(
        counts.values,
        labels=counts.index,
        autopct="%1.1f%%",
        startangle=140,
        colors=list(mcolors.TABLEAU_COLORS.values())[:len(counts)]
    )
    ax.set_title("Recipe Distribution by Diet Type", fontsize=14, fontweight="bold")
    fig.tight_layout()
    return fig_to_base64(fig)
 
 
@app.route(route="analyze", methods=["GET"])
def analyze(req: func.HttpRequest) -> func.HttpResponse:
    logging.info("Diet analysis function triggered.")
    start_time = time.time()
 
    try:
        # Optional filter by diet type
        diet_filter = req.params.get("diet_type", None)
 
        df = get_data_from_blob()
 
        # Apply filter if provided
        if diet_filter:
            df = df[df["Diet_type"].str.lower() == diet_filter.lower()]
            if df.empty:
                return func.HttpResponse(
                    json.dumps({"error": f"No data found for diet type: {diet_filter}"}),
                    status_code=404,
                    mimetype="application/json"
                )
 
        # Generate all charts
        bar_chart = chart_avg_macronutrients(df)
        scatter_chart = chart_scatter_carbs_protein(df)
        heatmap_chart = chart_nutrient_heatmap(df)
        pie_chart = chart_recipe_pie(df)
 
        execution_time = round(time.time() - start_time, 3)
 
        response = {
            "status": "success",
            "execution_time_seconds": execution_time,
            "diet_filter_applied": diet_filter if diet_filter else "none",
            "record_count": len(df),
            "charts": {
                "avg_macronutrients_bar": bar_chart,
                "carbs_vs_protein_scatter": scatter_chart,
                "nutrient_correlation_heatmap": heatmap_chart,
                "recipe_distribution_pie": pie_chart
            }
        }
 
        return func.HttpResponse(
            json.dumps(response),
            status_code=200,
            mimetype="application/json",
            headers={"Access-Control-Allow-Origin": "*"}
        )
 
    except Exception as e:
        logging.error(f"Error: {str(e)}")
        return func.HttpResponse(
            json.dumps({"status": "error", "message": str(e)}),
            status_code=500,
            mimetype="application/json",
            headers={"Access-Control-Allow-Origin": "*"}
        )