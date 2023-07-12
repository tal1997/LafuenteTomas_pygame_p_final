import random, pygame, time, pygame.mixer
from os import listdir
from os.path import isfile, join

pygame.init()


pygame.display.set_caption("Frog Atack")

        
#Defino constantes para el juego
ANCHO_VENTANA = 900
ALTO_VENTANA = 700
FPS = 60
VELOCIDAD_JUGADOR = 5
ROJO = (255,0,0)
NEGRO = (0,0,0)
BLANCO = (255,255,255)


ventana = pygame.display.set_mode((ANCHO_VENTANA , ALTO_VENTANA))

class Reloj:
    def __init__(self, player):
        self.tiempo_inicial = 60 * FPS
        self.tiempo_actual = self.tiempo_inicial
        self.font = pygame.font.SysFont(None, 30)
        self.player = player
        

    def actualizar(self):
        if self.tiempo_actual > 0:
            self.tiempo_actual -= 1

    def mostrar_tiempo(self, ventana):
        minutos = int(self.tiempo_actual // (FPS * 60))
        segundos = int((self.tiempo_actual // FPS) % 60)
        tiempo_restante = f"Tiempo: {minutos:02d}:{segundos:02d}"
        texto_reloj = self.font.render(tiempo_restante, True, NEGRO)
        ventana.blit(texto_reloj, (10, 40))
        
        if minutos == 0 and segundos == 0:
            self.tiempo_actual = self.tiempo_inicial
            self.player.vidas -=1
            self.player.rect.x = 50
            self.player.rect.y = 50
        
        
class Corazon(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.imagen = pygame.image.load("recursos/heart.png").convert_alpha()
        self.rect = self.imagen.get_rect()
        self.rect.x = x
        self.rect.y = y
    
    def draw(self, ventana):
        ventana.blit(self.imagen, self.rect)

class Score:
    def __init__(self):
        
        self.puntaje = 0
        self.font = pygame.font.SysFont(None, 40)
        
        
    def incrementar_score(self):
        self.puntaje += 50
        
    def draw(self, ventana):
        score_text = ("Puntuacion: {0}".format(self.puntaje))
        texto_surface = self.font.render(score_text, True, NEGRO)
        texto_rect = texto_surface.get_rect(center = (ANCHO_VENTANA // 2, 15))
        ventana.blit(texto_surface, texto_rect)


def girar_sprite(sprites):
    return [pygame.transform.flip(sprite, True, False) for sprite in sprites]

def cargar_hojas_sprite(directorio_1, directorio_2, ancho, alto, direccion = False):
    #Funcion que se encargara de cargar, girar presentar correctamente la hoja con los sprites deseados
    
    path = join("recursos", directorio_1,directorio_2)
    imagenes = [f for f in listdir(path) if isfile(join(path, f))]
    
    all_sprites = {}
    
    for imagen in imagenes:
        hoja_sprite = pygame.image.load(join(path, imagen)).convert_alpha()

        sprites = []
        for i in range(hoja_sprite.get_width() // ancho):
            superficie = pygame.Surface((ancho, alto,), pygame.SRCALPHA, 32)
            rect = pygame.Rect(i * ancho, 0, ancho, alto)
            superficie.blit(hoja_sprite, (0, 0), rect)
            sprites.append(pygame.transform.scale2x(superficie))
            
        if direccion:
            all_sprites[imagen.replace(".png", "") + "_derecha"] = sprites
            all_sprites[imagen.replace(".png", "") + "_izquierda"] = girar_sprite(sprites)
        else:
            all_sprites[imagen.replace(".png", "")] = sprites
            
    return all_sprites

def get_bloques(size):
    #Obtengo la superficie de los bloques, le cargo 96 y 9 a las coordenadas porque es el bloque que quiero usar de la plantilla
    path = join("recursos/Terrain/Terrain.png")
    imagen = pygame.image.load(path).convert_alpha()
    superficie = pygame.Surface((size,size),pygame.SRCALPHA, 32)
    rect = pygame.Rect(96, 0, size, size)
    superficie.blit(imagen, (0, 0), rect)
    return pygame.transform.scale2x(superficie)


class Objetos(pygame.sprite.Sprite):
    def __init__(self, x, y, ancho, alto, nombre = None):
        super().__init__()
        self.rect = pygame.Rect(x, y, ancho, alto)
        self.imagen = pygame.Surface((ancho,alto), pygame.SRCALPHA)
        self.ancho = ancho
        self.alto = alto
        self.nombre = nombre
        
    def draw(self, ventana):
        ventana.blit(self.imagen, (self.rect.x, self.rect.y))


class Enemigo(pygame.sprite.Sprite):
    GRAVEDAD = 1
    SPRITES = cargar_hojas_sprite("MainCharacters", "NinjaFrog", 32, 32, True)
    DELAY_ANIMACION = 5

    def __init__(self, x, y, ancho, alto):
        super().__init__()
        self.rect = pygame.Rect(x, y, ancho, alto)
        self.x_vel = 0
        self.y_vel = 0
        self.mask = None
        self.direccion = "izquierda"
        self.conteo_animacion = 0
        self.contador_tiempo_caida = 0
        self.hit = False
        self.contador_hit = 0
        
        self.contador_colisiones = 0
        self.ultima_actualizacion = time.time()
        self.contador_colision_proyectil = 0
       
        
    def obtener_coordenadas(self):
        return self.rect.x, self.rect.y  
             
    def make_hit(self):
        self.hit = True
        self.contador_hit = 0
        
    #Defino las funciones de movimiento
    def movimiento(self, direc_x, direc_y):
        self.rect.x += direc_x
        self.rect.y += direc_y

    def movimiento_izquierda(self, vel):
        if self.rect.x > 0:
            self.x_vel = -vel
        else:
            self.x_vel = 0
        if self.direccion != "izquierda":
            self.direccion = "izquierda"
            self.conteo_animacion = 0
        
    def movimiento_derecha(self, vel):
        if self.rect.x <= 900-64:
            self.x_vel = vel
        else:
            self.x_vel = 0         
        if self.direccion != "derecha":
            self.direccion = "derecha"
            self.conteo_animacion = 0 
    
    def contador_direccion(self, vel):
        if self.direccion == "izquierda":
            if self.rect.x > 0:
                self.x_vel = -vel
            else:
                self.x_vel = 0
                self.direccion = "derecha"
        else:
            if self.rect.x <= 900-64:
                self.x_vel = vel
            else:
                self.x_vel = 0
            
    def contador_impactos(self):
        if self.contador_colision_proyectil < 10:
            self.contador_colision_proyectil += 1
        else:    
            return True
    
    def loop(self, FPS, bloques, player):
        #Con esta funcion utilizo las funciones que necesito que se repitan una y otra vez cuando las precise
        self.y_vel += min(1, (self.contador_tiempo_caida / FPS) * self.GRAVEDAD)
        self.movimiento(self.x_vel, self.y_vel)

        #Verificar colisiones con bloques
        for bloque in bloques:
            if self.rect.colliderect(bloque.rect):
                #Colision desde arriba
                if self.y_vel > 0:
                    self.rect.bottom = bloque.rect.top
                    self.aterrizado()
                #Colision desde abajo
                elif self.y_vel < 0:
                    self.rect.top = bloque.rect.bottom
                    self.golpe_cabeza()

        #Verificar colision con el jugador
        if self.rect.colliderect(player.rect):
            #Colision con el jugador desde arriba, enemigo cae sobre el player
            if self.y_vel > 0:
                self.rect.bottom = player.rect.top
                self.aterrizado()
            else:
                #Colision con el jugador desde cualquier otro lado
                self.make_hit()
                player.make_hit()
        
        if self.hit:
            self.contador_hit += 1
            
        if self.contador_hit > FPS * 2:
            self.hit = False 
            self.contador_hit = 0   

        self.contador_tiempo_caida += 1  
        self.actualizar_sprite()
    
        
        #Movimiento aleatorio hacia la izquierda y derecha cada 1 segundos
        tiempo_actual = time.time()
        
        if tiempo_actual - self.ultima_actualizacion >= 1.5:
            self.direccion = random.choice(["izquierda", "derecha"])
            self.ultima_actualizacion = tiempo_actual
            
            #Cambiar la direccion aleatoriamente
        if self.direccion == "izquierda":
            self.movimiento_izquierda(VELOCIDAD_JUGADOR)
        
        elif self.direccion == "derecha":
            self.movimiento_derecha(VELOCIDAD_JUGADOR)
             
    def aterrizado(self):
        #Funcion para reinicar la gravedad al caer y que quede apoyado sobre el piso
        self.contador_tiempo_caida = 0
        self.y_vel = 0
        self.contador_salto = 0
        
    def golpe_cabeza(self):
        #Funcion para chocar contra objetos arriba y rebotar hacia abajo de nuevo
        self.contador = 0
        self.y_vel *= -1

    def actualizar_sprite(self):
        #Funcion para actualizar al sprite correspondiente
        hoja_sprite = "idle"
        if self.hit:
            hoja_sprite = "hit"
        elif self.y_vel > self.GRAVEDAD * 2:
            hoja_sprite = "fall" 
        elif self.x_vel != 0:
            hoja_sprite = "run"
    
        nombre_hoja_sprites = hoja_sprite + "_" + self.direccion
        sprites = self.SPRITES[nombre_hoja_sprites]
        indice_sprite = (self.conteo_animacion // self.DELAY_ANIMACION) % len(sprites)
        self.sprite = sprites[indice_sprite]
        self.conteo_animacion += 1
        self.actualizar()

    def actualizar(self):
        #Con esta funcion me aseguro que los objetos colisionen exactamente al pixel exacto, no al cuadrado de sprite general
        self.rect = self.sprite.get_rect(topleft=(self.rect.x, self.rect.y))
        self.mask = pygame.mask.from_surface(self.sprite)
                  
    def draw(self, ventana):
        #Funcion que llamare para pasarle al draw de la ventana y se dibuje el enemigo en pantalla
        ventana.blit(self.sprite, (self.rect.x , self.rect.y))
    
    
class Player(pygame.sprite.Sprite):
    #Creo la clase jugador, le cargo dimensiones, sprite, coordenadas, movimiento y el resto de atributos correspondientes
    GRAVEDAD = 1
    SPRITES = cargar_hojas_sprite("MainCharacters","MaskDude", 32, 32, True)
    DELAY_ANIMACION = 5
    
    
    def __init__(self, x, y, ancho, alto, grupo_enemigos):
        super().__init__()
        self.rect = pygame.Rect(x, y, ancho, alto)
        self.x_vel = 0
        self.y_vel = 0
        self.mask = None
        self.direccion = "izquierda"
        self.conteo_animacion = 0
        self.contador_tiempo_caida = 0
        self.contador_salto = 0
        self.hit = False
        self.contador_hit = 0
        self.vida = 100
        self.vidas = 3
        self.contador_colisiones = 0
        self.grupo_enemigos = grupo_enemigos
        self.proyectiles = []
        
       
    def obtener_coordenadas(self):
        return self.rect.x, self.rect.y
    
    def colision_enemigo(self, enemigos):
        #Funcion para detectar la colision del player con el enemigo y le resta 33 de vida al enemigo(tocando 4 veces con el enemigo pierde una vida)
        for enemigo in enemigos:
            if pygame.sprite.collide_rect(self, enemigo):
                self.vida -= 33
                if self.vida <= 0:
                    self.rect.x = 50
                    self.rect.y = 50
          
    def colision_fuego(self, fuego):
        #Funcion para generar las colisiones necesarias entre el jugador y trampas de fuego
        if self.rect.colliderect(fuego.rect):
            self.contador_colisiones +=0.05
            self.vida -= self.contador_colisiones
        if self.vida <= 0:
            self.vidas -= 1
            self.vida = 100
            self.rect.x = 50
            self.rect.y = 50
                        
    def mostrar_vidas(self, ventana):
        #Funcion para mostrar las vidas del jugador en pantalla
        font = pygame.font.SysFont(None, 30)
        texto = font.render(str(self.vidas), True, NEGRO)
        ventana.blit(texto,(20, 12))     
          
    def salto(self):
        #Aplico el salto utilizando la gravedad en negativo ya que tengo una gravedad cosntante que me tira hacia abajo en el juego,
        #entonces de esa forma hago que se eleve el jugador y luego lo vuelvo a hacer positivo para volver a bajar
        self.y_vel = -self.GRAVEDAD * 8
        self.conteo_animacion = 0
        self.contador_salto += 1
        if self.contador_salto == 1:
            self.contador_tiempo_caida = 0
            
    def make_hit(self):
        #Esta funcion chekea sirve como bandera de la colision del jugador con los objetos
        self.hit = True
        self.contador_hit = 0
        
    #Defino las funciones de movimiento
    def movimiento(self, direc_x, direc_y):
        self.rect.x += direc_x
        self.rect.y += direc_y

    def movimiento_izquierda(self, vel):
        #Funcion de movimientos a la izquierda
        if self.rect.x > 0:
            self.x_vel = -vel
        else:
            self.x_vel = 0
        if self.direccion != "izquierda":
            self.direccion = "izquierda"
            self.conteo_animacion = 0
        
    def movimiento_derecha(self, vel):
        #Funcion de movimientos a la derecha
        if self.rect.x <= 900-64:
            self.x_vel = vel
        else:
            self.x_vel = 0         
        if self.direccion != "derecha":
            self.direccion = "derecha"
            self.conteo_animacion = 0
    
    def lanzar_proyectil(self):
        #Funcion para lanzar los proyectiles
        if self.direccion == "derecha":
            proyectil = Proyectil((self.rect.x + 64), (self.rect.y + 32), 1)
            self.proyectiles.append(proyectil)
        else:
            proyectil = Proyectil((self.rect.x + 64), (self.rect.y + 32), -1)
            self.proyectiles.append(proyectil)
            
    def loop(self, FPS):
        #Con esta funcion utilizo las funciones que necesito que se repitan una y otra vez cuando las precise
        self.y_vel += min(1, (self.contador_tiempo_caida / FPS) * self.GRAVEDAD)
        self.movimiento(self.x_vel, self.y_vel)
        
        if self.hit:
            self.contador_hit += 1
            
        if self.contador_hit > FPS * 2:
            self.hit = False 
            self.contador_hit = 0   

        self.contador_tiempo_caida += 1  
        self.actualizar_sprite()
              
        for proyectil in self.proyectiles:
            proyectil.update()
            #proyectil.colision_enemigo()
        
    def aterrizado(self):
        #Funcion para reinicar la gravedad al caer y que quede apoyado sobre el piso
        self.contador_tiempo_caida = 0
        self.y_vel = 0
        self.contador_salto = 0
        
    def golpe_cabeza(self):
        #Funcion para chocar contra objetos arriba y rebotar hacia abajo de nuevo
        self.contador = 0
        self.y_vel *= -1

    def actualizar_sprite(self):
        #Funcion para poder actualizar los sprites del jugador,, le da nombre a la hoja de sprites para poder actualizarla correctamente
        hoja_sprite = "idle"
        if self.hit:
            hoja_sprite = "hit"
        if self.y_vel < 0:
            if self.contador_salto == 1:
                hoja_sprite = "jump"
            elif self.contador_salto == 2:
                hoja_sprite = "double_jump"
        
        elif self.y_vel > self.GRAVEDAD * 2:
            hoja_sprite = "fall" 
        
        elif self.x_vel != 0:
            hoja_sprite = "run"
    
        nombre_hoja_sprites = hoja_sprite + "_" + self.direccion
        sprites = self.SPRITES[nombre_hoja_sprites]
        indice_sprite = (self.conteo_animacion // self.DELAY_ANIMACION) % len(sprites)
        self.sprite = sprites[indice_sprite]
        self.conteo_animacion += 1
        self.actualizar()

    def actualizar(self):
        #Con esta funcion me aseguro que los objetos colisionen exactamente al pixel exacto, no al cuadrado de sprite general
        self.rect = self.sprite.get_rect(topleft=(self.rect.x, self.rect.y))
        self.mask = pygame.mask.from_surface(self.sprite)
        
    def draw(self, ventana):
        #Funcion para pasarle al draw de la ventana principal, es donde se va iniciar el player
        ventana.blit(self.sprite, (self.rect.x , self.rect.y))
    
    
class Proyectil(pygame.sprite.Sprite):
    #Clase encargada de todo lo que refiere a proyectiles y sus propiedades
    def __init__(self, x, y, direccion, radio = 3, color = ROJO):
        super().__init__()
        self.rect = pygame.Rect(x, y, radio * 2, radio * 2)
        self.x = x
        self.y = y
        self.radio = radio
        self.color = color
        self.direccion = direccion
        self.velocidad = 5
        self.enemigos = pygame.sprite.Group()
        self.contador_colision_enemigo = 0


    def get_rect(self):
        #Metodo para conseguir las coordenadas de mi proyectil y generar un rectangulo ficticio para usar en la colision con el enemigo
        return pygame.Rect(self.x - self.radio, self.y - self.radio, self.radio * 2, self.radio * 2)
    
    def actualizar(self):
        #Funcion para actualizar la posicion del proyectil
        self.x += self.velocidad * self.direccion
        self.rect.x = self.x
    
    def colision_enemigo(self):
        #Verificar colisiones con enemigos
        enemigos_alcanzados = pygame.sprite.spritecollide(self, self.enemigos, True)    
        
    def draw(self, ventana):
        #Funcion encargada de pasarle el draw principal de pantalla los datos necesarios para dibujar cada proyectil en pantalla
        pygame.draw.circle(ventana, self.color, self.rect.center , self.radio)

        
class Bloques(Objetos):
    #Clase encargada de los bloques de piso y demas
    #Clase para crear bloques que hereda de objetos
    def __init__(self, x, y, size):
        super().__init__(x, y, size, size)
        bloque = get_bloques(size)
        self.imagen.blit(bloque, (0,0))
        self.mask = pygame.mask.from_surface(self.imagen)


class Fuego(Objetos):
    #Clase encargada de las propiedades y caracteristicas de las trampas de fuego
    DELAY_ANIMACION = 3
    
    def __init__(self, x, y, ancho, alto):
        super().__init__(x, y, ancho, alto, "fuego")
        self.fire = cargar_hojas_sprite("Traps", "Fire", ancho, alto)
        self.imagen = self.fire["off"][0]
        self.mask = pygame.mask.from_surface(self.imagen)
        self.contador_animacion = 0
        self.nombre_animacion = "off"
    
    def on(self):
        #Funcion para determinar que la llama este en posicion "on"
        self.nombre_animacion = "on"
    
    def off(self):
        #Funcion para determinar que la llama este en posicion "off"
        self.nombre_animacion = "off"
    
    def loop(self):
        #Funcion para generar todos los metodos que necesite chekear una y otra vez en forma de loop
        sprites = self.fire[self.nombre_animacion]
        indice_sprite = (self.contador_animacion // self.DELAY_ANIMACION) % len(sprites)
        self.imagen = sprites[indice_sprite]
        self.contador_animacion += 1
        
        self.rect = self.imagen.get_rect(topleft=(self.rect.x, self.rect.y))
        self.mask = pygame.mask.from_surface(self.imagen)
        
        if self.contador_animacion // self.DELAY_ANIMACION > len(sprites):
            self.contador_animacion = 0
       
    
def get_fondo(): 
    #Obtengo el fondo de pantalla, le pinto los mosaicos que sean necesarios para x,y
    #utilizando bucles for para saber que canatidad de mosaicos necesito y los agrego a una lista que va a pintar la pantalla
    
    imagen = pygame.image.load("recursos/Background/Blue.png")
    _, _, ancho , alto = imagen.get_rect()
    mosaicos = [] 

    for i in range (ANCHO_VENTANA // ancho +1):
        for j in range(ALTO_VENTANA // alto +1):
            pos = [i * ancho , j * alto ]
            mosaicos.append(pos)
    return mosaicos , imagen


def fondo_game_over(ventana):
    #Fondo de pantalla que aparecera al perder todas las vidas
    imagen = pygame.image.load("recursos/GAMEOVER.png").convert()
    imagen = pygame.transform.scale(imagen, (ANCHO_VENTANA, ALTO_VENTANA))
    ventana.blit(imagen, (0,0))
    pygame.display.update()   

def fondo_inicio_juego(ventana):
    #Fondo de pantalla que aparecerá al inicio del juego antes de que comience a correr
    imagen = pygame.image.load("recursos/Ready.png").convert()
    imagen = pygame.transform.scale(imagen, (ANCHO_VENTANA, ALTO_VENTANA))
    ventana.blit(imagen, (0, 0))
    pygame.display.update()
    pygame.time.wait(1500)  # Congelar la pantalla por 1.5 segundos antes de comenzar el juego


def draw(ventana, fondo, bg_imagen, player, objetos, reloj, corazones, enemigos, score, perdedor):
    #Funcion donde se dibujara el fondo en pantalla, jugador, enemigos, etc.
    #Sera la encargada de dibujar todo practicamente
    
    for mosaico in fondo:
        ventana.blit(bg_imagen , mosaico)

    for obj in objetos:
        obj.draw(ventana)
    
    corazones.draw(ventana)
    
    reloj.mostrar_tiempo(ventana)
    
    player.draw(ventana)
    
    for enemigo in enemigos:
        enemigo.draw(ventana)
        
    for proyectil in player.proyectiles:
        proyectil.draw(ventana)
        
    score.draw(ventana)
    
    if perdedor is not None:
        ventana.blit(perdedor, (0,0))
    
    
    
    pygame.display.update()

def colision_vertical(player, objetos, direc_y):
    #Funcion para detectar colisiones verticales
    objetos_colisionados = []
    for obj in objetos:
        if pygame.sprite.collide_mask(player, obj):
            if direc_y > 0:
                player.rect.bottom = obj.rect.top   #Si choco contra el obj desde arriba, caigo sobre el objeto, el jugador queda apoyado sobre el mismo
                player.aterrizado()
            elif direc_y < 0:
                player.rect.top = obj.rect.bottom  #De esta forma, al chocar desde abajo con un objeto reboto con el mismo
                player.golpe_cabeza()
            
            objetos_colisionados.append(obj)
    
    return objetos_colisionados

def colision(player, objetos, direc_x):
    #Funcion para detectar cualquier tipo de colision
    player.movimiento(direc_x, 0)
    player.actualizar()
    objetos_colisionados = None
    for obj in objetos:
        if pygame.sprite.collide_mask(player,obj):
            objetos_colisionados = obj
            break
            
    player.movimiento(-direc_x, 0)
    player.actualizar()

    return objetos_colisionados   
            
def control_movimiento(player, objetos):
    '''
    Con esta funion voy a verificar las teclas presionadas y por cada una realizara una accion diferente
    '''
    keys = pygame.key.get_pressed()
    player.x_vel = 0
    colision_izquierda = colision(player,objetos, -VELOCIDAD_JUGADOR)
    colision_derecha = colision(player,objetos, VELOCIDAD_JUGADOR)
    
    if keys[pygame.K_LEFT] and not colision_izquierda:
        player.movimiento_izquierda(VELOCIDAD_JUGADOR)
    if keys[pygame.K_RIGHT] and not colision_derecha:
        player.movimiento_derecha(VELOCIDAD_JUGADOR)

    control_colision_vertical = colision_vertical(player, objetos, player.y_vel)
    chekeo = [colision_izquierda, colision_derecha, *control_colision_vertical]
    for obj in chekeo:
        if obj and obj.nombre == "fuego":
            player.make_hit()
    
def main(ventana):
    #Esta es la funcion principal donde se desarrolla el juego
    
    #Pinto el fondo con la funcion get_fondo, le paso el atributo y el archivo de color a pintar
    fondo , bg_imagen = get_fondo()
    
    #Mostrar fondo de inicio del juego
    fondo_inicio_juego(ventana)    
            
    #Musica fondo
    sonido = pygame.mixer.Sound("recursos/pista.wav")
    sonido.play(-1)
    
    #Game over
    game_over = False
    perdedor = None
    
    #tamaño de los bloques
    bloque_size = 96

    #Corazon para representar la vida en el juego, le paso (x,y)
    corazones = Corazon(9,5)
    
    #Score
    score = Score()
            
    #Generacion de enemigos, los agrego a una lista de enemigos
    enemigos = [Enemigo(500, 50,  50,50),
                Enemigo(800, 400, 50,50),
                Enemigo(700, 200, 50,50),
                Enemigo(200, 500, 50,50)]    
    
    #Generacion del player, verifico colision de los proyectiles creados con los enemigos
    player = Player(100, 100, 50, 50, enemigos)
    for enemigo in enemigos:
        if player.proyectiles:
            player.proyectiles[0].enemigos.add(enemigo)
    
    #Reloj
    reloj = Reloj(player)
       
    #Generacion de trampas de fuego
    fire = Fuego(100, ALTO_VENTANA - bloque_size - 64, 16, 32)
    fire_2 = Fuego(375, ALTO_VENTANA - bloque_size - 64, 16, 32)
    fire_3 = Fuego(570, ALTO_VENTANA - bloque_size * 3 - 64, 16, 32)
    fire_4 = Fuego(189, ALTO_VENTANA - bloque_size * 4 - 64, 16, 32)
    fire_5 = Fuego(672, ALTO_VENTANA - bloque_size * 6 - 64, 16, 32)
    fire.on(), fire_2.on(), fire_3.on(), fire_4.on(), fire_5.on()
        
    
    
    #Generacion de piso y plataformas
    piso = [Bloques(i * bloque_size, ALTO_VENTANA - bloque_size, bloque_size) for i in range(-ANCHO_VENTANA // bloque_size, ANCHO_VENTANA * 2 // bloque_size)]
    objetos = [*piso, Bloques(0, ALTO_VENTANA - bloque_size * 1, bloque_size),
                Bloques(bloque_size * 5, ALTO_VENTANA - bloque_size * 3, bloque_size),
                Bloques(bloque_size * 6, ALTO_VENTANA - bloque_size * 3, bloque_size),
                Bloques(bloque_size * 7, ALTO_VENTANA - bloque_size * 3, bloque_size),
                Bloques(bloque_size * 8, ALTO_VENTANA - bloque_size * 3, bloque_size),
                Bloques(bloque_size * 9, ALTO_VENTANA - bloque_size * 3, bloque_size),
                
                Bloques(bloque_size * 0, ALTO_VENTANA - bloque_size * 4, bloque_size),
                Bloques(bloque_size * 1, ALTO_VENTANA - bloque_size * 4, bloque_size),
                Bloques(bloque_size * 2, ALTO_VENTANA - bloque_size * 4, bloque_size),
                
                Bloques(bloque_size * 5, ALTO_VENTANA - bloque_size * 6, bloque_size),
                Bloques(bloque_size * 6, ALTO_VENTANA - bloque_size * 6, bloque_size),
                Bloques(bloque_size * 7, ALTO_VENTANA - bloque_size * 6, bloque_size), 
                fire, fire_2, fire_3, fire_4, fire_5]
    
    
    #COMIENZO DEL JUEGO, BUCLE WHILE PRINCIPAL
    run = True
    while run == True:
             
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sonido.stop()
                run = False
                pygame.quit()
         
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and player.contador_salto < 2:
                    player.salto()
                elif event.key == pygame.K_c:
                    player.lanzar_proyectil()

            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos_x,mouse_pos_y = pygame.mouse.get_pos()
                print(mouse_pos_x, mouse_pos_y)
            
        reloj.actualizar()
        reloj.mostrar_tiempo(ventana)
        
        #Score
        score.draw(ventana)
        
        #enemigo
        for enemigo in enemigos:
            enemigo.loop(FPS, objetos, player)
            enemigo.draw(ventana)
            
        #player
        player.loop(FPS)
        player.update()
        player.colision_enemigo(enemigos)
        player.colision_fuego(fire) or player.colision_fuego(fire_2) or player.colision_fuego(fire_3) or player.colision_fuego(fire_4) or player.colision_fuego(fire_5)
        
        #Proyectil y colision con enemigo
        for proyectil in player.proyectiles:
            proyectil.draw(ventana)
            proyectil.actualizar()
            proyectil_rect = proyectil.get_rect()
            for enemigo in enemigos:
                if proyectil_rect.colliderect(enemigo.rect):
                    enemigo.contador_impactos()
                    if proyectil in player.proyectiles:
                        player.proyectiles.remove(proyectil)
                    else:
                        pass
                    if enemigo.contador_impactos() == True: 
                        enemigos.remove(enemigo)
                        score.incrementar_score()
                    
        vida = player.vidas
        if vida == 0:
            game_over = True
            perdedor = fondo_game_over(ventana)
        
        while game_over:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    sonido.stop()
                    pygame.quit()
        
        fire.loop(), fire_2.loop(), fire_3.loop(), fire_4.loop(), fire_5.loop()
        corazones.draw(ventana)
        
        control_movimiento(player, objetos)
           
        draw(ventana, fondo , bg_imagen, player, objetos, reloj, corazones, enemigos, score, perdedor)
        
        player.mostrar_vidas(ventana)
        
        pygame.display.update()
        
if __name__ == "__main__":
    main(ventana)