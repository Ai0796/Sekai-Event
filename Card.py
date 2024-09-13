class Card:
    
    def __init__(self, card, eventId, bonus, Event) -> None:
        self.cardId = card
        self.eventId = eventId
        self.bonus = bonus
        self.card = Event.getCard(self.cardId)
        self.rarity = self.card['cardRarityType']
        self.unit = self.card['characterId']