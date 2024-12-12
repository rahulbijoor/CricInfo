
<a id="readme-top"></a>


<!-- PROJECT SHIELDS -->
<!--
*** I'm using markdown "reference style" links for readability.
*** Reference links are enclosed in brackets [ ] instead of parentheses ( ).
*** See the bottom of this document for the declaration of the reference variables
*** for contributors-url, forks-url, etc. This is an optional, concise syntax you may use.
*** https://www.markdownguide.org/basic-syntax/#reference-style-links
-->



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

  <h1 align="left">DuckDB</h1>
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


  <h1 align="left">Dash</h1>
  <p> Dash is a powerful open-source Python framework for building interactive, data-driven web applications. Developed by Plotly, Dash is specifically designed for applications that involve data visualization, dashboards, and analytics, making it a popular choice for projects in data science and machine learning. </p>
  <p align="left"><a href="https://dash.plotly.com/tutorial"> Documentation </a></p>
  <section>
  <h3>Why Dash for This Project?</h3>
  <p>
    In this Cricket Analytics Dashboard, <strong>Dash</strong> serves as the framework for building a highly interactive and visually appealing user interface. Here's why Dash is the ideal choice:
  </p>
  <ul>
    <li><strong>Interactive Data Visualization</strong>: Dash seamlessly integrates with Plotly to create dynamic and interactive visualizations, enabling users to explore cricket data effortlessly.</li>
    <li><strong>User-Friendly Development</strong>: Dash allows for rapid development of web applications with minimal coding, making it easy to design and deploy this analytics dashboard.</li>
    <li><strong>Python-Driven Framework</strong>: Built entirely in Python, Dash eliminates the need for switching between multiple programming languages, streamlining the development process.</li>
    <li><strong>Customizable and Extensible</strong>: With Dash’s extensive library of components and support for custom callbacks, the dashboard is tailored to meet specific project requirements.</li>
    <li><strong>Responsive Design</strong>: Dash ensures that the application works seamlessly across devices, providing an optimal user experience for desktop, tablet, and mobile users.</li>
  </ul>
  <p>
    By using Dash, this project achieves:
  </p>
  <ul>
    <li>Interactive scorecards, partnership charts, and data tables for cricket matches.</li>
    <li>A professional, responsive interface for users to analyze match data intuitively.</li>
    <li>Flexibility to add new features or visualizations as the project evolves.</li>
  </ul>
  <p>
    Dash’s ability to combine the power of Python with modern web technologies makes it the perfect choice for building this Cricket Analytics Dashboard.
  </p>
</section>



  <h1 align="left">Plotly</h1>
  <p>Plotly is a powerful, open-source data visualization library in Python that enables the creation of highly interactive and visually appealing charts and graphs. It's widely used for building dashboards, exploratory data analysis, and data storytelling. Plotly charts are dynamic, allowing users to zoom, pan, hover, and interact with data points for deeper exploration. It supports a variety of visualizations, including line charts, bar charts, scatter plots, heatmaps, 3D plots, and more. Plotly works seamlessly with popular Python frameworks like Dash, Jupyter notebooks, and web applications.</p>
  <p align="left"><a href="https://plotly.com/python/"> Documentation </a></p>

  <section>
  <h3>Why Plotly for This Project?</h3>
  <p>
    In this Cricket Analytics Dashboard, <strong>Plotly</strong> is the chosen visualization library due to its powerful and versatile capabilities:
  </p>
  <ul>
    <li><strong>Interactive Visualizations</strong>: Plotly allows for the creation of highly interactive charts, including hover effects, zooming, and tooltips, making data exploration intuitive and engaging.</li>
    <li><strong>Wide Range of Chart Types</strong>: It supports a variety of visualizations, such as bar charts, scatter plots, and dual-axis partnership charts, enabling rich representation of cricket statistics.</li>
    <li><strong>Customization and Styling</strong>: With Plotly, it is easy to customize visuals to match the aesthetic and functional needs of the dashboard, including color schemes, axis labeling, and annotations.</li>
    <li><strong>Seamless Dash Integration</strong>: Plotly integrates natively with Dash, ensuring smooth incorporation of visual elements into the web application.</li>
    <li><strong>Open-Source and Community-Driven</strong>: Being open-source, Plotly benefits from a large community, extensive documentation, and ongoing enhancements, making it a reliable choice for projects.</li>
  </ul>
  <p>
    By leveraging Plotly, this project delivers:
  </p>
  <ul>
    <li>Visually appealing and highly interactive scorecards and partnership charts.</li>
    <li>Intuitive insights into match data for cricket enthusiasts.</li>
    <li>A flexible and responsive user interface for exploring cricket statistics.</li>
  </ul>
  <p>
    Plotly’s interactivity and robust features make it the perfect tool for creating engaging and insightful visualizations in the Cricket Analytics Dashboard.
  </p>
</section>


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







