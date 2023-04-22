import pandas as pd
from math import radians, sin, cos, sqrt, atan2

# Load the dataset
data = pd.read_csv('Crime_Data.csv')

# Preprocessing: Extract street names from the LOCATION column
data['street_name'] = data['LOCATION'].str.extract(r'\b\d{1,5}\s([A-Z0-9\s]+)')

# Assign weights to crime types
crime_weights = {
    'female_minor': 1.5,
    'female': 1.3,
    'minor': 1.2,
    'default': 1.0
}

# Calculate crime weight based on the victim's sex and descent
def calculate_crime_weight(row):
    is_female = row['Vict Sex'] == 'F'
    is_minor = row['Vict Descent'] == 'M'

    if is_female and is_minor:
        return crime_weights['female_minor']
    elif is_female:
        return crime_weights['female']
    elif is_minor:
        return crime_weights['minor']
    else:
        return crime_weights['default']

data['crime_weight'] = data.apply(calculate_crime_weight, axis=1)

# Haversine distance calculation
def haversine_distance(coord1, coord2):
    R = 6371  # Earth's radius in km
    lat1, lon1 = coord1
    lat2, lon2 = coord2

    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)
    a = sin(dlat / 2) ** 2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon / 2) ** 2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    return R * c

# Filter data within 20 miles of the user's location
user_location = (34.052235, -118.243683)  # Replace with user's latitude and longitude
data['distance'] = data.apply(lambda row: haversine_distance(user_location, (row['LAT'], row['LON'])), axis=1)
data = data[data['distance'] <= 20]

# Calculate the time of day weight
data['TIME OCC'] = pd.to_datetime(data['TIME OCC'], errors='coerce')
data['time_of_day_weight'] = data['TIME OCC'].apply(lambda x: 1.5 if 0 <= x.hour <= 6 else 1.0)

# Calculate danger value for each row based on the crime_weight and time_of_day_weight columns
data['weighted_count'] = data['crime_weight'] * data['time_of_day_weight']

# Aggregate danger values per block
block_danger_values = data.groupby(['street_name', 'LOCATION'])['weighted_count'].sum().reset_index()

# Export results as a CSV file
block_danger_values.to_csv('block_danger_values.csv', index=False)


# Preprocessing: Extract street names from the LOCATION column
data['street_name'] = data['LOCATION'].str.extract(r'\b\d{1,5}\s([A-Z0-9\s]+)')


# Remove rows with missing street names
data = data.dropna(subset=['street_name'])

# Convert ages to numeric values and fill missing ages with a placeholder value
data['Vict Age'] = pd.to_numeric(data['Vict Age'], errors='coerce').fillna(-1)

# Starting point (latitude, longitude)
user_location = (34.052235, -118.243683)  # Example: Los Angeles city center

# Filter data within a 20-mile radius of the starting point
def within_radius(row, user_location, radius_miles):
    location = (row['LAT'], row['LON'])
    distance = haversine_distance(user_location, location)
    return distance <= radius_miles

radius_miles = 20
data['within_radius'] = data.apply(within_radius, args=(user_location, radius_miles), axis=1)
data = data[data['within_radius']]

# Assign weights to different crime codes
crime_weights = {
    110: 5,  # Homicide
    210: 4,  # Robbery
    310: 3,  # Burglary
    330: 2,  # Theft
    510: 1,  # Vehicle theft
}

# Map the crime codes in the dataset to the weights
data['crime_weight'] = data['Crm Cd'].apply(lambda x: crime_weights.get(x, 0))

# Apply additional weights based on victim's age and sex
age_weight = 1.5
sex_weight = 1.5

data['age_weight'] = data['Vict Age'].apply(lambda x: age_weight if x < 18 else 1)
data['sex_weight'] = data['Vict Sex'].apply(lambda x: sex_weight if x == 'F' else 1)

# Assign time categories based on the time of day
def assign_time_category(time_str):
    hour = int(time_str[:2])

    if 6 <= hour < 12:
        return 'morning'
    elif 12 <= hour < 18:
        return 'afternoon'
    elif 18 <= hour < 24:
        return 'evening'
    else:
        return 'night'

data['time_category'] = data['TIME OCC'].apply(lambda x: assign_time_category(x.strftime('%H:%M')))

# Assign weights to the time categories
time_weights = {
    'morning': 1,
    'afternoon': 1.25,
    'evening': 1.5,
    'night': 1.75,
}

# Map the time categories in the dataset to the time weights
data['time_weight'] = data['time_category'].apply(lambda x: time_weights.get(x, 1))

# Calculate the weighted crime count
data['weighted_count'] = data['crime_weight'] * data['age_weight'] * data['sex_weight'] * data['time_weight']

# Haversine distance function
def haversine_distance(coord1, coord2):
    R = 6371  # Earth's radius in kilometers

    lat1, lon1 = coord1
    lat2, lon2 = coord2

    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)

    a = sin(dlat/2) * sin(dlat/2) + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon/2) * sin(dlon/2)
    c = 2 * atan2(sqrt(a), sqrt(1-a))

    distance = R * c

    return distance * 0.621371  # Convert kilometers to miles

# Aggregate danger values per block
block_danger_values = data.groupby(['street_name', 'LOCATION'])['weighted_count'].sum().reset_index()

# Export results as a CSV file
block_danger_values.to_csv('block_danger_values.csv', index=False)

