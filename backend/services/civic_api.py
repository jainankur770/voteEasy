import requests
from backend.utils.config import settings

def get_civic_data(location: str) -> str:
    """
    Fetches real-time election context from Google Civic Information API.
    A test electionId (2000) is used to ensure mock response data exists
    year-round, but still localizes it to the user's provided state.
    """
    # Use Civic Key if provided, else fall back to Gemini Key as they are often the same project
    api_key = settings.google_civic_api_key or settings.gemini_api_key
    
    if not api_key or api_key == "placeholder_if_not_set":
        return "Civic data unavailable: Please provide an API key."

    # Using test electionId=2000 ensures we get formatted location datasets returned
    url = f"https://www.googleapis.com/civicinfo/v2/voterinfo?address={location}&electionId=2000&key={api_key}"
    
    try:
        response = requests.get(url, timeout=10)
        # Handle cases where API gets rate limited or the address isn't properly localized
        if response.status_code != 200:
            location_clean = location.strip() if location else "your area"
            return (
                f"LOCAL CIVIC DATA (Simulated Fallback for {location_clean}):\n"
                f"Official Election Website: https://voters.eci.gov.in/\n"
                f"Official Location Finder: https://electoralsearch.eci.gov.in/\n"
                f"Example Polling Location: 7:00 AM - 6:00 PM at Government School, {location_clean}\n"
            )
            
        data = response.json()
        
        # Parse useful components
        state_data = data.get("state", [{}])[0].get("electionAdministrationBody", {})
        polling_locations = data.get("pollingLocations", [])
        
        context_parts = []
        if state_data.get("electionInfoUrl"):
            context_parts.append(f"Official Election Website: {state_data['electionInfoUrl']}")
        if state_data.get("votingLocationFinderUrl"):
            context_parts.append(f"Official Location Finder: {state_data['votingLocationFinderUrl']}")
            
        if polling_locations:
            first_poll = polling_locations[0]
            address = first_poll.get('address', {})
            poll_string = f"Example Valid Polling Location: {first_poll.get('pollingHours', 'Standard hours')} at "
            poll_string += f"{address.get('locationName', 'Building')}, {address.get('line1', '')}, {address.get('city', '')}, {address.get('state', '')}"
            context_parts.append(poll_string)
            
        if context_parts:
            return "LOCAL CIVIC DATA:\n" + "\n".join(context_parts)
        return "No specific local polling data found in Civic API."
        
    except requests.exceptions.RequestException as e:
        print(f"Error calling Civic API: {e}")
        return "Civic data unavailable due to network."
