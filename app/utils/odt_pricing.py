def get_price_per_person(total_people: int , meal_preference :bool) :
    if meal_preference == True :
        if total_people <= 3:
            return 1351
        elif total_people <= 5:
            return 1275
        else:
            return 1251
    else:
        if total_people <= 3:
            return 1151
        elif total_people <= 5:
            return 1125
        else:
            return 1101