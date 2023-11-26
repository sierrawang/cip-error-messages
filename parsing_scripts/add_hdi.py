import pandas as pd
import math

def convert_country_name(country):
    switcher = {
        'Hong Kong': 'Hong Kong, China (SAR)',
        'Turkey': 'Türkiye',
        'Czech Republic': 'Czechia',
        'Vietnam': 'Viet Nam',
        'Russia': 'Russian Federation',
        'Bolivia': 'Bolivia (Plurinational State of)',
        'Venezuela': 'Venezuela (Bolivarian Republic of)',
        'Iran': 'Iran (Islamic Republic of)',
        'South Korea': 'Korea (Republic of)',
        'Tanzania': 'Tanzania (United Republic of)',
        'Ivory Coast': "Côte d'Ivoire",
        'Moldova': 'Moldova (Republic of)',
        'Myanmar [Burma]': 'Myanmar',
        'Palestine': 'Palestine, State of',
        'Macao': None,
        'Taiwan': None,
        'Puerto Rico': None,
        'Kosovo': None,
        'New Caledonia': None,
        'Guam': None,
        'Guernsey': None,
        'Antarctica': None,
        'Laos': None,
        'British Indian Ocean Territory': None,
        'Somalia': None,
        'Monaco': None,
        'Nauru': None,
        'Jersey': None
    }
    return switcher.get(country, country)

def add_hdi_to_csv():
    demo_df = pd.read_csv('../data_files/sl_and_student_data.csv')
    demo_df['hdi'] = None

    # Skip the first four rows, set header as 0
    data = pd.read_excel("hdi.xlsx", skiprows=5, header=0)

    # Remove or Drop Column with NaN value
    data = data.dropna(how='all', axis=1)

    count = 0

    for index, row in demo_df.iterrows():
        country = row['country']
        country = convert_country_name(country)
        if country is None or (isinstance(country, float) and math.isnan(country)):
            print(f'No HDI for {country}')
            count += 1
            continue
        hdi = data[data['Country'] == country]['Value'].values[0]
        demo_df.at[index, 'hdi'] = hdi

    print(f'No HDI for {count} users. Total users: {len(demo_df)}')

    # Write the dataframe to a csv file
    # demo_df.to_csv('./cip_data_10-23/section_data_with_hdi.csv', index=False)
    demo_df.to_csv('./clean_folder/data_files/sl_and_student_data.csv', index=False)

if __name__ == "__main__":
    add_hdi_to_csv()