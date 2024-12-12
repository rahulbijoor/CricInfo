
<a id="readme-top"></a>


<!-- PROJECT SHIELDS -->
<!--
*** I'm using markdown "reference style" links for readability.
*** Reference links are enclosed in brackets [ ] instead of parentheses ( ).
*** See the bottom of this document for the declaration of the reference variables
*** for contributors-url, forks-url, etc. This is an optional, concise syntax you may use.
*** https://www.markdownguide.org/basic-syntax/#reference-style-links
-->



<!-- PROJECT LOGO -->
<br />
<div align="center">
  

  <h1 align="center">StumpStats</h1>

  <p align="center">
    This project involves the development of an interactive Cricket Match Analytics Dashboard using Python, Dash, and Plotly. The dashboard provides a comprehensive visualization of match data, including scorecards, bowling and batting performances, and partnership contributions. It is designed to make match statistics more accessible and visually intuitive.
    <br />
  </p>
</div>



<!-- TABLE OF CONTENTS -->
<details>
  <summary>Table of Contents</summary>
  <ol>
    <li>
      <a href="#about-the-project">About The Project</a>
      <ul>
        <li><a href="#built-with">Built With</a></li>
      </ul>
    </li>
    <li>
      <a href="#getting-started">Getting Started</a>
      <ul>
        <li><a href="#prerequisites">Prerequisites</a></li>
        <li><a href="#installation">Installation</a></li>
      </ul>
    </li>
  </ol>
</details>



<!-- ABOUT THE PROJECT -->
## About The Project


This project aims to create an interactive and visually appealing Cricket Match Analytics Dashboard using Python, Dash, and Plotly. The dashboard provides users with detailed insights into cricket matches, showcasing batting and bowling scorecards, partnership contributions, and team performances in an intuitive format.

<p align="right">(<a href="#readme-top">back to top</a>)</p>



### Built With

This section should list any major frameworks/libraries used to bootstrap your project. Leave any add-ons/plugins for the acknowledgements section. Here are a few examples.

  <h3 align="center">Duckdb</h3>
  <p> DuckDB is a high-performance, in-process SQL database management system designed specifically for analytical workloads. Often referred to as the "SQLite for Analytics," it is lightweight, easy to use, and optimized for working with structured data. Unlike traditional relational databases, DuckDB excels at running complex analytical queries directly on flat files or in-memory datasets without requiring a separate database server. Its columnar storage format and vectorized execution engine allow for fast data processing, making it an ideal choice for data science, machine learning. </p>
  <p align="left"><a href="https://duckdb.org/docs/guides/overview.html"> Documentation </a></p>
  <section>
  <h3>Why DuckDB for This Project?</h3>
  <p>
    In this Cricket Analytics Dashboard, <strong>DuckDB</strong> is the database engine of choice, and for good reason:
  </p>
  <ul>
    <li><strong>Efficient Data Processing</strong>: DuckDB is optimized for analytical workloads, making it ideal for processing batting, bowling, and partnership statistics quickly and reliably.</li>
    <li><strong>Seamless Multi-Dataset Handling</strong>: With support for querying multiple datasets (e.g., <code>batsmen_details</code>, <code>bowlers_details</code>) effortlessly, DuckDB requires minimal configuration compared to traditional databases.</li>
    <li><strong>Real-Time Querying</strong>: DuckDB provides real-time query capabilities, allowing for dynamic exploration of match data without delays.</li>
    <li><strong>Lightweight and Self-Contained</strong>: Unlike larger database systems, DuckDB doesn't require heavy infrastructure, making it easy to integrate and deploy for projects of any size.</li>
  </ul>
  <p>
    By leveraging DuckDB, this project achieves:
  </p>
  <ul>
    <li>High-speed querying of cricket data.</li>
    <li>A lightweight setup that doesn’t compromise performance.</li>
    <li>A smooth and interactive user experience for data exploration.</li>
  </ul>
  <p>
    DuckDB’s simplicity and power ensure that the Cricket Analytics Dashboard remains fast, flexible, and user-friendly.
  </p>
</section>


  <h3 align="center">Dash</h3>
  <p> Dash is a powerful open-source Python framework for building interactive, data-driven web applications. Developed by Plotly, Dash is specifically designed for applications that involve data visualization, dashboards, and analytics, making it a popular choice for projects in data science and machine learning. </p>
  <p align="left"><a href="https://dash.plotly.com/tutorial"> Documentation </a></p>
  <section>
  <h2>Why DuckDB for This Project?</h2>
  <p>
    In this Cricket Analytics Dashboard, <strong>DuckDB</strong> is the database engine of choice, and for good reason:
  </p>
  <ul>
    <li><strong>Efficient Data Processing</strong>: DuckDB is optimized for analytical workloads, making it ideal for processing batting, bowling, and partnership statistics quickly and reliably.</li>
    <li><strong>Seamless Multi-Dataset Handling</strong>: With support for querying multiple datasets (e.g., <code>batsmen_details</code>, <code>bowlers_details</code>) effortlessly, DuckDB requires minimal configuration compared to traditional databases.</li>
    <li><strong>Real-Time Querying</strong>: DuckDB provides real-time query capabilities, allowing for dynamic exploration of match data without delays.</li>
    <li><strong>Lightweight and Self-Contained</strong>: Unlike larger database systems, DuckDB doesn't require heavy infrastructure, making it easy to integrate and deploy for projects of any size.</li>
  </ul>
  <p>
    By leveraging DuckDB, this project achieves:
  </p>
  <ul>
    <li>High-speed querying of cricket data.</li>
    <li>A lightweight setup that doesn’t compromise performance.</li>
    <li>A smooth and interactive user experience for data exploration.</li>
  </ul>
  <p>
    DuckDB’s simplicity and power ensure that the Cricket Analytics Dashboard remains fast, flexible, and user-friendly.
  </p>
</section>


  <h3 align="center">Plotly</h3>
  <p>Plotly is a powerful, open-source data visualization library in Python that enables the creation of highly interactive and visually appealing charts and graphs. It's widely used for building dashboards, exploratory data analysis, and data storytelling. Plotly charts are dynamic, allowing users to zoom, pan, hover, and interact with data points for deeper exploration. It supports a variety of visualizations, including line charts, bar charts, scatter plots, heatmaps, 3D plots, and more. Plotly works seamlessly with popular Python frameworks like Dash, Jupyter notebooks, and web applications.</p>
  <p align="left"><a href="https://plotly.com/python/"> Documentation </a></p>



<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- GETTING STARTED -->
## Getting Started

### Prerequisites
  Python 3.7 or higher is required. You can download it from [python.org](https://www.python.org/).


### Setup



1. Get a API Key at [RapidAPI](https://rapidapi.com/hub)
2. Clone the repo
   ```sh
   git clone https://github.com/rahulbijoor/CricInfo.git
   ```
3. Install the required packages
   ```sh
   pip install -r requirements.txt
   ```
4. Enter your API in `.env`
   ```
   RAPIDAPI_KEY2 = 'ENTER YOUR API';
   ```
5. Run the app.py
   ```sh
   python app.py
   ```

<p align="right">(<a href="#readme-top">back to top</a>)</p>







