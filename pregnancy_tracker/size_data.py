# Size comparisons for different pregnancy weeks
# Format: week -> (size comparison, length in cm/inches)

PREGNANCY_SIZES = {
    4: ("Poppy seed", "0.2 cm"),
    5: ("Sesame seed", "0.3 cm"),
    6: ("Lentil", "0.6 cm"),
    7: ("Blueberry", "1 cm"),
    8: ("Raspberry", "1.6 cm"),
    9: ("Grape", "2.3 cm"),
    10: ("Kumquat", "3.1 cm"),
    11: ("Fig", "4.1 cm"),
    12: ("Lime", "5.4 cm"),
    13: ("Pea pod", "7.4 cm"),
    14: ("Lemon", "8.7 cm"),
    15: ("Apple", "10.1 cm"),
    16: ("Avocado", "11.6 cm"),
    17: ("Turnip", "13 cm"),
    18: ("Bell pepper", "14.2 cm"),
    19: ("Mango", "15.3 cm"),
    20: ("Banana", "16.4 cm"),
    21: ("Carrot", "26.7 cm"),
    22: ("Papaya", "27.8 cm"),
    23: ("Grapefruit", "28.9 cm"),
    24: ("Corn", "30 cm"),
    25: ("Cauliflower", "34.6 cm"),
    26: ("Lettuce", "35.6 cm"),
    27: ("Cabbage", "36.6 cm"),
    28: ("Eggplant", "37.6 cm"),
    29: ("Butternut squash", "38.6 cm"),
    30: ("Coconut", "39.9 cm"),
    31: ("Pineapple", "41.1 cm"),
    32: ("Bok choy", "42.4 cm"),
    33: ("Durian", "43.7 cm"),
    34: ("Cantaloupe", "45 cm"),
    35: ("Honeydew melon", "46.2 cm"),
    36: ("Romaine lettuce", "47.4 cm"),
    37: ("Swiss chard", "48.6 cm"),
    38: ("Leek", "49.8 cm"),
    39: ("Watermelon", "50.7 cm"),
    40: ("Pumpkin", "51.2 cm"),
}

def get_size_for_week(week):
    """Get the size comparison for a given pregnancy week"""
    if week < 4:
        return ("Too early", "< 0.2 cm")
    elif week > 40:
        return ("Full term!", "~51 cm")
    else:
        return PREGNANCY_SIZES.get(week, ("Growing", f"~{10 + (week-10)*1.5:.1f} cm"))