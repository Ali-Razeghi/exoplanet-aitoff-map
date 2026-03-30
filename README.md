# Exoplanet Aitoff Sky Map

This Python program fetches **live data from NASA Exoplanet Archive** and visualizes the distribution of confirmed exoplanets on an **Aitoff sky projection**.

- **Color** = discovery method (Transit, Radial Velocity, Imaging, Microlensing, etc.)
- **Shape** = discovery project (Kepler/K2, TESS, Other)

From an **astronomy perspective**, it shows how thousands of confirmed exoplanets are spread across the sky.  
From a **programming perspective**, it demonstrates how Python + scientific libraries can bring real NASA data into meaningful visualization.

---

## Requirements
- Python 3.9+
- Packages:
  ```bash
  pip install astroquery astropy pandas numpy matplotlib
  ```

---

## Usage
Run the program from the terminal:
```bash
python exoplanet_aitoff_kepler_tess.py
```
The program will:
1. Download the latest exoplanet dataset from NASA.
2. Render an Aitoff sky map.
3. Open the resulting image automatically.

---

## Example Output
*An Aitoff projection map with exoplanets, color-coded by discovery method and shaped by project.*

---

## License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
