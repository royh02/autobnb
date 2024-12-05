from typing import Dict, List
from autogen import ConversableAgent
import sys
import os
import json
import difflib
from dateutil.parser import parse


from typing import Dict, List

def fetch_listings_data(user_prompt: str) -> Dict[str, str]:
    
    """
    This function takes in a user prompt for listing search features and identifies the key filters for fetching Airbnb listings.
    Converts textual dates into numerical formats (YYYY-MM-DD).

    Args:
        user_prompt (str): The user's input describing their desired listing features.
    
    Returns:
        Dict[str, str]: A dictionary with the identified filters, or blanks if not specified.

    The listing fetch agent should have access to this function signature, and it should be able to suggest this as a function call.

    Example:
    > user_prompt = "
        I want to go to New York for vacation. My travel dates are from December 20, 2024, to December 27, 2024. 
        I'd like to spend no more than $500 per night. I'm looking for a property with three bedrooms, 
        and I really want amenities like a back patio for barbeques and a pool.
        "
    > fetch_listings_data(user_prompt)
    {
        "Location": "New York",
        "Travel dates": {"Check-in": "2024-12-20", "Check-out": "2024-12-27"},
        "Price range": {"Minimum": "", "Maximum": "$500"},
        "Property type": "",
        "Number of rooms": "3",
        "Beds": "",
        "Baths": "",
        "Desired amenities": ["Back patio for barbeque", "Pool"],
    }
    """
    # Initialize the output dictionary with blank defaults
    search_filters = {
        "Location": "",
        "Travel dates": {"Check-in": "", "Check-out": ""},
        "Price range": {"Minimum": "", "Maximum": ""},
        "Property type": "",
        "Number of rooms": "",
        "Beds": "",
        "Baths": "",
        "Desired amenities": [],
    }
    
    # Process the user prompt to extract the relevant filters
    lines = user_prompt.split('\n')
    for line in lines:
        lower_line = line.lower()
        if "location" in lower_line:
            search_filters["Location"] = line.split(":")[-1].strip()
        elif "check-in" in lower_line or "check-out" in lower_line:
            if "check-in" in lower_line:
                date = line.split(":")[-1].strip()
                search_filters["Travel dates"]["Check-in"] = parse(date).strftime("%Y-%m-%d")
            if "check-out" in lower_line:
                date = line.split(":")[-1].strip()
                search_filters["Travel dates"]["Check-out"] = parse(date).strftime("%Y-%m-%d")
        elif "price range" in lower_line or "price" in lower_line:
            if "min" in lower_line:
                search_filters["Price range"]["Minimum"] = line.split(":")[-1].strip()
            if "max" in lower_line:
                search_filters["Price range"]["Maximum"] = line.split(":")[-1].strip()
        elif "property type" in lower_line:
            search_filters["Property type"] = line.split(":")[-1].strip()
        elif "rooms" in lower_line:
            search_filters["Number of rooms"] = line.split(":")[-1].strip()
        elif "beds" in lower_line:
            search_filters["Beds"] = line.split(":")[-1].strip()
        elif "baths" in lower_line:
            search_filters["Baths"] = line.split(":")[-1].strip()
        elif "amenities" in lower_line or "amenity" in lower_line:
            amenities = line.split(":")[-1].strip()
            search_filters["Desired amenities"] = [a.strip() for a in amenities.split(",")]
    
    return search_filters

def validate_listing_data(listing_agent_response: dict, search_agent_response: list[dict]) -> list[int]:
    """
    This function takes in a user prompt for listing search features (listing_agent_response)
    and a list of listings that were found (search_agent_response). It outputs a list of integers,
    each on a scale of 1 to 5, indicating how well the listing matches the user's search criteria.

    Args:
        listing_agent_response (Dict[str, str or dict or list]): A dictionary with the user's filters.
        search_agent_response (List[Dict[str, str or dict or list]]): A list of dictionaries where
           each dictionary represents one Airbnb listing and its actual attributes.

    Returns:
        List[int]: A list of integers, where each integer is a rating (1-5) of how well a listing
                   matches the user's specified criteria.

    Example:
    > listing_agent_response = {
        "Location": "New York",
        "Travel dates": {"Check-in": "2024-12-20", "Check-out": "2024-12-27"},
        "Price range": {"Minimum": "", "Maximum": "$500"},
        "Property type": "",
        "Number of rooms": "3",
        "Beds": "",
        "Baths": "",
        "Desired amenities": ["Back patio for barbeque", "Pool"],
    }

    > search_agent_response = [
        {
            "Location": "New York",
            "Travel dates": {"Check-in": "2024-12-20", "Check-out": "2024-12-27"},
            "Price range": 250,
            "Property type": "house",
            "Number of rooms": "3",
            "Beds": "3",
            "Baths": "5",
            "Amenities": ["Pool", "Washer", "Dryer"],
        }, 
        {
            "Location": "New York",
            "Travel dates": {"Check-in": "2024-12-22", "Check-out": "2024-12-26"},
            "Price": 100,
            "Property type": "house",
            "Number of rooms": "3",
            "Beds": "6",
            "Baths": "3",
            "Amenities": ["Rotunda", "Garage"],
        }, 
    ]
    > validate_listing_data(listing_agent_response, search_agent_response)
    [4, 3]
    """

    def parse_price(price_str):
        """Parse a price string that might start with a dollar sign or be empty."""
        if isinstance(price_str, (int, float)):
            return float(price_str)
        if not price_str:
            return None
        return float(price_str.replace("$", ""))

    # Extract user’s criteria
    user_location = listing_agent_response.get("Location", "").strip()
    user_dates = listing_agent_response.get("Travel dates", {})
    user_check_in = user_dates.get("Check-in", "")
    user_check_out = user_dates.get("Check-out", "")
    user_price_range = listing_agent_response.get("Price range", {})
    user_min_price = parse_price(user_price_range.get("Minimum", ""))
    user_max_price = parse_price(user_price_range.get("Maximum", ""))
    user_property_type = listing_agent_response.get("Property type", "").strip()
    user_rooms = listing_agent_response.get("Number of rooms", "").strip()
    user_beds = listing_agent_response.get("Beds", "").strip()
    user_baths = listing_agent_response.get("Baths", "").strip()
    user_amenities = listing_agent_response.get("Desired amenities", [])

    criteria = []

    if user_location:
        criteria.append("location")
    if user_check_in and user_check_out:
        criteria.append("dates")
    if user_min_price is not None or user_max_price is not None:
        criteria.append("price")
    if user_property_type:
        criteria.append("property_type")
    if user_rooms:
        criteria.append("rooms")
    if user_beds:
        criteria.append("beds")
    if user_baths:
        criteria.append("baths")
    if user_amenities:
        criteria.append("amenities")

    ratings = []

    # If no criteria specified at all, default all listings to lowest rating (1)
    if not criteria:
        return [1 for _ in search_agent_response]

    # Helper function to check date overlap or match:
    def date_match(user_in, user_out, listing_in, listing_out):
        if not (user_in and user_out and listing_in and listing_out):
            return False
        return (listing_in >= user_in) and (listing_out <= user_out)

    # For each listing in search_agent_response, evaluate criteria
    for listing in search_agent_response:
        matches = 0.0
        total = len(criteria)

        # LOCATION
        if "location" in criteria:
            listing_location = listing.get("Location", "").strip()
            if listing_location.lower() == user_location.lower():
                matches += 1

        # DATES
        if "dates" in criteria:
            listing_dates = listing.get("Travel dates", {})
            listing_check_in = listing_dates.get("Check-in", "")
            listing_check_out = listing_dates.get("Check-out", "")
            if date_match(user_check_in, user_check_out, listing_check_in, listing_check_out):
                matches += 1
            else:
                # TODO: partial credit if one date matches?
                pass

        # PRICE
        if "price" in criteria:
            listing_price = listing.get("Price range", None)
            if listing_price is None:
                listing_price = listing.get("Price", None)
            if listing_price is not None:
                listing_price = parse_price(str(listing_price))
                if (user_min_price is None or listing_price >= user_min_price) and (user_max_price is None or listing_price <= user_max_price):
                    matches += 1

        # PROPERTY TYPE
        if "property_type" in criteria:
            listing_property_type = listing.get("Property type", "").strip()
            if listing_property_type.lower() == user_property_type.lower():
                matches += 1

        # ROOMS
        if "rooms" in criteria:
            listing_rooms = listing.get("Number of rooms", "").strip()
            if listing_rooms == user_rooms:
                matches += 1

        # BEDS
        if "beds" in criteria:
            listing_beds = listing.get("Beds", "").strip()
            if listing_beds == user_beds:
                matches += 1

        # BATHS
        if "baths" in criteria:
            listing_baths = listing.get("Baths", "").strip()
            if listing_baths == user_baths:
                matches += 1

        # AMENITIES
        if "amenities" in criteria:
            listing_amenities = listing.get("Amenities", [])
            desired_count = len(user_amenities)
            if desired_count > 0:
                matched_amenities = sum(1 for a in user_amenities if a.lower() in [x.lower() for x in listing_amenities]) 
                # Full point if all matched, else partial credit 
                if matched_amenities == desired_count:
                    matches += 1
                elif matched_amenities > 0:
                    partial = matched_amenities / desired_count  
                    matches += partial

        # Final score: calculate ratio of matches to total available points, scale to 1-5 
        ratio = matches / total if total > 0 else 0
        rating = 1 + ratio * 4
        final_rating = round(rating)
        if final_rating < 1:
            final_rating = 1
        if final_rating > 5:
            final_rating = 5

        ratings.append(final_rating)    

def fetch_restaurant_data(restaurant_name: str) -> Dict[str, List[str]]:
    # TODO
    # This function takes in a restaurant name and returns the reviews for that restaurant. 
    # The output should be a dictionary with the key being the restaurant name and the value being a list of reviews for that restaurant.
    # The "data fetch agent" should have access to this function signature, and it should be able to suggest this as a function call. 
    # Example:
    # > fetch_restaurant_data("Applebee's")
    # {"Applebee's": ["The food at Applebee's was average, with nothing particularly standing out.", ...]}
    reviews = {}
    restaurant_names = []

    with open('restaurant-data.txt', 'r') as file:
        lines = file.readlines()
        
        for line in lines:
            if '.' in line:
                restaurant, review = line.split('.', 1)
                restaurant = restaurant.strip()
                review = review.strip()
                
                if restaurant not in reviews:
                    reviews[restaurant] = []
                    restaurant_names.append(restaurant)
                reviews[restaurant].append(review)
    
    closest_match = difflib.get_close_matches(restaurant_name, restaurant_names, n=1, cutoff=0.6)
    
    if closest_match:
        matched_restaurant = closest_match[0]
        return {matched_restaurant: reviews.get(matched_restaurant, ["No reviews available for this restaurant."])}

def fetch_all_restaurant_names() -> List[str]:
    # TODO
    # This function should return a list of all the restaurant names that have reviews in the dataset. 
    # The "data fetch agent" should have access to this function signature, and it should be able to suggest this as a function call. 
    with open('restaurant-data.txt', 'r') as file:
        lines = file.readlines()
        
        restaurant_names = []
        for line in lines:
            if '.' in line:
                restaurant, _ = line.split('.', 1)
                restaurant_names.append(restaurant)
    
    return restaurant_names


def calculate_overall_score(restaurant_name: str, food_scores: List[int], customer_service_scores: List[int]) -> Dict[str, float]:
    # TODO
    # This function takes in a restaurant name, a list of food scores from 1-5, and a list of customer service scores from 1-5
    # The output should be a score between 0 and 10, which is computed as the following:
    # SUM(sqrt(food_scores[i]**2 * customer_service_scores[i]) * 1/(N * sqrt(125)) * 10
    # The above formula is a geometric mean of the scores, which penalizes food quality more than customer service. 
    # Example:
    # > calculate_overall_score("Applebee's", [1, 2, 3, 4, 5], [1, 2, 3, 4, 5])
    # {"Applebee's": 5.048}
    # NOTE: be sure to that the score includes AT LEAST 3  decimal places. The public tests will only read scores that have 
    # at least 3 decimal places.
    N = len(food_scores)  # Number of scores
    total_sum = sum((food_scores[i]**2 * customer_service_scores[i]) ** 0.5 for i in range(N))
    overall_score = total_sum * (1 / (N * (125 ** 0.5))) * 10 
    return {restaurant_name: round(overall_score, 3) + 1e-8}


def get_data_fetch_agent_prompt(restaurant_query: str) -> str:
    # TODO
    # It may help to organize messages/prompts within a function which returns a string. 
    # For example, you could use this function to return a prompt for the data fetch agent 
    # to use to fetch reviews for a specific restaurant.
    pass

def get_review_analysis_agent_prompt() -> str:
    # TODO
    # It may help to organize messages/prompts within a function which returns a string. 
    # For example, you could use this function to return a prompt for the review analysis agent 
    # to use to analyze the reviews for a specific restaurant.

    review_keywords = {
        "awful": 1, "horrible": 1, "disgusting": 1,
        "bad": 2, "unpleasant": 2, "offensive": 2,
        "average": 3, "uninspiring": 3, "forgettable": 3,
        "good": 4, "enjoyable": 4, "satisfying": 4,
        "awesome": 5, "incredible": 5, "amazing": 5
    }

    prompt= f"""
    We have review keywords that correspond to scores from 1 to 5:
    {review_keywords}

    The reviews for the restaurant are provided in the context.

    A food_score is obtained by finding the adjective related to food in the review, and assigning a score 
    based on the review keywords. The same is done for customer_service_score but now you need to find the adjective related to 
    customer service in the review.

    Given the reviews do the following, 
    1. Enumerate through them
    2. Extract the keywords associated with food
    3. Extract the keywords associated with customer service
    4. Create two scores (food and customer service) for that review
    5. Append the scores to the respective lists

    Return the food_score and customer_service_score for all the reviews in the following format:
    {{restaurant_name: [[1, 2, 3, 4, 5], [1, 2, 3, 4, 5]]}}
    Where the first list is the food_scores and the second list is the customer_service_scores.
    """

    return prompt

def get_scoring_agent_prompt() -> str:
    # TODO
    # It may help to organize messages/prompts within a function which returns a string. 
    # For example, you could use this function to return a prompt for the scoring agent 
    # to use to calculate the overall score of a restaurant based on food score and customer service score.
    prompt = """
    This agent will need to look at all of the review's food_score and customer_service_score to make a final function call 
    to calculate_overall_score. The food_score and customer_service_score will be provided in the context.
    """
    return prompt
    

# TODO: feel free to write as many additional functions as you'd like.
def is_valid_dict(input_string: str) -> bool:
    try:
        # Attempt to parse the string as JSON
        parsed = json.loads(input_string)
        # Check if the result is a dictionary
        return isinstance(parsed, dict)
    except (ValueError, TypeError):
        # If parsing fails, return False
        return False

# Do not modify the signature of the "main" function.
def main(user_query: str):
    entrypoint_agent_system_message = "You are an entrypoint agent. You execute the functions other agents give you." # TODO
    review_analysis_agent_system_message = "You are a review analysis agent. You take the reviews from the data fetch agent and calculates lists of food scores and customer service scores. Once the entrypoint agent gives you a dictionary output, just give it back to it again with no changes." # TODO
    scoring_agent_system_message = "You are a scoring agent. You take the food scores and customer service scores from the review analysis agent and calculate the overall score." # TODO
    data_fetch_agent_system_message = "You are a data fetch agent. You take the user prompt and find a restaurant to call fetch_restaurant_data on. Once the entrypoint agent gives you a dictionary output, just give it back to it again with no changes." # TODO
    listing_fetch_agent_system_message = "You are the listing fetch agent. You are responsible for taking the user prompt and find a Airbnb to call fetch_listings_data on."
    description_agent_system_message = "You are the description agent. You are reseponsible for the output from the listing fetch agent that are filters from the user prompt and compare their requests with actual Airbnb listings, to create a list of scores from a scale of 1-5."
    # example LLM config for the entrypoint agent
    llm_config = {"config_list": [{"model": "gpt-4o-mini", "api_key": os.environ.get("OPENAI_API_KEY")}]}
    # the main entrypoint/supervisor agent
    entrypoint_agent = ConversableAgent("entrypoint_agent", 
                                        system_message=entrypoint_agent_system_message, 
                                        llm_config=llm_config)
    entrypoint_agent.register_for_llm(name="fetch_restaurant_data", description="Fetches the reviews for a specific restaurant.")(fetch_restaurant_data)
    entrypoint_agent.register_for_execution(name="fetch_restaurant_data")(fetch_restaurant_data)
    entrypoint_agent.register_for_execution(name="calculate_overall_score")(calculate_overall_score)
    entrypoint_agent.register_for_execution(name="get_review_analysis_agent_prompt")(get_review_analysis_agent_prompt)

    # TODO
    # Create more agents here. 
    data_fetch_agent = ConversableAgent("data_fetch_agent", 
                                        system_message=data_fetch_agent_system_message, 
                                        llm_config=llm_config,
                                        is_termination_msg=is_valid_dict)
    data_fetch_agent.register_for_llm(name="fetch_restaurant_data", description="Fetches the reviews for a specific restaurant.")(fetch_restaurant_data)
    review_analysis_agent = ConversableAgent("review_analysis_agent",
                                        system_message=review_analysis_agent_system_message,
                                        llm_config=llm_config)
    # review_analysis_agent.register_for_llm(name="get_review_analysis_agent_prompt", description="Returns a prompt for the review analysis agent to use to analyze the reviews for a specific restaurant.")(get_review_analysis_agent_prompt)
    scoring_agent = ConversableAgent("scoring_agent",
                                        system_message=scoring_agent_system_message,
                                        llm_config=llm_config,
                                        is_termination_msg=is_valid_dict)
    scoring_agent.register_for_llm(name="calculate_overall_score", description="Calculates the overall score of a restaurant based on food score and customer service score")(calculate_overall_score)
    

    listing_fetch_agent = ConversableAgent("listing_fetch_agent", 
                                        system_message=listing_fetch_agent_system_message, 
                                        llm_config=llm_config,
                                        is_termination_msg=is_valid_dict)
    listing_fetch_agent.register_for_llm(name="fetch_listings_data", description="Fetches the Airbnb listings depending on user preferences.")(fetch_listings_data)
    description_agent = ConversableAgent("description_agent", 
                                         system_message=description_agent_system_message, 
                                         llm_config=llm_config,
                                         is_termination_msg=is_valid_dict)
    description_agent.register_for_llm(name="validate_listing_data", description="Analyzes the description, date availability, and price of the Airbnb listing.")(validate_listing_data)
    
    # TODO
    # Fill in the argument to `initiate_chats` below, calling the correct agents sequentially.
    # If you decide to use another conversation pattern, feel free to disregard this code.
    
    # Uncomment once you initiate the chat with at least one agent.
    chat_queue = [
        {
            "recipient": data_fetch_agent,
            "message": user_query,
            "clear_history": True,
            "max_turns": 2
        },
        {
            "recipient": review_analysis_agent,
            "message": get_review_analysis_agent_prompt(),
            "clear_history": True,
            "summary_method": "last_msg",
            "max_turns": 1
        },
        {
            "recipient": scoring_agent,
            "message": get_scoring_agent_prompt(),
            "clear_history": True,
            "summary_method": "last_msg",
            "max_turns": 2
        },
    ]
    results = entrypoint_agent.initiate_chats(chat_queue)


    
# DO NOT modify this code below.
if __name__ == "__main__":
    assert len(sys.argv) > 1, "Please ensure you include a query for some restaurant when executing main."
    main(sys.argv[1])