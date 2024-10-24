import yaml
from cffconvert import Citation
import requests
import urllib.parse

def validate_cff_dict(cff_string: dict) -> bool:
    try:
        # Load the CFF content from the YAML string
        citation = Citation(cff_string)
        
        # Perform validation
        citation.validate()
        
        # If no exception is raised, the validation is successful
        return True
    except Exception as e:
        # If there is an exception, print the error and return False
        #print(f"Validation failed: {e}")
        return False

def map_license(license_string):
    # Define the base URL and the query
    base_url = 'https://observatory.openebench.bsc.es/licenses-mapping/map'

    # Encode the query
    encoded_query = urllib.parse.quote_plus(license_string)

    # Make the full URL
    url = f"{base_url}?q={encoded_query}"
    headers = {
    'Content-Type': 'application/json'  # Assuming the API expects JSON
    }
    print(url)

     
    # Send the GET request
    response = requests.post(url, data={}, headers=headers)

    # Check if the request was successful
    if response.status_code == 200:
        # Parse and print the JSON response
        data = response.json()  # Assuming the response is in JSON format
        if data:
            license_id = data.get('licenseId')
        else:
            license_id = None
            print(f"Error when mapping license: {response.status_code} - {response.text}")
    else:
        license_id = None
        print(f"Errorwhen mapping license: {response.status_code} - {response.text}")
    
    return license_id



def create_cff(metadata):
    cff_data = {
        'cff-version': '1.2.0',
        'message': 'If you use this software, please cite it as below.'
    }
    
    # Function to validate and remove the field if validation fails
    def add_field(cff_data, key, value):
        cff_data[key] = value
        cff_string = yaml.dump(cff_data, sort_keys=False)
        if not validate_cff_dict(cff_string):  # If validation fails, remove the field
            del cff_data[key]
            print(f"Field {key} with value {value} removed due to validation error.")
    
    # Add title
    if metadata.get('name'):
        cff_data['title'] = metadata.get('name')
    else:
        print("Error: No title provided.")
        return ""
    
    # Add authors
    if metadata.get('authors'):
        authors_data = []
        for author in metadata['authors']:
            author_entry = {
                'given-names': author['name'],
                'email': author['email'] if author.get('email') else None,
            }
            authors_data.append(author_entry)
        cff_data['authors'] = authors_data

    else:
        print("Error: No authors provided.")
        return ""

    
    # Add version
    if metadata.get('version'):
        add_field(cff_data, 'version', metadata.get('version'))
    
    # Add licenses
    if metadata.get('license'):
        licenses = []  # Initialize a list to store all valid license IDs
        for license_entry in metadata.get('license'):
            license_name = license_entry.get('name')
            if license_name:
                try:
                    license_id = map_license(license_name)  # Map the license name to the SPDX ID
                except Exception as e:
                    print(f"Error when mapping license: {e}")
                    license_id = None

                if license_id:
                    licenses.append(license_id)  # Add the valid license ID to the list

    if licenses:  # Only add the field if there are valid licenses
        add_field(cff_data, 'license', licenses)
    # Add keywords/tags
    if metadata.get('tags'):
        add_field(cff_data, 'keywords', metadata.get('tags'))
    
    # Add repository
    if metadata.get('repository'):
        add_field(cff_data, 'repository', metadata['repository'][0])
    
    # Add webpage
    if metadata.get('webpage'):
        add_field(cff_data, 'url', metadata['webpage'][0])
    
    
    
    # Add references/publications
    if metadata.get('publication'):
        references = []
        for publication in metadata['publication']:
            entry = {}
            if publication.get('doi'):
                entry['doi'] = publication['doi']
            if publication.get('title'):
                entry['title'] = publication['title']
            if publication.get('year'):
                entry['year'] = publication['year']
            if publication.get('journal'):
                entry['journal'] = publication['journal']
            references.append(entry)
        add_field(cff_data, 'references', references)

    # Final CFF string
    cff_string = yaml.dump(cff_data, sort_keys=False)
    
    # Validate final CFF
    if validate_cff_dict(cff_string):
        return cff_string
    else:        
        return cff_string  # Optional: return a message or log failure if needed

