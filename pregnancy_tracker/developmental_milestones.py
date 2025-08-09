"""Developmental milestones and anatomy updates for each week of pregnancy."""

def get_milestone_for_week(week):
    """Get developmental milestone information for a specific week.
    
    Returns:
        dict: Contains 'size', 'weight', and 'development' keys with milestone info
    """
    
    milestones = {
        4: {
            "size": "Poppy seed",
            "weight": "< 1g",
            "development": "Neural tube forming, heart beginning to develop"
        },
        5: {
            "size": "Sesame seed",
            "weight": "< 1g",
            "development": "Heart starts beating, arm & leg buds appear"
        },
        6: {
            "size": "Lentil",
            "weight": "< 1g",
            "development": "Eyes & ears forming, jaw & throat developing"
        },
        7: {
            "size": "Blueberry",
            "weight": "< 1g",
            "development": "Brain hemispheres forming, arms & legs growing"
        },
        8: {
            "size": "Kidney bean",
            "weight": "1g",
            "development": "Fingers & toes forming, eyelids developing"
        },
        9: {
            "size": "Grape",
            "weight": "2g",
            "development": "Essential organs formed, elbows & toes visible"
        },
        10: {
            "size": "Kumquat",
            "weight": "4g",
            "development": "Vital organs functioning, tooth buds forming"
        },
        11: {
            "size": "Fig",
            "weight": "7g",
            "development": "Bones hardening, hair follicles forming"
        },
        12: {
            "size": "Lime",
            "weight": "14g",
            "development": "Reflexes starting, kidneys producing urine"
        },
        13: {
            "size": "Peapod",
            "weight": "23g",
            "development": "Fingerprints forming, vocal cords developing"
        },
        14: {
            "size": "Lemon",
            "weight": "43g",
            "development": "Face muscles working, can squint & frown"
        },
        15: {
            "size": "Apple",
            "weight": "70g",
            "development": "Legs longer than arms, all joints working"
        },
        16: {
            "size": "Avocado",
            "weight": "100g",
            "development": "Can hear sounds, eyes moving side to side"
        },
        17: {
            "size": "Turnip",
            "weight": "140g",
            "development": "Skeleton hardening, sweat glands developing"
        },
        18: {
            "size": "Bell pepper",
            "weight": "190g",
            "development": "Ears in final position, myelin protecting nerves"
        },
        19: {
            "size": "Heirloom tomato",
            "weight": "240g",
            "development": "Sensory development, vernix caseosa forming"
        },
        20: {
            "size": "Banana",
            "weight": "300g",
            "development": "Can swallow, producing meconium"
        },
        21: {
            "size": "Carrot",
            "weight": "360g",
            "development": "Eyebrows & eyelids complete, responds to sounds"
        },
        22: {
            "size": "Spaghetti squash",
            "weight": "430g",
            "development": "Eyes can perceive light, grip strengthening"
        },
        23: {
            "size": "Mango",
            "weight": "500g",
            "development": "Hearing fully developed, rapid eye movement"
        },
        24: {
            "size": "Corn cob",
            "weight": "600g",
            "development": "Lungs developing branches, taste buds forming"
        },
        25: {
            "size": "Rutabaga",
            "weight": "660g",
            "development": "Responding to voice, nostrils opening"
        },
        26: {
            "size": "Scallion bunch",
            "weight": "760g",
            "development": "Eyes opening, inhaling & exhaling amniotic fluid"
        },
        27: {
            "size": "Cauliflower",
            "weight": "875g",
            "development": "Brain tissue developing, regular sleep cycles"
        },
        28: {
            "size": "Eggplant",
            "weight": "1kg",
            "development": "Can blink, dreaming during REM sleep"
        },
        29: {
            "size": "Butternut squash",
            "weight": "1.2kg",
            "development": "Muscles & lungs maturing, head growing"
        },
        30: {
            "size": "Large cabbage",
            "weight": "1.3kg",
            "development": "Red blood cell production, brain developing rapidly"
        },
        31: {
            "size": "Coconut",
            "weight": "1.5kg",
            "development": "All five senses working, processing information"
        },
        32: {
            "size": "Jicama",
            "weight": "1.7kg",
            "development": "Bones hardening, practicing breathing"
        },
        33: {
            "size": "Pineapple",
            "weight": "1.9kg",
            "development": "Immune system developing, detecting light"
        },
        34: {
            "size": "Cantaloupe",
            "weight": "2.1kg",
            "development": "Central nervous system maturing, recognizing songs"
        },
        35: {
            "size": "Honeydew melon",
            "weight": "2.4kg",
            "development": "Kidneys fully developed, liver processing waste"
        },
        36: {
            "size": "Romaine lettuce",
            "weight": "2.6kg",
            "development": "Shedding lanugo, digestive system ready"
        },
        37: {
            "size": "Swiss chard",
            "weight": "2.9kg",
            "development": "Full term, practicing breathing & sucking"
        },
        38: {
            "size": "Leek",
            "weight": "3.1kg",
            "development": "Organs mature, brain & nervous system ready"
        },
        39: {
            "size": "Mini watermelon",
            "weight": "3.3kg",
            "development": "Fully developed, building fat layers"
        },
        40: {
            "size": "Small pumpkin",
            "weight": "3.5kg",
            "development": "Ready for birth, all systems functional"
        }
    }
    
    # Handle weeks outside normal range
    if week < 4:
        return {
            "size": "Poppy seed",
            "weight": "< 1g",
            "development": "Cells dividing rapidly, implantation occurring"
        }
    elif week > 40:
        return {
            "size": "Small pumpkin",
            "weight": "3.5kg+",
            "development": "Fully developed, ready for arrival any day"
        }
    
    return milestones.get(week, milestones[40])