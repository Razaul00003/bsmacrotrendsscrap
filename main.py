import requests
from bs4 import BeautifulSoup
import pandas as pd

# Create an empty DataFrame to store the data
df = pd.DataFrame()

# Define the URL of the main page
main_url = 'https://www.macrotrends.net/countries/ranking/carbon-co2-emissions'

# Define the headers
headerstxt = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'
}

# Send an HTTP GET request to the main page with the specified headers
response = requests.get(main_url, headers=headerstxt)

# Check if the request was successful (status code 200)
if response.status_code == 200:
    print('rank page scraping started')
    # Parse the HTML content of the page
    soup = BeautifulSoup(response.text, 'html.parser')
    # Find the first table on the main page
    main_table = soup.find('table')

    # Check if the main table was found
    if main_table:
        # Iterate through the rows of the table
        for index, row in enumerate(main_table.find('tbody').find_all('tr')):
            # Extract data from the columns
            columns = row.find_all('td')
            country_name = columns[0].text.strip()

            # Find the hyperlink to the country page
            country_link = columns[0].find('a')['href']

            # Construct the URL for the country page
            country_page_url = f'https://www.macrotrends.net{country_link}'

            # Send an HTTP GET request to the country page with the specified headers
            country_page_response = requests.get(
                country_page_url, headers=headerstxt)

            # Check if the request was successful
            if country_page_response.status_code == 200:
                print('country page scraping started')
                # Parse the HTML content of the country page
                country_page_soup = BeautifulSoup(
                    country_page_response.text, 'html.parser')

                # Find all tables on the country page with the specified class
                country_tables = country_page_soup.find_all(
                    'table', class_='historical_data_table table table-striped table-bordered')
                # Iterate through the tables on the country page

                country_table = country_tables[1]
                # Check if the first header (th) in the table is "Year"
                headcolums = country_table.find_all('thead')[1].find_all('th')
                if headcolums and headcolums[0].text.strip() == "Year":
                    # Extract data from the table
                    data = []
                    for country_row in country_table.find('tbody').find_all('tr'):
                        country_columns = country_row.find_all('td')
                        year = country_columns[0].text.strip()
                        co2_emission = country_columns[1].text.strip()
                        data.append((year, co2_emission))

                    # Create a DataFrame from the data with 'Year' and 'Country' columns
                    country_df = pd.DataFrame(data, columns=['Year', 'CO2 Emission'])

                    # Add the 'Country' column with the country name
                    country_df['Country'] = country_name

                    # Pivot the DataFrame so that years become columns
                    country_df = country_df.pivot(index='Country', columns='Year', values='CO2 Emission')

                    # Reset the index
                    country_df.reset_index(inplace=True)

                    # Append the country DataFrame to the main DataFrame
                    df = pd.concat([df, country_df], ignore_index=True)
                # Close the country page response
                country_page_response.close()
                print(f'{index}.{country_name}: rank page scraping ended')

            else:
                print(
                    f"Failed to retrieve data from the country page: {country_page_url}")

    else:
        print("Main table not found on the main page.")
else:
    print(
        f"Failed to retrieve data from the main page. Status code: {response.status_code}")

# Save the DataFrame to a CSV file
df.to_csv('co2_emissions.csv', index=False)

# Close the main page response
response.close()
