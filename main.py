# Kolikkojahti pelissä ohjataan nuolinäppäimillä robottia ja kerätään pelialueelta kolikkoja
# liikkumalla niiden päälle. Kolikkoja ilmestyy satunnaisiin paikkoihin ja ne ovat esillä vain hetken aikaa.
# 3 kolikon välein pelialueelle ilmestyy ovi josta kulkemalla pääsee seuraavalle tasolle.
# Seuraavilla tasoilla peli vaikeutuu mörköjen takia joihin ei saa osua. Kolikkojen esillä oloaika myös pienenee.

import pygame
from random import randint

class Peli:
  def __init__(self):
    pygame.init()
    self.__nayton_leveys = 640
    self.__nayton_korkeus = 480
    self.__naytto = pygame.display.set_mode((self.__nayton_leveys, self.__nayton_korkeus))
    pygame.display.set_caption("Kolikkojahti")
    self.__robon_kuva = pygame.image.load("robo.png")
    self.__oven_kuva = pygame.image.load("ovi.png")
    self.__haamu = pygame.image.load("hirvio.png")
    self.__kolikko = pygame.image.load("kolikko.png")
    self.__fontti = pygame.font.SysFont("Arial", 24)
    self.__pieni_fontti = pygame.font.SysFont("Arial", 16)

    self.__liiku_oikealle = False
    self.__liiku_vasemmalle = False
    self.__liiku_ylos = False
    self.__liiku_alas = False
    self.__peli_kaynnissa = False

    self.__uusi_peli()
    self.__kello = pygame.time.Clock()
    self.__main_loop()
  
  def __uusi_peli(self):
    self.__kolikot = [] #kolikkojen (x,y) tuplet
    self.__haamut = [] #haamujen (x,y) tuplet
    self.__haamujen_suunnat = [] #Taulukkoon tallennetaan jokaisen haamun liikkeen suunta
    self.__robo = [self.__robon_kuva, (0, 0)]
    self.__ovi = [self.__oven_kuva, (self.__nayton_leveys/2 + self.__oven_kuva.get_width()/2, self.__nayton_korkeus/2 + self.__oven_kuva.get_height()/2)]
    self.__pisteet = 0
    self.__taso = 1
    self.__sekkari = 0
    self.__kolikon_viive = 250
    self.__ovi_esilla = False
    self.__gameover = False

  def __kasittele_tapahtumat(self):
    for tapahtuma in pygame.event.get():
      if tapahtuma.type == pygame.QUIT:
        exit()
      
      if tapahtuma.type == pygame.KEYDOWN:
        if tapahtuma.key == pygame.K_LEFT:
          self.__liiku_vasemmalle = True
        if tapahtuma.key == pygame.K_RIGHT:
          self.__liiku_oikealle = True
        if tapahtuma.key == pygame.K_UP:
          self.__liiku_ylos = True
        if tapahtuma.key == pygame.K_DOWN:
          self.__liiku_alas = True
        if tapahtuma.key == pygame.K_p and self.__gameover == False:
          if self.__peli_kaynnissa:
            self.__peli_kaynnissa = False
          else:
            self.__peli_kaynnissa = True

      if tapahtuma.type == pygame.KEYUP:
        if tapahtuma.key == pygame.K_LEFT:
          self.__liiku_vasemmalle = False
        if tapahtuma.key == pygame.K_RIGHT:
          self.__liiku_oikealle = False
        if tapahtuma.key == pygame.K_UP:
          self.__liiku_ylos = False
        if tapahtuma.key == pygame.K_DOWN:
          self.__liiku_alas = False
        if tapahtuma.key == pygame.K_F2:
          self.__uusi_peli()
          self.__peli_kaynnissa = True
        if tapahtuma.key == pygame.K_ESCAPE:
          exit()

  # Tällä ohjataan robotin liikettä. Funktio palauttaa tuplen jossa on uudet x- ja y-koordinaatit.
  # Samalla tarkistetaan, että ei liikuta alueen ulkopuolelle.
  def __liikuta(self, kuva: pygame.Surface , koordinaatit: tuple, nopeus: int) -> tuple:
    leveys = kuva.get_width()
    korkeus = kuva.get_height()
    x = koordinaatit[0]
    y = koordinaatit[1] 
    if self.__gameover != True:
      if self.__liiku_oikealle and x + leveys <= self.__nayton_leveys:
        x += nopeus
      if self.__liiku_vasemmalle and x >= 0:
        x -= nopeus
      if self.__liiku_alas and y + korkeus <= self.__nayton_korkeus:
        y += nopeus
      if self.__liiku_ylos and y >= 0:
        y -= nopeus

    return (x,y)

  # Tämä tarkistaa osuuko kaksi piirrettävää objektia toistensa päälle
  def __osuvatko_yhteen(self, obj1: tuple, obj2: tuple) -> bool:
    # obj1 ja obj2 ovat kahden alkion tupleja. Ensimmäinen alkio sisältää piirrettävän kuvan,
    # jotta sen koko saadaan selville. Toinen alki sisältää tuplen jossa on kyseisen hahmon x- ja y-koordinaatit
    kuva1 = obj1[0]
    x1 = obj1[1][0]
    y1 = obj1[1][1]
    kuva2 = obj2[0]
    x2 = obj2[1][0]
    y2 = obj2[1][1]
    k1_leveys = kuva1.get_width()
    k1_korkeus = kuva1.get_height()
    k2_leveys = kuva2.get_width()
    k2_korkeus = kuva2.get_height()

    if x1 >= x2 and x1 <= x2 + k2_leveys and y1 >= y2 and y1 <= y2 + k2_korkeus:
      return True
    if x1 + k1_leveys >= x2 and x1 + k1_leveys <= x2 + k2_leveys and y1 >= y2 and y1 <= y2 + k2_korkeus:
      return True
    if y1 + k1_korkeus >= y2 and y1 + k1_korkeus <= y2 + k2_korkeus and x1 >= x2 and x1 <= x2 + k2_leveys:
      return True
    if y1 + k1_korkeus >= y2 and y1 + k1_korkeus <= y2 + k2_korkeus and x1 + k1_leveys >= x2 and x1 + k1_leveys <= x2 + k2_leveys:
      return True
    
    return False

  def __luo_kolikko(self):
    if self.__sekkari % 120 == 0 and self.__gameover != True:
      x = randint(0, self.__nayton_leveys - self.__kolikko.get_width())
      y = randint(0, self.__nayton_korkeus - self.__kolikko.get_height())
      self.__kolikot.append((x, y))

  def __luo_haamu(self):
    x = randint(0, self.__nayton_leveys - self.__kolikko.get_width())
    y = randint(0, self.__nayton_korkeus - self.__kolikko.get_height())
    self.__haamut.append((x, y))
    self.__haamujen_suunnat.append([randint(0,1),randint(0,1)])
  
  def __liikuta_haamuja(self):
    # 
    if self.__gameover != True:
      for i in range(len(self.__haamut)):
        x = self.__haamut[i][0]
        y = self.__haamut[i][1]

        # Haamujen suunnat ovat kahden alkin taulukossa. Ensimmäinen alkio on x-liike, toinen y-liike
        # 0 arvo tarkoittaa, että liike on joko ylös tai vasemmalle, 1 liikuttaa joko alas tai oikealle.
        # Mikäli haamu osuu rajoihin, niin sen kulkusuunta muutetaan.
        if self.__haamujen_suunnat[i][0] == 1:
          if x + self.__haamu.get_width() <= self.__nayton_leveys:
            x += 1
          else:
            x -= 1
            self.__haamujen_suunnat[i][0] = 0
        if self.__haamujen_suunnat[i][0] == 0: 
            if x >= 0:
              x -= 1
            else:
              x += 1
              self.__haamujen_suunnat[i][0] = 1
        if self.__haamujen_suunnat[i][1] == 1: 
          if y + self.__haamu.get_height() <= self.__nayton_korkeus:
            y += 1
          else:
            y -= 1
            self.__haamujen_suunnat[i][1] = 0
        if self.__haamujen_suunnat[i][1] == 0:
          if y >= 0:
            y -= 1
          else:
            y += 1
            self.__haamujen_suunnat[i][1] = 1

        self.__haamut[i] = (x, y)

  # Poistaa kolikon itsestään
  def __poista_kolikko(self):
    if self.__sekkari % self.__kolikon_viive == 0 and len(self.__kolikot) > 0:
      self.__kolikot.pop(0)

  # Robotti poistaa kolikon täällä
  def __poimi_kolikko(self):
    poistettava = -1
    for i in range(len(self.__kolikot)):
      kolikko = (self.__kolikko, self.__kolikot[i])
      if self.__osuvatko_yhteen(self.__robo, kolikko):
        poistettava = i

    if poistettava >= 0:
      self.__kolikot.pop(poistettava)
      self.__pisteet += 1

    if self.__pisteet % 3 == 0 and self.__pisteet > 0:
      self.__ovi_esilla = True
  
  def __osuuko_haamu(self):
    for h in self.__haamut:
      haamu = (self.__haamu, h)
      if self.__osuvatko_yhteen(self.__robo, haamu):
        self.__gameover = True
        self.__peli_kaynnissa = False

  def __seuraavalle_tasolle(self):
    self.__kolikon_viive -= 30
    self.__ovi_esilla = False
    self.__taso += 1
    self.__pisteet += 1
    self.__kolikot.clear()
    self.__luo_haamu()

  def __piirra_naytto(self):
    self.__naytto.fill((100,100,100))

    self.__pisteet_teksti = self.__fontti.render(f"Pisteet: {self.__pisteet}", True, (255, 0, 0))
    self.__taso_teksti = self.__fontti.render(f"Taso: {self.__taso}", True, (255, 0, 0))
    self.__ohjeteksti = self.__pieni_fontti.render(f"Kerää robotilla kolikoita. Varo haamuja. Ovesta aukeaa uusi taso.", True, (255, 0, 0))
    self.__gameover_teksti = self.__fontti.render(f"GAME OVER", True, (255, 0, 0))
    self.__painikkeet_teksti = self.__fontti.render(f"F2 = Uusi peli     P = Pause     Esc = poistu", True, (255, 0, 0))
    self.__liikkuminen_teksti = self.__fontti.render(f"Liikkuminen nuolinäppäimillä", True, (255, 0, 0))
    self.__naytto.blit(self.__pisteet_teksti, (620 - self.__pisteet_teksti.get_width(), 20))
    self.__naytto.blit(self.__taso_teksti, (620 - self.__taso_teksti.get_width(), 50))

    self.__naytto.blit(self.__robo[0], (self.__robo[1]))

    for i in range(len(self.__haamut)):
      self.__naytto.blit(self.__haamu, self.__haamut[i])

    for i in range(len(self.__kolikot)):
      self.__naytto.blit(self.__kolikko, self.__kolikot[i])
    
    if self.__ovi_esilla:
      self.__naytto.blit(self.__ovi[0], (self.__ovi[1]))
      if self.__osuvatko_yhteen(self.__robo, self.__ovi) and self.__ovi_esilla:
        self.__seuraavalle_tasolle()

    if self.__peli_kaynnissa == False:
      self.__naytto.blit(self.__painikkeet_teksti, (self.__nayton_leveys/2 - self.__painikkeet_teksti.get_width()/2, self.__nayton_korkeus - 130))
      self.__naytto.blit(self.__liikkuminen_teksti, (self.__nayton_leveys/2 - self.__liikkuminen_teksti.get_width()/2, self.__nayton_korkeus - 100))
      self.__naytto.blit(self.__ohjeteksti, (self.__nayton_leveys/2 - self.__ohjeteksti.get_width()/2, self.__nayton_korkeus - 50))

    if self.__gameover:
      self.__naytto.blit(self.__gameover_teksti, (620/2 - self.__taso_teksti.get_width()/2, 320/2))

    pygame.display.flip()

  def __main_loop(self):
    while True:
      self.__kasittele_tapahtumat()
      if self.__peli_kaynnissa:
        self.__robo[1] = self.__liikuta(self.__robo[0], self.__robo[1], 2)
        self.__luo_kolikko()
        self.__poista_kolikko()
        self.__poimi_kolikko()
        self.__liikuta_haamuja()
        self.__osuuko_haamu()
      self.__piirra_naytto()

      self.__kello.tick(60)
      self.__sekkari += 1

if __name__ == "__main__":
  Peli()