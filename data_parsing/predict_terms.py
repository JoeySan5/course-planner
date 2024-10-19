

def predict_offered_terms(historic_course_terms):
    odd_spring = True
    even_spring = True
    odd_fall = True
    even_fall = True

    terms_since_2019 = [201910, 201940, 202010, 202040, 202110, 202140, 202210, 202240, 202310, 202340, 202410, 202440, 202510]

    # historic_course_terms = [202010, 202040, 202140, 202240, 202410, 202440]
    historic_course_terms.sort()
    # If the course hasn't been offered since 2019, we assume it will not be offered in the future
    if len(historic_course_terms) == 0:
        return []
    offered_since = historic_course_terms[0]

    spring_suffix = 10
    fall_suffix = 40
    end_year = 2040

    for term in terms_since_2019:
        if term in historic_course_terms:
            # If the course was offered this term, we don't disqualify any categories
            continue
        elif term < offered_since:
            # If this term was before the course was ever offered, we don't disqualify any categories
            continue
        else:
            # If the course was not offered this term, we disqualify some category
            spring = term % 20 == spring_suffix % 20
            fall = term % 20 == fall_suffix % 20
            odd_year = term // 100 % 2 == 1
            even_year = term // 100 % 2 == 0
            if spring and odd_year:
                odd_spring = False
            elif spring and even_year:
                even_spring = False
            elif fall and odd_year:
                odd_fall = False
            elif fall and even_year:
                even_fall = False
            
            

    offered_terms = []
    offered_terms = list(set(historic_course_terms))
    for year in range(2025, end_year):
        odd = year % 2 == 1
        if odd:
            if odd_spring:
                offered_terms.append(year * 100 + spring_suffix)
            if odd_fall:
                offered_terms.append(year * 100 + fall_suffix)
        else:
            if even_spring:
                offered_terms.append(year * 100 + spring_suffix)
            if even_fall:
                offered_terms.append(year * 100 + fall_suffix)
    # Ensure unique terms and sort them
    offered_terms = list(set(offered_terms))
    offered_terms.sort()
    return offered_terms

    
def main():
    # Take user input for terms
    user_input = input("Enter historic course terms (comma-separated): ")
    historic_course_terms = list(map(int, user_input.split(',')))

    # Call the predict_offered_terms function
    result = predict_offered_terms(historic_course_terms)

    # Print the result
    print("Predicted offered terms:", result)

if __name__ == "__main__":
    main()

