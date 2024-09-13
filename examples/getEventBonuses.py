from Event import Event

rarityBonus3654 = {
    'rarity_1': 0.5,
    'rarity_2': 1,
    'rarity_3': 5,
    'rarity_birthday': 7.5,
    'rarity_4': 10,
}

rarityBonus55108 = {
        'rarity_1': 0.5,
        'rarity_2': 1,
        'rarity_3': 5,
        'rarity_birthday': 10,
        'rarity_4': 15,
}

rarityBonus = {
    'rarity_1': 0.5,
    'rarity_2': 1,
    'rarity_3': 5,
    'rarity_birthday': 15,
    'rarity_4': 25,
}

## EventID required due to mastery bonuses
def getMaxBonus(cards, eventId):
    maxEB = 0
    useCards = set()
    
    bonuses = []
    lastEB = 0
    
    for card in cards:
        if card.unit not in useCards:
            maxEB += card.bonus
            if eventId >= 36 and eventId < 54:
                maxEB += rarityBonus3654[card.rarity]
            elif eventId >= 52 and eventId < 108: ## 52 on EN 54 on JP
                maxEB += rarityBonus55108[card.rarity]
            else:
                maxEB += rarityBonus[card.rarity]
            bonuses.append(maxEB - lastEB)
            lastEB = maxEB
            useCards.add(card.unit)
            
        if len(useCards) == 5:
            break
            
    return int(maxEB) / 100

def get4StarBonus(cards):
    maxEB = 0
    useCards = set()
    
    for card in cards:
        if card.unit not in useCards:
            maxEB += card.bonus
            useCards.add(card.unit)
            
        if len(useCards) == 5:
            break
            
    return int(maxEB) / 100

def get3StarBonus(cards):
    maxEB = 0
    useCards = set()
    
    for card in cards:
        if card.unit not in useCards and card.rarity != "rarity_4":
            maxEB += card.bonus
            useCards.add(card.unit)
            
        if len(useCards) == 5:
            break
            
    return int(maxEB) / 100

def getEventBonuses(eventId):
    
    eventData = Event()
    eventData.load()

    focusCards = eventData.getFocusEventCards(eventId)
    fullCards = eventData.getFullEventBonusCards(eventId)
    halfCards = eventData.getHalfEventBonusCards(eventId)

    highestPossible = getMaxBonus(focusCards + fullCards + halfCards, eventId)
    gachaless = get4StarBonus(fullCards + halfCards)
    no4Stars = get3StarBonus(fullCards + halfCards)
    
    print(f"Amount of 50%+ Cards: {len(focusCards + fullCards)}")
    
    print(f"Highest Possible Bonus: {highestPossible}")
    print(f"Gachaless Bonus: {gachaless}")
    print(f"No 4 Stars Bonus: {no4Stars}")
    
if __name__ == "__main__":
    getEventBonuses(75)  # Replace 75 with the desired event ID