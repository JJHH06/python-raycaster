#Proyecto 3 raycaster, basado en el código de Carlos Alonso por haberlo hecho durante la clase
#José Hurtarte 19707
import pygame
from math import cos, pi, sin, tan, atan2

RAY_AMOUNT = 100

SPRITE_BACKGROUND = (152, 0, 136, 255)

wallcolors = {
    '1': pygame.Color('red'),
    '2': pygame.Color('green'),
    '3': pygame.Color('blue'),
    '4': pygame.Color('yellow'),
    '5': pygame.Color('purple')
    }

wallTextures = {
    '1': pygame.image.load('STONE3.png'),
    '2': pygame.image.load('STONGARG.png'),
    '3': pygame.image.load('BIGDOOR7.png'),
    '4': pygame.image.load('MARBFAC2.png'),
    '5': pygame.image.load('MARBFACE.png')
    }

enemies = [{"x" : 100,
            "y" : 200,
            "sprite" : pygame.image.load('sprite1.png')},

           {"x" : 350,
            "y" : 150,
            "sprite" : pygame.image.load('sprite2.png')},

            {"x" : 300,
             "y" : 400,
             "sprite" : pygame.image.load('sprite3.png')}

    ]

class Background(pygame.sprite.Sprite):
    def __init__(self, image_file, location, size):
        pygame.sprite.Sprite.__init__(self)  #call Sprite initializer
        self.image = pygame.image.load(image_file)
        self.image = pygame.transform.scale(self.image, size)
        self.rect = self.image.get_rect()
        self.rect.left, self.rect.top = location

class Raycaster(object):
    def __init__(self, screen):
        super().__init__()
        self.screen = screen


        _,_, self.width, self.height = screen.get_rect()
        #La info del mapa como una lista
        self.map = []
        # Para determinar la cantidad de pixeles que ocuparia en el mapa en un lado 
        self.zbuffer = [float('inf') for z in range(int(self.width / 2))]
        #Tamaño del bloque
        self.blocksize =50
        self.wallheight = 50

        self.maxdistance = 300

        #Cuanto me muevo
        self.stepSize = 5
        self.turnSize = 5

        self.player = {
            'x': 100,
            'y': 100,
            'fov': 60,
            'angle': 0
            
        }

    #Para cargar el mapa con el .txt
    def load_map(self, filename):
        with open(filename) as file:
            for line in file.readlines():
                self.map.append( list(line.rstrip()) )

    def drawBlock(self, x, y, id):
        tex = wallTextures[id]
        tex = pygame.transform.scale(tex, (self.blocksize, self.blocksize) )
        rect = tex.get_rect()
        rect = rect.move((x,y))
        self.screen.blit(tex, rect)


    def drawIcons(self):
        if self.player['x'] < self.width / 2:
            rect = (self.player['x'] - 2, self.player['y'] - 2, 5,5)
            self.screen.fill(pygame.Color('black'), rect )

        for enemy in enemies:
            rect = (enemy['x'] - 2, enemy['y'] - 2, 5,5)
            self.screen.fill(pygame.Color('red'), rect )

    def drawSprite(self, obj, size):
        # Pitagoras
        spriteDist = ((self.player['x'] - obj['x']) ** 2 + (self.player['y'] - obj['y']) ** 2) ** 0.5

        # Angulo
        spriteAngle = atan2(obj['y'] - self.player['y'], obj['x'] - self.player['x']) * 180 / pi

        #Tamaño del sprite
        aspectRatio = obj['sprite'].get_width() / obj['sprite'].get_height()
        spriteHeight = (self.height / spriteDist) * size
        spriteWidth = spriteHeight * aspectRatio

        # Buscar el punto inicial para dibujar el sprite
        angleDif = (spriteAngle - self.player['angle']) % 360
        angleDif = (angleDif - 360) if angleDif > 180 else angleDif
        startX = angleDif * (self.width / 2) / self.player['fov'] 
        startX += (self.width * 3/4) - (spriteWidth  / 2)
        startY = (self.height /  2) - (spriteHeight / 2)
        startX = int(startX)
        startY = int(startY)

        for x in range(startX, startX + int(spriteWidth)):
            if (self.width / 2 < x < self.width) and self.zbuffer[x - int(self.width / 2)] >= spriteDist:
                for y in range(startY, startY + int(spriteHeight)):
                    tx = int((x - startX) * obj['sprite'].get_width() / spriteWidth )
                    ty = int((y - startY) * obj['sprite'].get_height() / spriteHeight )
                    texColor = obj['sprite'].get_at((tx, ty))
                    if texColor != SPRITE_BACKGROUND and texColor[3] > 128:
                        self.screen.set_at((x,y), texColor)
                        self.zbuffer[x - int(self.width / 2)] = spriteDist

    def castRay(self, angle):
        rads = angle*pi/180
        # paso a paso y distancia por distancia
        dist = 0
        stepSize = 1
        stepX = stepSize * cos(rads)
        stepY = stepSize * sin(rads)

        playerPos = (self.player['x'],self.player['y'] )

        x = playerPos[0]
        y = playerPos[1]

        while 1:
            dist += stepSize      

            x += stepX
            y += stepY

            i = int(x/self.blocksize)
            j = int(y/self.blocksize)

            #Que retorne la distancia con la que hizo contacto y el identificador de la pared
            if j < len(self.map):
                if i < len(self.map[j]):
                    if self.map[j][i] != ' ':
                        hitX = x - i*self.blocksize
                        hitY = y - j*self.blocksize
                        hit = 0

                        if 1 < hitX < self.blocksize-1:
                            if hitY < 1:
                                hit = self.blocksize - hitX
                            elif hitY >= self.blocksize-1:
                                hit = hitX
                        elif 1 < hitY < self.blocksize-1:
                            if hitX < 1:
                                hit = hitY
                            elif hitX >= self.blocksize-1:
                                hit = self.blocksize - hitY

                        tx = hit / self.blocksize

                        pygame.draw.line(self.screen,pygame.Color('white'), playerPos, (x,y))
                        return dist, self.map[j][i], tx

                        

            
            


    def render(self):

        halfWidth = int(self.width/2)
        halfHeight = int(self.height/2)

        # Para las coordenadas de la pantalla, se empieza desde esquina superior izquierda
        for x in range(0, halfWidth, self.blocksize):
            #Para que vaya saltandose el size del bloque
            for y in range(0, self.height, self.blocksize):
                #Vamos revisando, dependiendo del paso que vamos

                i = int(x/self.blocksize)
                j = int(y/self.blocksize)

                #Para accesar al valor del mapa en esa posicion
                if j < len(self.map):
                    if i < len(self.map[j]):
                        if self.map[j][i] != ' ':
                            self.drawBlock(x,y, self.map[j][i])

        self.drawIcons()

        #Generacio de rayos
        for column in range(RAY_AMOUNT):
            angle = self.player['angle'] + (-(self.player['fov']/2)) + (self.player['fov']*column/RAY_AMOUNT)
            dist, id, tx = self.castRay(angle)

            rayWidth = int(( 1 / RAY_AMOUNT) * halfWidth)

            for i in range(rayWidth):
                self.zbuffer[column * rayWidth + i] = dist

            startX = halfWidth + int(( (column / RAY_AMOUNT) * halfWidth))

            # perceivedHeight = screenHeight / (distance * cos( rayAngle - viewAngle)) * wallHeight
            h = self.height / (dist * cos( (angle - self.player["angle"]) * pi / 180)) * self.wallheight
            startY = int(halfHeight - h/2)
            endY = int(halfHeight + h/2)

            color_k = (1 - min(1, dist / self.maxdistance)) * 255

            tex = wallTextures[id]
            tex = pygame.transform.scale(tex, (tex.get_width() * rayWidth, int(h)))

            #Descomentar esta linea para sombrear 
            #tex.fill((color_k,color_k,color_k), special_flags=pygame.BLEND_MULT)
            tx = int(tx * tex.get_width())
            self.screen.blit(tex, (startX, startY), (tx,0,rayWidth,tex.get_height()))
            
            


        for enemy in enemies:
            self.drawSprite(enemy, 50)

        
        # Columna divisora
        for i in range(self.height):
            self.screen.set_at( (halfWidth, i), pygame.Color('black'))
            self.screen.set_at( (halfWidth+1, i), pygame.Color('black'))
            self.screen.set_at( (halfWidth-1, i), pygame.Color('black'))


            


width = 1000
height = 500

# Crear ventana de pygame
pygame.init()

screen = pygame.display.set_mode((width, height), pygame.DOUBLEBUF | pygame.HWACCEL) #Flags, configuraciones para que sea óptimo
#Double buffering significa que pygame usa un segundo espacio de memoria, mientras el primer frame buffer se dibuja en pantalla
# En si para que no se vea la reenderizacion en tiempo real

#Tambien puede ser pygame.FULLSCREEN
# o tambien pygame.OPENGL para usar la tarjeta de video

screen.set_alpha(None) #No toma transparencia para mas rapido

rCaster = Raycaster(screen)
rCaster.load_map("map.txt")
#para medir fps
clock = pygame.time.Clock()
#Para cambiar el formato a una fuente
font = pygame.font.SysFont("Arial", 25)
buttonFont = pygame.font.SysFont("Arial", 32)

titleFont = pygame.font.SysFont("verdana", 40)


#Fondo
BackGround = Background('background.jpg', [0,0],(width, height))
pauseBackground = Background('doom-pause.jpg', [0,0],(width, height))

def updateFPS():

    #Es como usar time.deltaTime(), solo que hace todos los calculos para los fps
    fps = str(int(clock.get_fps()))
    #De una vez regresa el texto
    fps = font.render(fps, 1, pygame.Color("white"))

    return fps



isRunning = 1
isMenu = 1
isPause = 0
first = 1


b1Pos=(400,250)

b2Pos=(400,350)

menuSelect = [True, False]
pauseSelect = [1, 0]


flipSelection = lambda l: [not n for n in l]

while isRunning:
    #Se revisan todos los eventos

    
    for ev in pygame.event.get():

        #Se revisa si hay un evento de tipo quit
        #Se activa si apachamos x arriba o si le hacemos un binding a otro boton

        if ev.type == pygame.QUIT:
            isRunning = 0

        #Si la tecla esta en hold
        elif ev.type == pygame.KEYDOWN:

            if ev.key == pygame.K_ESCAPE:
                # como tipo quit
                isRunning = 0
            
            if ev.key == pygame.K_p:
                if not isMenu:
                    isPause = not isPause

            if ev.key == pygame.K_UP or ev.key == pygame.K_DOWN:
                if isMenu:
                    menuSelect = flipSelection(menuSelect)
                if (not isMenu) and (isPause):
                    pauseSelect = flipSelection(pauseSelect)

            if ev.key == pygame.K_RETURN:
                if isMenu:
                    if menuSelect[0]:
                        isMenu = 0
                        first = 1
                    elif menuSelect[1]:
                        isRunning = 0
                if isPause:
                    if pauseSelect[0]:
                        if isPause:
                            screen.fill(pygame.Color("gray"))#Fondo gris
                            screen.fill(pygame.Color("saddlebrown"), (int(width / 2), 0,  int(width / 2), int(height / 2)))

            # Piso
                            screen.fill(pygame.Color("dimgray"), (int(width / 2), int(height / 2),  int(width / 2), int(height / 2)))
                            rCaster.render()
                        isPause = 0
                    elif pauseSelect[1]:
                        isMenu = 1
                        isPause = 0
                        rCaster.player = {'x': 100,'y': 175,'fov': 60,'angle': 180}


    if not isMenu:
        
        if isPause:
            screen.fill([255, 255, 255])
            screen.blit(pauseBackground.image, BackGround.rect)
            screen.fill((100,100,100), (b1Pos[0],b1Pos[1],200,70))
            screen.fill((100,100,100), (b2Pos[0],b2Pos[1],200,70))

            if pauseSelect[0]:
                screen.fill(pygame.Color("red"), (b1Pos[0] +5,b1Pos[1] + 5,200 -5*2,70 -5*2))

            else:
                screen.fill((245, 173, 66), (b1Pos[0] +5,b1Pos[1] + 5,200 -5*2,70 -5*2))


            if pauseSelect[1]:
                screen.fill(pygame.Color("red"), (b2Pos[0] +5,b2Pos[1] + 5,200 -5*2,70 -5*2))
            else:
                screen.fill((245, 173, 66), (b2Pos[0] +5,b2Pos[1] + 5,200 -5*2,70 -5*2))

            screen.blit(titleFont.render("Pausa", 1, pygame.Color("black")), (418,165))
            screen.blit(titleFont.render("Pausa", 1, pygame.Color("white")), (415,165))
            screen.blit(buttonFont.render("Reanudar", 1, pygame.Color("black")), (440,265))
            screen.blit(buttonFont.render("Menu", 1, pygame.Color("black")), (455,365))


        else:
            
            keys = pygame.key.get_pressed()  #checking pressed keys
            
            if first:
                screen.fill(pygame.Color("gray"))#Fondo gris
                screen.fill(pygame.Color("saddlebrown"), (int(width / 2), 0,  int(width / 2), int(height / 2)))

            # Piso
                screen.fill(pygame.Color("dimgray"), (int(width / 2), int(height / 2),  int(width / 2), int(height / 2)))
                rCaster.render()
                first = False

            if keys[pygame.K_w] or keys[pygame.K_a] or keys[pygame.K_d] or keys[pygame.K_e]or keys[pygame.K_q]or keys[pygame.K_s] :
                newX = rCaster.player['x']
                newY = rCaster.player['y']
                forward = rCaster.player['angle']*pi/180
                right = ((rCaster.player['angle']+90)*pi/180)
                
                        
                if keys[pygame.K_w]:
                    newX +=  cos(forward)*rCaster.stepSize
                    newY +=  sin(forward)*rCaster.stepSize

                elif keys[pygame.K_s]:
                    newX -=  cos(forward)*rCaster.stepSize
                    newY -=  sin(forward)*rCaster.stepSize
                            
                if keys[pygame.K_a]:
                    newX -=  cos(right)*rCaster.stepSize
                    newY -=  sin(right)*rCaster.stepSize

                elif keys[pygame.K_d]:
                            
                    newX +=  cos(right)*rCaster.stepSize
                    newY +=  sin(right)*rCaster.stepSize

                if keys[pygame.K_q]:
                    rCaster.player['angle'] -= rCaster.turnSize

                elif keys[pygame.K_e]:
                    rCaster.player['angle'] += rCaster.turnSize

                i = int(newX/rCaster.blocksize)
                j = int(newY/rCaster.blocksize)

                if rCaster.map[j][i] == ' ':
                    rCaster.player['x'] = newX
                    rCaster.player['y'] = newY
                screen.fill(pygame.Color("gray"))#Fondo gris


                screen.fill(pygame.Color("saddlebrown"), (int(width / 2), 0,  int(width / 2), int(height / 2)))

            # Piso
                screen.fill(pygame.Color("dimgray"), (int(width / 2), int(height / 2),  int(width / 2), int(height / 2)))
                rCaster.render()
            # Para dar el fps
            screen.fill(pygame.Color("black"), (0,0,30,30))#Cuadrito en la esquina de color negro

            #Dibujar objetos, texto o imagenes, en este caso los fps
            screen.blit(updateFPS(), (0,0))

    else:
        
        screen.fill([255, 255, 255])
        screen.blit(BackGround.image, BackGround.rect)
        screen.fill((100,100,100), (b1Pos[0],b1Pos[1],200,70))
        screen.fill((100,100,100), (b2Pos[0],b2Pos[1],200,70))

        if menuSelect[0]:
            screen.fill(pygame.Color("red"), (b1Pos[0] +5,b1Pos[1] + 5,200 -5*2,70 -5*2))

        else:
            screen.fill((245, 173, 66), (b1Pos[0] +5,b1Pos[1] + 5,200 -5*2,70 -5*2))


        if menuSelect[1]:
            screen.fill(pygame.Color("red"), (b2Pos[0] +5,b2Pos[1] + 5,200 -5*2,70 -5*2))
        else:
            screen.fill((245, 173, 66), (b2Pos[0] +5,b2Pos[1] + 5,200 -5*2,70 -5*2))

        screen.blit(titleFont.render("El raycaster en python", 1, pygame.Color("black")), (258,165))
        screen.blit(titleFont.render("El raycaster en python", 1, pygame.Color("white")), (255,165))
        screen.blit(buttonFont.render("Jugar", 1, pygame.Color("black")), (455,265))
        screen.blit(buttonFont.render("Salir", 1, pygame.Color("black")), (455,365))
    
    # Valor maximo de los fps
    clock.tick(60)
    

    pygame.display.flip()




# Cierra la pantalla
pygame.quit()