# Latin Mass Chapels in LATAM

An interactive map showing Traditional Latin Mass chapels across Latin America (Central America, South America, and Mexico).

## Features

- Interactive map with chapel locations
- Chapel information including:
  - Name and address
  - Phone numbers
  - Website links
  - Mass schedules and comments
- Automatic data updates from SSPX websites
- Clean, modern UI with Bulma CSS and Nunito font

## Live Demo

The map is automatically deployed to GitHub Pages at: `https://yourusername.github.io/sspx-chapel-map/`

## Setup GitHub Pages

To enable automatic deployment to GitHub Pages:

1. Go to your repository on GitHub
2. Click on **Settings**
3. Scroll down to **Pages** in the left sidebar
4. Under **Source**, select **GitHub Actions**
5. The workflow will automatically run on every push to the main branch

## Local Development

1. Clone the repository
2. Install dependencies: `pip install -r requirements.txt`
3. Run the scraper to update data: `python scrap.py`
4. Open `index.html` in your browser

## Data Sources

The chapel data is automatically scraped from:
- Central America: https://centroamerica.fsspx.org/es/capillas-1
- South America: https://fsspx-sudamerica.org/es/capillas
- Mexico: https://fsspx.mx/es/capillas-2

## Contributing

Feel free to submit issues or pull requests to improve the map or add new features.