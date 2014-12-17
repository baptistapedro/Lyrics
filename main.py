import os, sys, thread
import pygame, pygame.mixer
import requests
from bs4 import BeautifulSoup
from twisted.internet.task import LoopingCall
from twisted.internet import stdio
from twisted.protocols import basic
from twisted.internet import reactor



def _audio_player(f):
    """ Use pygame to simulate an audio player """
    os.environ['SDL_VIDEODRIVER'] = "dummy"
    pygame.init()
    pygame.mixer.music.load(f)
    pygame.mixer.music.set_volume(0.9)
    pygame.mixer.music.play(0) # 0 = 1, just plays one time

    for event in pygame.event.get():
        if event.type == KEYDOWN:
            if event.key == K_ESCAPE:
                running = False


class Song(object):
    """Receive the artist,track names and google it"""
    def __init__(self, artist, track):
        self.artist = artist
        self.track = track

    def search_url(self):
        return "http://www.google.com/search?q=%(artist)s+%(track)s+rapgenius" % {
          'artist': self.artist.replace(' ', '+'),
          'track': self.name.replace(' ', '+')



def lyrics_page():
    """ Find first rapgenius google result
    and returns the URL lyrics page
    """
    song = Song('Jay-z', 'Empire State of Mind')
    goog = requests.get(song.search_url())
    soup = BeautifulSoup(goog.text)

    for node in soup.findAll('h3', {'class': 'r'})[0]:
            return node['href'].split('=')[1].split('&')[0]



def lyrics():
    """ Returns full lyrics of the song """
    lp = requests.get(lyrics_page())
    tree = BeautifulSoup(lp.text)
    return list([p.text.lower().split() for p in tree.findAll('div', {'class': 'lyrics'})][0])



FPS = 5.0
words = set()

class RawInput(basic.LineReceiver):
    """ Replaces raw_input() because it is a blocking call """
    from os import linesep as delimiter
    prompt = '-> '

    def connectionMade(self):
        self.transport.write(self.prompt)

    def lineReceived(self, w):
        w = w.strip()
        if w:
            words.update([w])

        self.transport.write(self.prompt)

def pygame_tick():
    #know when the song ends.
    if not pygame.mixer.music.get_busy():
        reactor.stop()


def main():
    _audio_player("jayz.mp3")
    tick = LoopingCall(pygame_tick)
    tick.start(1.0 / FPS)

    #create a protocol to read what is typed on the terminal
    stdio.StandardIO(RawInput())
    #reads all events
    reactor.run()
    match = words.intersection(lyrics())

    print '%s words you\'ve entered are on the lyrics of the song!' % len(match)

if __name__ == '__main__':
    main()
