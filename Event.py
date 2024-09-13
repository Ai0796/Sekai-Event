import numpy as np
import pandas as pd
from Card import Card
from Cache import Cache

class Event:
    
    DB_LINK = "https://raw.githubusercontent.com/Sekai-World/sekai-master-db-en-diff/main"
    JP_DB_LINK = "https://raw.githubusercontent.com/Sekai-World/sekai-master-db-diff/main"
    
    RARITYWORTH = {
        'rarity_1': '1',
        'rarity_2': '2',
        'rarity_3': '3',
        'rarity_birthday': '4',
        'rarity_4': '5',
    }
    
    def __init__(self, isJP=False):
        
        self.resetDic()
        self.isJP = isJP
        
    def load(self):
        if self.isJP:
            self.DB_LINK = self.JP_DB_LINK
            
        eventURL = f"{self.DB_LINK}/events.json"
        eventCardURL = f"{self.DB_LINK}/eventCards.json"
        eventDeckURL = f"{self.DB_LINK}/eventDeckBonuses.json"
        cardURL = f"{self.DB_LINK}/cards.json"
        charactersURL = f"{self.DB_LINK}/gameCharacters.json"
        characterUnitsURL = f"{self.DB_LINK}/gameCharacterUnits.json"
        unitsURL = f"{self.DB_LINK}/unitProfiles.json"
        
        self.cache = Cache()
        
        # self.tiers = rapidjson.load(open("lib/tiers.json", "r"))
        self.eventData = self.parseWebJSON(eventURL)
        self.eventCardData = self.parseWebJSON(eventCardURL)
        self.eventDeckData = self.parseWebJSON(eventDeckURL)
        self.cardData = self.parseWebJSON(cardURL)
        self.charactersData = self.parseWebJSON(charactersURL)
        self.characterUnitsData = self.parseWebJSON(characterUnitsURL)
        self.unitsData = self.parseWebJSON(unitsURL)
            
    def resetDic(self):
        self.dataDic = {
            "Event ID": [],
            "Date": [],
            "Time": [],
            "Main Character": [],
            "Side Character1": [],
            "Side Character2": [],
            "EventType": [],
            # "EventDeck": [],
            "EventPoints": [],
            "EventLength": [],
            "Percentage": [],
            "Tier": [],
            "Unit": [],
            "Final Score": []
        }
    
    def parseWebJSON(self, url):
        key = url.split("/")[-1].split(".")[0]
        self.cache.load(key, url)

    def getEvent(self, eventId):
        for event in self.eventData:
            if event["id"] == eventId:
                return event
        return None

    def getEventCards(self, eventId):
        eventCards = []
        for eventCard in self.eventCardData:
            if eventCard["eventId"] == eventId:
                eventCards.append(eventCard)
        return eventCards
    
    def getCard(self, cardId):
        for card in self.cardData:
            if card["id"] == cardId:
                return card
        return None

    def getCharacterID(self, cardId):
        return self.getCard(cardId)["characterId"]
    
    def getCharacter(self, characterId):
        for character in self.charactersData:
            if character["id"] == characterId:
                return character
            
    def getCharacterUnit(self, characterUnitId):
        for characterUnit in self.characterUnitsData:
            if characterUnit["id"] == characterUnitId:
                return characterUnit
    
    def getEventDeck(self, eventId):
        eventDeck = []
        for card in self.eventDeckData:
            if card["eventId"] == eventId and \
                "gameCharacterUnitId" in card and \
                "cardAttr" not in card:
                eventDeck.append(card)
                
        return eventDeck
    
    def getFullEventBonusCards(self, eventId) -> list[Card]:
        if eventId == 38:
            return []
        eventDeckBonus = []
        for card in self.eventDeckData:
            if card["eventId"] == eventId and int(card['bonusRate']) >= 50:
                eventDeckBonus.append(card)
                
        bonus = 50
        units = []
        attr = None
                
        for card in eventDeckBonus:
            if 'gameCharacterUnitId' in card:
                gameChar = self.getCharacterUnit(card['gameCharacterUnitId'])
                if gameChar['id'] == gameChar['gameCharacterId']:
                    units.append((gameChar['gameCharacterId'], None))
                else:
                    units.append((gameChar['gameCharacterId'], gameChar['unit']))
            if 'cardAttr' in card:
                attr = card['cardAttr']
                
        bonus = 50
        cards = []
        
        for unit, group in units:
            cards += self.getCardByUnit(unit, group, eventId)
            
        focusCards = self.getFocusEventCards(eventId)
        cards = set(cards) & set(self.getCardByAttr(attr, eventId))
        cards -= set(card.cardId for card in self.getFocusEventCards(eventId))
        cards = [Card(card, eventId, bonus, self) for card in cards]
        
        cards.sort(key=lambda x: self.RARITYWORTH[x.rarity], reverse=True)
                
        return cards
    
    def getHalfEventBonusCards(self, eventId) -> list[Card]:
        if eventId == 38:
            return []
        eventDeckBonus = []
        for card in self.eventDeckData:
            if card["eventId"] == eventId and int(card['bonusRate']) >= 20 and int(card['bonusRate']) < 50:
                eventDeckBonus.append(card)
            
        units = []
        attr = None
                
        for card in eventDeckBonus:
            if 'gameCharacterUnitId' in card:
                gameChar = self.getCharacterUnit(card['gameCharacterUnitId'])
                if gameChar['id'] == gameChar['gameCharacterId']:
                    units.append((gameChar['gameCharacterId'], None))
                else:
                    units.append((gameChar['gameCharacterId'], gameChar['unit']))
            if 'cardAttr' in card:
                attr = card['cardAttr']
                
        bonus = 25 if eventId >= 36 else 20
        
        cards = []
        
        for unit, group in units:
            cards += self.getCardByUnit(unit, group, eventId)
        
        cards = set(cards).symmetric_difference(set(self.getCardByAttr(attr, eventId)))
        cards = [Card(card, eventId, bonus, self) for card in cards]
        
        cards.sort(key=lambda x: self.RARITYWORTH[x.rarity], reverse=True)
                
        return cards
    
    def getFocusEventCards(self, eventId) -> list[Card]:
        if eventId == 38:
            return []
        eventDeckBonus = []
        if eventId < 36:
            return eventDeckBonus
        
        for card in self.getEventCards(eventId):
            if int(card['bonusRate']) > 0:
                eventDeckBonus.append(card['cardId'])
                
        bonus = 70 if eventId >= 36 else 50
                
        eventDeckBonus = [Card(card, eventId, bonus, self) for card in eventDeckBonus]
                
        return eventDeckBonus
    
    def getCardByUnit(self, unitId, group, eventId = None):
        if eventId is None:
            stopper = float("inf")
        else:
            stopper = max(self.getEventCards(eventId), key=lambda x: x["cardId"])["cardId"]
            
        cards = []
        if group:
            for card in self.cardData:
                if card["id"] > stopper:
                    break
                if card["characterId"] == unitId:
                    if card['supportUnit'] == group:
                        cards.append(card['id']) 
                        
        else:
            for card in self.cardData:
                if card["id"] > stopper:
                    break
                if card["characterId"] == unitId:
                    cards.append(card['id']) 
    
        return cards
    
    def getCardByAttr(self, attr, eventId = None):
        if eventId is None:
            stopper = float("inf")
        else:
            stopper = max(self.getEventCards(eventId), key=lambda x: x["cardId"])["cardId"]
        cards = []
        for card in self.cardData:
            if card["id"] > stopper:
                break
            if card["attr"] == attr:
                cards.append(card['id'])
        return cards
    
    def getUnitId(self, unit):
        for unitData in self.unitsData:
            if unitData["unit"] == unit:
                return unitData["seq"]
        return None
    
    def getData(self, eventId, tier):
        filepath = f"Events-EN/Event{eventId:02d}/{tier}.csv"
        df = pd.read_csv(filepath)
            
        xData = np.array(df["Event Time"])
        points = np.array(df["Score"])
        
        return xData, points
    
    def getPercentage(self, timestamp, length):
        """
        Converts timestamp to percentage of event completion
        
        timestamp: days since event start
        length: event length in unix timestamp
        """
        return timestamp / (length / 1000 / 60 / 60 / 24)