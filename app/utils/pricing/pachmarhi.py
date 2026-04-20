def get_price_per_person(total_people: int , meal_preference : str , sharing_preference : str):
    print("Total People:", total_people , "Meal:", meal_preference , "Sharing:", sharing_preference)
    
    print("meal == with_meal?", meal_preference == "with_meal")
    print("repr:", repr(meal_preference))  # check for hidden spaces
    if meal_preference == "with_meal":
        if sharing_preference == "double":
             if total_people == 1:
                return 6999
             elif total_people <= 3:
                return 6999
             elif total_people <= 5:  
                return 6899
             else:   
                return 6799
        else:  # non-sharing
             if total_people == 1:
                return 6699
             elif total_people <= 3:
                return 6599
             elif total_people <= 5:  
                return 6499
             else:   
                return 6399
        
    else:
        if sharing_preference == "double":
             if total_people  == 1:
                return 6199
             elif total_people <= 3:
                return 6199
             elif total_people <= 5:
                return 6099
             else:
                return 5999
        else: # non-sharing
             if total_people  == 1:
                return 5899
             elif total_people <= 3:
                return 5799
             elif total_people <= 5:
                return 5699
             else:
                return 5599