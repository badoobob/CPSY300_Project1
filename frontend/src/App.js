import React, { useState } from "react";
import "./App.css";

const API_URL =
  "https://diet-analysis-func-bhc3h4h2ane3axam.canadacentral-01.azurewebsites.net/api/analyze";

function App() {
  const [data, setData] = useState(null);
  const [diet, setDiet] = useState("");

  const fetchData = async () => {
    try {
      let url = API_URL;

      if (diet) {
        url += `?diet_type=${diet}`;
      }

      const res = await fetch(url);
      const json = await res.json();

      console.log("API RESPONSE:", json);

      setData(json);
    } catch (err) {
      console.error("Error:", err);
    }
  };

  return (
    <div className="container">
      <h1 className="title">Nutritional Insights</h1>

      {/* FILTERS */}
      <div className="filters">
        <input
          placeholder="Search by Diet Type"
          onChange={(e) => setDiet(e.target.value)}
        />
        <select>
          <option>All Diet Types</option>
        </select>
      </div>

      {/* BUTTONS */}
      <div className="buttons">
        <button onClick={fetchData} className="btn btn-primary">
          Get Nutritional Insights
        </button>

        <button className="btn btn-green">Get Recipes</button>
        <button className="btn btn-purple">Get Clusters</button>
      </div>

      {/* METADATA */}
      {data && (
        <div className="meta">
          <p><b>Execution Time:</b> {data.execution_time_seconds}s</p>
          <p><b>Records:</b> {data.record_count}</p>
          <p><b>Filter:</b> {data.diet_filter_applied}</p>
        </div>
      )}

      {/* CHARTS */}
      {data && (
        <div className="grid">
          <div className="card">
            <h3>Bar Chart</h3>
            <img
              src={`data:image/png;base64,${data.charts.avg_macronutrients_bar}`}
              alt="bar"
            />
          </div>

          <div className="card">
            <h3>Scatter Plot</h3>
            <img
              src={`data:image/png;base64,${data.charts.carbs_vs_protein_scatter}`}
              alt="scatter"
            />
          </div>

          <div className="card">
            <h3>Heatmap</h3>
            <img
              src={`data:image/png;base64,${data.charts.nutrient_correlation_heatmap}`}
              alt="heatmap"
            />
          </div>

          <div className="card">
            <h3>Pie Chart</h3>
            <img
              src={`data:image/png;base64,${data.charts.recipe_distribution_pie}`}
              alt="pie"
            />
          </div>
        </div>
      )}

      {/* PAGINATION */}
      <div className="pagination">
        <button>Previous</button>
        <button className="active">1</button>
        <button>2</button>
        <button>Next</button>
      </div>

      <footer>© 2025 Nutritional Insights</footer>
    </div>
  );
}

export default App;