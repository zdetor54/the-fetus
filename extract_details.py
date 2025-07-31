def extract_patient_details_regex(text: str) -> dict:
    elements = text.split()
    extracted_data = dict()
    for element in elements:
        try:
            int(element)
            extracted_data["phone"] = element
        except ValueError:
            if "name" not in extracted_data:
                extracted_data["name"] = element
            else:
                extracted_data["surname"] = element
    print(elements)
    return extracted_data


if __name__ == "__main__":
    search_query = "φανή βασιλειάδου 6977221781"

    print(extract_patient_details_regex(search_query))
