from IRCMessage import IRCMessage
from IRCResponse import IRCResponse, ResponseType
from Function import Function
import WebUtils

import re

from bs4 import BeautifulSoup

class Instantiate(Function):
    Help = 'mtg(f) <card name> - fetches details of the Magic: The Gathering card you specify from gatherer.wizards.com. mtgf includes the flavour text, if it has any'

    def GetResponse(self, message):
        if message.Type != 'PRIVMSG':
            return

        match = re.search('^mtgf?$', message.Command, re.IGNORECASE)
        if not match:
            return

        searchTerm = 'http://gatherer.wizards.com/pages/search/default.aspx?name='
        for param in message.ParameterList:
            searchTerm += '+[%s]' % param

        webPage = WebUtils.FetchURL(searchTerm)

        soup = BeautifulSoup(webPage.Page)

        name = soup.find('div', {'id' : 'ctl00_ctl00_ctl00_MainContent_SubContent_SubContent_nameRow'})
        if name is None:
            return IRCResponse(ResponseType.Say, 'Multiple or no cards found: ' + searchTerm, message.ReplyTo)

        name = name.find('div', 'value').text.strip()
        types = ' | T: ' + soup.find('div', {'id' : 'ctl00_ctl00_ctl00_MainContent_SubContent_SubContent_typeRow'}).find('div', 'value').text.strip()
        rarity = ' | R: ' + soup.find('div', {'id' : 'ctl00_ctl00_ctl00_MainContent_SubContent_SubContent_rarityRow'}).find('div', 'value').text.strip()

        manaCost = soup.find('div', {'id' : 'ctl00_ctl00_ctl00_MainContent_SubContent_SubContent_manaRow'})
        if manaCost is not None:
            manaCost = unicode(manaCost.find('div', 'value'))
            manaCost = ' | MC: ' + re.sub('<img.+?name=([^&"]+).+?>', "\\1", manaCost)
            manaCost = re.sub('<[^>]+?>', '', manaCost)
            manaCost = manaCost.replace('\n', '')
        else:
            manaCost = ''

        convCost = soup.find('div', {'id' : 'ctl00_ctl00_ctl00_MainContent_SubContent_SubContent_cmcRow'})
        if convCost is not None:
            convCost = ' | CMC: ' + convCost.find('div', 'value').text.strip()
        else:
            convCost = ''

        cardText = soup.find('div', {'id' : 'ctl00_ctl00_ctl00_MainContent_SubContent_SubContent_textRow'})
        if cardText is not None:
            cardTexts = cardText.find_all('div', 'cardtextbox')
            texts = []
            for text in cardTexts:
                text = re.sub('<img.+?name=([^&"]+).+?>', '\\1', unicode(text))
                text = re.sub('<[^>]+?>', '', text)
                texts.append(text)
            cardText = ' | CT: ' + ' > '.join(texts)
        else:
            cardText = ''

        flavText = soup.find('div', {'id' : 'ctl00_ctl00_ctl00_MainContent_SubContent_SubContent_FlavorText'})
        if flavText is not None:
            flavTexts = flavText.find_all('div', 'cardtextbox')
            texts = []
            for text in flavTexts:
                texts.append(unicode(text.text))
            flavText = ' | FT: ' + ' > '.join(texts)
        else:
            flavText = ''

        powTough = soup.find('div', {'id' : 'ctl00_ctl00_ctl00_MainContent_SubContent_SubContent_ptRow'})
        if powTough is not None:
            powTough = ' | P/T: ' + powTough.find('div', 'value').text.strip().replace(' ', '')
        else:
            powTough = ''

        reply = name + manaCost + convCost + types + cardText + flavText + powTough + rarity

        return IRCResponse(ResponseType.Say, reply, message.ReplyTo)