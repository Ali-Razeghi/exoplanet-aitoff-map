# Exoplanet Aitoff Sky Map

## Description

This Python project visualizes confirmed exoplanets using an Aitoff projection, based on live data retrieved from the NASA Exoplanet Archive.

The program maps the global sky distribution of exoplanets in celestial coordinates (Right Ascension and Declination), providing insight into observational biases and detection patterns from major missions such as Kepler and TESS.

From a scientific perspective, this visualization highlights how exoplanet discoveries are distributed across the sky. From a programming perspective, it demonstrates how Python and scientific libraries can transform real astronomical datasets into meaningful visual representations.

---

## Features

* Aitoff projection of exoplanet positions on the celestial sphere
* Live data retrieval from NASA Exoplanet Archive
* Color-coded visualization based on discovery method (Transit, Radial Velocity, Imaging, Microlensing, etc.)
* Shape-based differentiation of discovery missions (Kepler/K2, TESS, Other)
* Automatic rendering and display of the sky map

---

## Scientific Background

The Aitoff projection is commonly used in astronomy to represent the entire celestial sphere in a two-dimensional format. It preserves the global structure of sky distributions and is especially useful for large-scale surveys.

This project uses celestial coordinates (Right Ascension and Declination) to plot exoplanet positions. Since most exoplanets are discovered by specific missions focused on limited regions of the sky, this visualization also reveals observational biases and clustering patterns in detection data.

---

## Requirements

* Python 3.9+
* Required packages:

```bash
pip install astroquery astropy pandas numpy matplotlib
```

---

## How to Run

Run the program from the terminal:

```bash
python exoplanet_aitoff_kepler_tess.py
```

Main script: `exoplanet_aitoff_kepler_tess.py`

---

## Output

The program performs the following steps:

1. Retrieves the latest confirmed exoplanet dataset from the NASA Exoplanet Archive  
2. Converts celestial coordinates (Right Ascension and Declination) into projection format  
3. Generates an Aitoff sky projection map  
4. Displays the visualization automatically  

The resulting plot shows the global sky distribution of exoplanets, highlighting observational clustering from major surveys.

---

## Example Output

![Aitoff Map](assets/aitoff_map.png)

*(Make sure to add your generated image inside the `assets` folder.)*

---

## Future Improvements

* Add interactive visualization using Plotly
* Integrate filtering by planet radius, orbital period, or stellar type
* Enable real-time updates from the NASA API
* Improve coordinate transformation accuracy
* Export high-resolution publication-quality figures

---

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
